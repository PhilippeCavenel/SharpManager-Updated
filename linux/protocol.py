"""Serial protocol compatible with SharpManager's Arduino driver 1.3.

Modified 6 October 2026 from the archived macOS V5.2 driver for Linux:
English diagnostics and serial-port permission guidance. On-wire commands,
64-byte transfers, control-line handling and timing remain compatible.
SharpManager: Copyright 2024 Wayne Venables / Codaris Computing.
See LICENSE-SharpManager.txt and ../NOTICE.

One worker owns all reads. This prevents idle printing and a cassette transfer
from consuming one another's replies, even after repeated operations.
"""

import queue
import threading
import time

SOH, STX, ETX, ACK, DLE, NAK, SYN, CAN = 1, 2, 3, 6, 16, 21, 22, 24


class ProtocolError(Exception):
    pass


def swap_header(data):
    """The TAP header stores reversed nibbles; the driver expects them swapped."""
    result = bytearray(data)
    if len(result) >= 8:
        for i in range(1, 8):
            result[i] = ((result[i] & 15) << 4) | (result[i] >> 4)
        if result[0] in (0x71, 0x73) and len(result) >= 18:
            for i in range(10, 18):
                result[i] = ((result[i] & 15) << 4) | (result[i] >> 4)
    return bytes(result)


