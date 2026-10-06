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
            self.emit("log", f"Connecté : {version.decode('latin-1', errors='replace')}")
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
            self.emit("log", "Déconnecté")

    def _ping(self):
        self._sync()
        self._write((SOH, 2))
        self._response(2.5)
        self.emit("log", "Ping : OK")

    def _send(self, tape):
        if not 10 <= len(tape) <= 65535:
            raise ProtocolError("Taille de cassette invalide")
        self._sync()
        length = len(tape)
        self._write((SOH, 6, length & 255, length >> 8, 10))
        self._response()
        payload = swap_header(tape)
        for offset in range(0, length, 64):
            self._write(payload[offset:offset + 64])
            self._response(8 if offset == 0 else 5)
        self.emit("log", f"Envoi terminé : {length} octets")

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
                self.emit("done", action)
