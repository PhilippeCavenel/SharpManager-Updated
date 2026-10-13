"""Serial protocol compatible with SharpManager's Arduino driver 1.3.

One worker owns all reads. This prevents idle printing and a cassette transfer
from consuming one another's replies, even after repeated operations.
"""

from pathlib import Path
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
        self._printer_raw = bytearray()  # raw bytes for LPRINT diagnosis
        self.alive = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def submit(self, action, *args):
        self.commands.put((action, args))

    def _read(self, timeout):
        self.serial.timeout = timeout
        value = self.serial.read(1)
        if not value:
            raise ProtocolError(f"Délai d'attente dépassé ({timeout:g} s)")
        return value[0]

    def _write(self, data):
        self.serial.write(bytes(data))
        # On the macOS FTDI driver, the successful standalone probe explicitly
        # flushed each SYN. Do the same for every complete protocol write.
        self.serial.flush()

    def _expect(self, expected, timeout):
        value = self._read(timeout)
        if value != expected:
            raise ProtocolError(f"Réponse 0x{value:02X}, attendu 0x{expected:02X}")

    def _response(self, timeout=5):
        value = self._read(timeout)
        if value == ACK:
            return
        if value == NAK:
            raise ProtocolError(f"Erreur Arduino {self._read(1)}")
        raise ProtocolError(f"Réponse inattendue 0x{value:02X}")

    def _sync(self, attempts=11):
        for attempt in range(attempts):
            # Match the raw pyserial probe that succeeded on the user's FT232R:
            # clear stale bytes, send SYN, read a short burst rather than one
            # byte, and leave a small interval before the next try.
            self.serial.reset_input_buffer()
            self._write((SYN,))
            self.serial.timeout = 1
            reply = self.serial.read(8)
            self.emit("log", f"SYN {attempt + 1} : {reply.hex(' ') or '(aucune réponse)'}")
            if SYN in reply:
                self.emit("log", f"Synchronisation obtenue à la tentative {attempt + 1}")
                return
            time.sleep(.3)
        raise ProtocolError("Synchronisation impossible avec la Pro Mini")

    def _reset_driver(self):
        """Pulse FTDI RTS, wired to the Pro Mini DTR/reset input.

        A previous interrupted CLOAD can leave the firmware inside Tape::Load,
        where it cannot answer a new SYN. Reset is only attempted when a new
        connection has already failed to synchronize.
        """
        self.emit("log", "Aucune réponse : réinitialisation de la Pro Mini par RTS/DTR")
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
        connection.open()
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
                raise ProtocolError(f"Driver {major}.{minor}, tampon {size} : attendu 1.3")
            self._expect(STX, 1)
            version = bytearray()
            while True:
                value = self._read(1)
                if value == ETX:
                    break
                if len(version) > 512:
                    raise ProtocolError("Identifiant de firmware trop long")
                version.append(value)
            label = version.decode('latin-1', errors='replace')
            self.stream_mode = "flux continu V5" in label
            self.emit("log", f"Connecté : {label}")
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
            self.emit("log", "Déconnecté")

    def _ping(self):
        self._sync()
        self._write((SOH, 2))
        self._response(2.5)
        self.emit("log", "Ping : OK")

    def _send(self, tape, block_pause=0):
        if not 10 <= len(tape) <= (32767 if self.stream_mode else 65535):
            raise ProtocolError("Taille de cassette invalide")
        self._sync()
        length = len(tape)
        self._write((SOH, 6, length & 255, length >> 8, 10))
        try:
            self._response(20 if self.stream_mode else 5)
        except ProtocolError as exc:
            raise ProtocolError(f"commande CLOAD, avant les données : {exc}") from exc
        payload = swap_header(tape)
        block_count = (length + 63) // 64
        if self.stream_mode:
            self.emit("log", f"Envoi de {length} octets en {block_count} blocs de 64")
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
                    f"bloc {block_number}/{block_count}, octets "
                    f"{offset + 1}–{min(length, offset + 64)} : {exc}"
                ) from exc
            if self.stream_mode and (block_number % 8 == 0 or block_number == block_count):
                self.emit("log", f"Arduino : {min(length, offset + 64)}/{length} octets acceptés")
        if self.stream_mode:
            # ACK acknowledges buffer intake. ETX follows the last waveform
            # bit, so the UI does not claim completion while XIN is active.
            try:
                self._expect(ETX, 10 + length * .040)
            except ProtocolError as exc:
                raise ProtocolError(f"fin du signal cassette après {length} octets : {exc}") from exc
            self.emit("log", f"Signal cassette terminé : {length} octets ; flux continu")
        else:
            self.emit("log", f"Envoi terminé : {length} octets ; pause/bloc {int(block_pause * 1000)} ms")

    def _receive(self):
        self._sync()
        self._write((SOH, 7))
        self._response()
        self.emit("log", "En attente de CSAVE…")
        start = self._read(120)
        if start == NAK:
            raise ProtocolError(f"Erreur Arduino {self._read(1)}")
        if start != STX:
            raise ProtocolError(f"Trame reçue 0x{start:02X} au lieu de STX")
        output = bytearray()
        while True:
            value = self._read(5)
            if value == DLE:
                value = self._read(1)
            elif value == ETX:
                break
            elif value == NAK:
                raise ProtocolError(f"Erreur Arduino {self._read(1)}")
            elif value == CAN:
                raise ProtocolError("Réception annulée")
            output.append(value)
            if len(output) > 65535:
                raise ProtocolError("Cassette trop longue")
        tape = swap_header(output)
        self.emit("received", tape)
        self.emit("log", f"CSAVE reçu : {len(tape)} octets")

    def _read_disk_frame(self):
        """Read CE-140F command-8 frame with DLE escaping.

        Firmware sends SOH, 8, STX, data bytes, ETX. The whole frame must
        be consumed before replying, or NAK can disrupt the Sharp protocol.
        """
        start = self._read(2.5)
        if start == NAK:
            raise ProtocolError("CE-140F Arduino error " + str(self._read(1)))
        if start != STX:
            raise ProtocolError(f"CE-140F: expected STX, got 0x{start:02X}")
        frame = bytearray()
        while True:
            value = self._read(2)
            if value == ETX:
                return bytes(frame)
            if value == DLE:
                value = self._read(2)
            elif value == CAN:
                raise ProtocolError("CE-140F: transmission cancelled")
            elif value == NAK:
                raise ProtocolError("CE-140F Arduino error " + str(self._read(1)))
            frame.append(value)
            if len(frame) > 8192:
                raise ProtocolError("CE-140F frame exceeds 8192-byte safety limit")

    def _disk_response(self, data, capture=False):
        """Reply via Arduino Manager::ProcessDataFrame and 64-byte ACKs."""
        if len(data) > 65535:
            raise ProtocolError("CE-140F response exceeds 16-bit length")
        self._write((SOH, 8, 0xFF if capture else 0,
                     len(data) & 255, (len(data) >> 8) & 255))
        self._response(5)
        for offset in range(0, len(data), 64):
            self._write(data[offset:offset + 64])
            self._response(5)

    def _disk_request(self):
        """Consume a disk frame and return a bounded no-drive result.

        This does not provide CE-140F file I/O. It prevents corrupting the
        serial protocol with NAK/3, and records command payloads for analysis.
        """
        payload = self._read_disk_frame()
        opcode = payload[0] if payload else None
        op = f"0x{opcode:02X}" if opcode is not None else "(empty)"
        self.emit("log", f"CE-140F: {op}, {len(payload)} bytes: {payload[:24].hex(' ')}")
        if (opcode == 0x04 and len(payload) == 3
                and payload[1] == 0xFF
                and (sum(payload[:-1]) & 0xFF) == payload[-1]):
            # The real PC-1403 sends 04 FF 03 (checksum included) when
            # closing ALL CE-140F handles, including after LPRINT.
            # Windows CE140F.CommandClose(0xFF) returns CreateResult(true)
            # even with no files open. Previously replying FF here caused
            # a fresh Sharp ERROR 1 after CLOAD was already successful.
            response = b"\x00"
            self.emit("log", "CE-140F CLOSE ALL (04 FF 03): OK; no files open")
        elif opcode == 0x05:
            # CE140F CommandFilesInit() with an empty/unconfigured directory.
            response = b"\x00\x00\x00"
        elif opcode in (0x03, 0x04, 0x0A, 0x0E, 0x0F, 0x10,
                        0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
                        0x17, 0x1D, 0x20):
            # Other CLOSE/file requests are unsupported without a drive.
            response = b"\xff"
        else:
            # CE140F ErrorFrame (unknown function).
            response = b"\xff\x00"
        self._disk_response(response)
        self.emit("log", f"CE-140F response: {response.hex(' ')}; no virtual drive")

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
                device = self._read(1)
                if device == 0x41 and self._printer_raw:
                    # Disk selection partway through printer traffic may
                    # explain why the calculator displays an error but the
                    # application shows only a single control character.
                    self.emit("log", f"LPRINT interrupted: raw {self._printer_raw.hex(' ')}")
                    self._printer_raw.clear()
                self.emit("log", f"Sharp device selected: 0x{device:02X}")
            elif command == 4:
                character = self._read(1)
                self._printer_raw.append(character)
                if character in (0x0E, 0x0F):
                    # ASCII SO/SI are printer control bytes, not glyphs.
                    label = "SO" if character == 0x0E else "SI"
                    self.emit("log", f"LPRINT control {label} (0x{character:02X})")
                else:
                    self.emit("print", "\n" if character == 13 else chr(character))
                if character in (0x0E, 13) or len(self._printer_raw) >= 128:
                    self.emit("log", f"LPRINT raw bytes: {self._printer_raw.hex(' ')}")
                    self._printer_raw.clear()
            elif command == 8:
                self._disk_request()
            elif command == 5:
                self.emit("log", f"Donnée : {self._read(1):02X}")
            else:
                self._write((NAK, 3))
                self.emit("log", f"Commande Arduino non prise en charge : {command}")
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
                        raise ProtocolError("Connecte d'abord la Pro Mini")
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