class Driver:
    def __init__(self, emit):
        self.emit = emit
        self.serial = None
        self.stream_mode = False
        self.commands = queue.Queue()
        self.alive = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def submit(self, action, *args):
        self.commands.put((action, args))

    def _read(self, timeout):
        self.serial.timeout = timeout
        value = self.serial.read(1)
        if not value:
            raise ProtocolError(f"Timed out after {timeout:g} s")
        return value[0]

    def _write(self, data):
        self.serial.write(bytes(data))
        # On the macOS FTDI driver, the successful standalone probe explicitly
        # flushed each SYN. Do the same for every complete protocol write.
        self.serial.flush()

    def _expect(self, expected, timeout):
        value = self._read(timeout)
        if value != expected:
            raise ProtocolError(f"Reply 0x{value:02X}; expected 0x{expected:02X}")

    def _response(self, timeout=5):
        value = self._read(timeout)
        if value == ACK:
            return
        if value == NAK:
            raise ProtocolError(f"Arduino error {self._read(1)}")
        raise ProtocolError(f"Unexpected reply 0x{value:02X}")

    def _sync(self, attempts=11):
        for attempt in range(attempts):
            # Match the raw pyserial probe that succeeded on the user's FT232R:
            # clear stale bytes, send SYN, read a short burst rather than one
            # byte, and leave a small interval before the next try.
            self.serial.reset_input_buffer()
            self._write((SYN,))
            self.serial.timeout = 1
            reply = self.serial.read(8)
            self.emit("log", f"SYN {attempt + 1}: {reply.hex(' ') or '(no reply)'}")
            if SYN in reply:
                self.emit("log", f"Synchronized on attempt {attempt + 1}")
                return
            time.sleep(.3)
        raise ProtocolError("Cannot synchronize with the Pro Mini")

    def _reset_driver(self):
        """Pulse FTDI RTS, wired to the Pro Mini DTR/reset input.

        A previous interrupted CLOAD can leave the firmware inside Tape::Load,
        where it cannot answer a new SYN. Reset is only attempted when a new
        connection has already failed to synchronize.
        """
        self.emit("log", "No reply: resetting the Pro Mini through RTS/DTR")
        self.serial.rts = True
        time.sleep(.12)
        self.serial.rts = False
        time.sleep(2.5)  # let the bootloader finish
        self.serial.reset_input_buffer()

    def _connect(self, port):
        import serial
        self._disconnect()
        # Supply the control-line state at open; RTS goes via DTR on the board.
        connection = serial.Serial(port=None, baudrate=115200, timeout=1)
        connection.dtr = False
        connection.rts = False
        connection.port = port
        try:
            connection.open()
        except serial.SerialException as exc:
            if "permission denied" in str(exc).lower():
                raise ProtocolError(
                    f"Permission denied for {port}. See README.md: add your user "
                    "to the port's group (usually dialout), then log out and back in."
                ) from exc
            raise
        self.serial = connection
        try:
            # The FTDI RTS line is connected to Pro Mini DTR. Opening the USB
            # device can reset the ATmega; let its bootloader finish first.
            time.sleep(2)
            try:
                self._sync(attempts=3)
            except ProtocolError:
                self._reset_driver()
                self._sync(attempts=20)
            self._write((SOH, 1))
            self._expect(SOH, 2.5)
            major, minor, size = (self._read(1) for _ in range(3))
            if (major, minor) != (1, 3) or size < 16:
                raise ProtocolError(f"Driver {major}.{minor}, buffer {size}: expected 1.3")
            self._expect(STX, 1)
            version = bytearray()
            while True:
                value = self._read(1)
                if value == ETX:
                    break
                if len(version) > 512:
                    raise ProtocolError("Firmware identifier is too long")
                version.append(value)
            label = version.decode('latin-1', errors='replace')
            # This French identifier belongs to the firmware protocol and must
            # remain unchanged, even though the Linux UI uses English.
            self.stream_mode = "flux continu V5" in label
            self.emit("log", f"Connected: {label}")
        except Exception:
            self._disconnect()
            raise

    def _disconnect(self):
        if self.serial is not None:
            try:
                self._write((CAN,))
            except Exception:
                pass
            self.serial.close()
            self.serial = None
            self.stream_mode = False
            self.emit("log", "Disconnected")

    def _ping(self):
        self._sync()
        self._write((SOH, 2))
        self._response(2.5)
        self.emit("log", "Ping: OK")

    def _send(self, tape, block_pause=0):
        if not 10 <= len(tape) <= (32767 if self.stream_mode else 65535):
            raise ProtocolError("Invalid cassette size")
        self._sync()
        length = len(tape)
        self._write((SOH, 6, length & 255, length >> 8, 10))
        try:
            self._response(20 if self.stream_mode else 5)
        except ProtocolError as exc:
            raise ProtocolError(f"CLOAD command, before data: {exc}") from exc
        payload = swap_header(tape)
        block_count = (length + 63) // 64
        if self.stream_mode:
            self.emit("log", f"Sending {length} bytes in {block_count} blocks of 64")
        for offset in range(0, length, 64):
            if offset and block_pause and not self.stream_mode:
                # Controlled experiment: Arduino has ACKed the previous block
                # after generating its waveform. Delay only the next block.
                time.sleep(block_pause)
            self._write(payload[offset:offset + 64])
            block_number = offset // 64 + 1
            try:
                # The first block includes the 2 s cassette leader. Later
                # ACKs can also be delayed when the circular buffer is full.
                self._response(20 if self.stream_mode else (8 if offset == 0 else 5))
            except ProtocolError as exc:
                raise ProtocolError(
                    f"block {block_number}/{block_count}, bytes "
                    f"{offset + 1}–{min(length, offset + 64)} : {exc}"
                ) from exc
            if self.stream_mode and (block_number % 8 == 0 or block_number == block_count):
                self.emit("log", f"Arduino: {min(length, offset + 64)}/{length} bytes accepted")
        if self.stream_mode:
            # ACK acknowledges buffer intake. ETX follows the last waveform
            # bit, so the UI does not claim completion while XIN is active.
            try:
                self._expect(ETX, 10 + length * .040)
            except ProtocolError as exc:
                raise ProtocolError(f"End of cassette signal after {length} bytes: {exc}") from exc
            self.emit("log", f"Cassette signal ended: {length} bytes; continuous stream")
        else:
            self.emit("log", f"Send complete: {length} bytes; block pause {int(block_pause * 1000)} ms")

    def _receive(self):
        self._sync()
        self._write((SOH, 7))
        self._response()
        self.emit("log", "Waiting for CSAVE…")
        start = self._read(120)
        if start == NAK:
            raise ProtocolError(f"Arduino error {self._read(1)}")
        if start != STX:
            raise ProtocolError(f"Received 0x{start:02X} instead of STX")
        output = bytearray()
        while True:
            value = self._read(5)
            if value == DLE:
                value = self._read(1)
            elif value == ETX:
                break
            elif value == NAK:
                raise ProtocolError(f"Arduino error {self._read(1)}")
            elif value == CAN:
                raise ProtocolError("Receive cancelled")
            output.append(value)
            if len(output) > 65535:
                raise ProtocolError("Cassette is too long")
        tape = swap_header(output)
        self.emit("received", tape)
        self.emit("log", f"CSAVE received: {len(tape)} bytes")

    def _idle(self):
        self.serial.timeout = .08
        raw = self.serial.read(1)
        if not raw:
            return
        value = raw[0]
        if value == SYN:
            self._write((SYN,))
        elif value == SOH:
            command = self._read(1)
            if command == 2:
                self._write((ACK,))
            elif command == 3:
                self._read(1)  # device select
            elif command == 4:
                character = self._read(1)
                self.emit("print", "\n" if character == 13 else chr(character))
            elif command == 5:
                self.emit("log", f"Data: {self._read(1):02X}")
            else:
                self._write((NAK, 3))
                self.emit("log", f"Unsupported Arduino command: {command}")
        else:
            self._write((NAK, 3))

    def _run(self):
        while self.alive:
            try:
                action, args = self.commands.get(timeout=.08 if self.serial else .5)
            except queue.Empty:
                if self.serial:
                    try:
                        self._idle()
                    except Exception as exc:
                        self.emit("error", str(exc))
                        self._disconnect()
                continue
            if action == "quit":
                self.alive = False
                self._disconnect()
                break
            try:
                if action == "connect":
                    self._connect(*args)
                elif action == "disconnect":
                    self._disconnect()
                else:
                    if not self.serial:
                        raise ProtocolError("Connect the Pro Mini first")
                    {"ping": self._ping, "send": self._send,
                     "receive": self._receive}[action](*args)
                self.emit("done", action)
            except Exception as exc:
                self.emit("error", f"{action} : {exc}")
                if action == "send":
                    # A partial tape command can leave the Arduino busy.
                    # Force a new connection, which can reset it through RTS.
                    self._disconnect()
                self.emit("done", action)
