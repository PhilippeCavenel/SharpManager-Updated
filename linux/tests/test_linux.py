"""Linux conversion and serial integration tests; no Sharp hardware required.

Added 6 October 2026. See ../LICENSE-SharpManager.txt.
The serial tests use real pySerial and a Linux pseudo-terminal. They check
host framing, acknowledgements and escaping, not physical cassette timing.
"""

import os
from pathlib import Path
import pty
import queue
import select
import sys
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

LINUX = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LINUX))

from app import decode_basic, encode_basic, ports
from protocol import ACK, CAN, DLE, ETX, NAK, SOH, STX, SYN, Driver


def wire_header(tape):
    # Independent expected TAP-to-wire representation for unprotected BASIC.
    return tape[:1] + bytes((value % 16) * 16 + value // 16
                            for value in tape[1:8]) + tape[8:]


class FirmwarePeer:
    """Finite Arduino protocol peer at the other end of a real serial port."""

    def __init__(self, script):
        self.master, self.slave = pty.openpty()
        self.port = os.ttyname(self.slave)
        self.errors = []
        self.thread = threading.Thread(target=self.run, args=(script,), daemon=True)
        self.thread.start()

    def run(self, script):
        try:
            script(self)
        except Exception as exc:
            self.errors.append(exc)

    def read(self, length, timeout=10):
        result = bytearray()
        deadline = time.monotonic() + timeout
        while len(result) < length:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.master], [], [], remaining)[0]:
                raise AssertionError(f"Peer expected {length} bytes, got {bytes(result)!r}")
            result.extend(os.read(self.master, length - len(result)))
        return bytes(result)

    def expect(self, value):
        actual = self.read(len(value))
        if actual != value:
            raise AssertionError(f"Peer expected {value!r}, got {actual!r}")

    def write(self, value):
        os.write(self.master, bytes(value))

    def sync(self):
        self.expect(bytes([SYN]))
        self.write([SYN])

    def connect(self):
        self.sync()
        self.expect(bytes([SOH, 1]))
        self.write(bytes([SOH, 1, 3, 64, STX]) + b"PC-1403 flux continu V5" + bytes([ETX]))

    def close(self):
        self.thread.join(1)
        os.close(self.master)
        os.close(self.slave)


class LinuxTests(unittest.TestCase):
    def test_usb_ports_and_ftdi_preference(self):
        devices = [
            SimpleNamespace(device="/dev/ttyACM0", vid=0x2341),
            SimpleNamespace(device="/dev/ttyUSB1", vid=0x0403),
            SimpleNamespace(device="/dev/ttyUSB0", vid=0x067B),
            SimpleNamespace(device="/dev/ttyS0", vid=None),
        ]
        with patch("serial.tools.list_ports.comports", return_value=devices) as scan:
            self.assertEqual(ports(), ["/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyUSB0"])
            scan.assert_called_once_with(include_links=True)

    def test_basic_converter_round_trip(self):
        source_path = LINUX.parent / "examples/basic/BONJOUR.bas"
        tape = encode_basic(source_path)
        decoded = decode_basic(tape)
        expected = [line.strip() for line in source_path.read_text().splitlines() if line.strip()]
        self.assertEqual([line.strip() for line in decoded.splitlines() if line.strip()], expected)

    def make_driver(self, script):
        self.peer = FirmwarePeer(script)
        self.events = queue.Queue()
        self.history = []
        self.driver = Driver(lambda kind, data: self.events.put((kind, data)))
        self.addCleanup(self.cleanup_driver)
        self.action("connect", self.peer.port)

    def cleanup_driver(self):
        self.driver.submit("quit")
        self.driver.thread.join(2)
        self.peer.close()

    def action(self, action, *args, allow_error=False):
        self.driver.submit(action, *args)
        deadline = time.monotonic() + 15
        seen = []
        while time.monotonic() < deadline:
            if self.peer.errors:
                raise self.peer.errors[0]
            try:
                event = self.events.get(timeout=.1)
            except queue.Empty:
                continue
            self.history.append(event)
            seen.append(event)
            if event[0] == "error" and not allow_error:
                self.fail(event[1])
            if event == ("done", action):
                return seen
        self.fail(f"Driver did not finish {action}")

    def test_connect_ping_block_boundaries_receive_and_print(self):
        tests = LINUX.parent / "examples/tests-transfert"
        tapes = [(tests / folder / "TEST.tap").read_bytes()
                 for folder in ("64_octets", "65_octets")]
        self.assertEqual([len(tape) for tape in tapes], [64, 65])
        received = b"\x70ABCDEFG\x00\x00" + bytes([SOH, STX, ETX, DLE, NAK, CAN, SYN])
        counts = []
        final_signal = threading.Event()

        def script(peer):
            peer.connect()
            peer.sync()
            peer.expect(bytes([SOH, 2]))
            peer.write([ACK])
            for tape in tapes:
                peer.sync()
                peer.expect(bytes([SOH, 6, len(tape) & 255, len(tape) >> 8, 10]))
                peer.write([ACK])
                payload = bytearray()
                blocks = 0
                for offset in range(0, len(tape), 64):
                    payload.extend(peer.read(min(64, len(tape) - offset)))
                    blocks += 1
                    peer.write([ACK])
                self.assertEqual(bytes(payload), wire_header(tape))
                counts.append(blocks)
                time.sleep(.1)
                final_signal.set()
                peer.write([ETX])
            peer.sync()
            peer.expect(bytes([SOH, 7]))
            peer.write([ACK, STX])
            for value in wire_header(received):
                peer.write([DLE, value] if value in (ETX, DLE, NAK, CAN) else [value])
            peer.write([ETX])
            # Printer messages are processed by the same worker after CSAVE.
            for value in b"OK\r":
                peer.write([SOH, 4, value])
            peer.expect(bytes([CAN]))

        self.make_driver(script)
        self.assertTrue(self.driver.stream_mode)
        self.action("ping")
        for tape in tapes:
            final_signal.clear()
            self.action("send", tape)
            self.assertTrue(final_signal.is_set(), "Send finished before the final ETX")
        seen = self.action("receive")
        self.assertIn(("received", received), seen)
        printed = ""
        deadline = time.monotonic() + 3
        while len(printed) < 3 and time.monotonic() < deadline:
            kind, value = self.events.get(timeout=1)
            if kind == "print":
                printed += value
            elif kind == "error":
                self.fail(value)
        self.assertEqual(printed, "OK\n")
        self.assertEqual(counts, [1, 2])
        self.action("disconnect")
        self.peer.thread.join(1)
        self.assertFalse(self.peer.errors)

    def test_rejected_block_disconnects_before_more_data(self):
        tape = (LINUX.parent / "examples/tests-transfert/65_octets/TEST.tap").read_bytes()

        def script(peer):
            peer.connect()
            peer.sync()
            peer.expect(bytes([SOH, 6, 65, 0, 10]))
            peer.write([ACK])
            peer.expect(wire_header(tape)[:64])
            peer.write([NAK, 4])
            # A failed send closes the connection instead of sending byte 65.
            peer.expect(bytes([CAN]))

        self.make_driver(script)
        seen = self.action("send", tape, allow_error=True)
        errors = [value for kind, value in seen if kind == "error"]
        self.assertEqual(len(errors), 1)
        self.assertIn("block 1/2", errors[0])
        self.assertIn("Arduino error 4", errors[0])
        self.assertIsNone(self.driver.serial)
        self.peer.thread.join(1)
        self.assertFalse(self.peer.errors)


if __name__ == "__main__":
    unittest.main()
