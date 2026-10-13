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

    def test_cload_compat_header_preserves_basic(self):
        """Unnamed cassette: a header variant, not modified BASIC contents."""
        source = LINUX.parent / "examples/basic/BONJOUR.bas"
        named = encode_basic(source, compatible=False)
        compat = encode_basic(source, compatible=True)
        self.assertEqual(len(named), len(compat))
        self.assertEqual(named[0], 0x70)
        self.assertEqual(compat[0], 0x70)
        self.assertNotEqual(named[1:8], compat[1:8])
        self.assertEqual(named[10:], compat[10:])
        self.assertEqual(decode_basic(named), decode_basic(compat))

    def test_disk_command8_consumed_without_corrupting_lprint(self):
        """SOH/8 is framed CE140F traffic, not an unknown Arduino command.

        The Arduino waits for a proper SOH/8 response; replying NAK/3 to
        its outbound frame corrupts the channel and can cause Sharp ERROR 8.
        No virtual disk is configured: unsupported disk actions receive a
        negative result, while subsequent LPRINT bytes must still arrive.
        """
        def script(peer):
            peer.connect()
            time.sleep(.15)
            peer.write([SOH, 3, 0x41])  # CE-140F device selected by Sharp
            peer.write([SOH, 8, STX, DLE, NAK, 0x02,
                        DLE, ETX, DLE, CAN, ETX])
            # Negative CE140F response, not generic NAK/3:
            peer.expect(bytes([SOH, 8, 0, 1, 0]))
            peer.write([ACK])
            peer.expect(bytes([0xFF]))
            peer.write([ACK])
            # Ensure idle LPRINT remains synchronized after Disk frame.
            for ch in b"HELLO\r":
                peer.write([SOH, 4, ch])
                time.sleep(.015)
            peer.expect(bytes([CAN]))

        self.make_driver(script)
        printed = ""
        logs = []
        deadline = time.monotonic() + 4
        while len(printed) < 6 and time.monotonic() < deadline:
            if self.peer.errors:
                raise self.peer.errors[0]
            try:
                kind, value = self.events.get(timeout=.1)
            except queue.Empty:
                continue
            if kind == "print":
                printed += value
            elif kind == "log":
                logs.append(value)
            elif kind == "error":
                self.fail(value)
        self.assertEqual(printed, "HELLO\n")
        self.assertTrue(any("CE-140F" in s and "15" in s for s in logs))
        self.assertTrue(any("0x41" in s for s in logs))

    def test_pc1403_exact_close_all_trace_and_lprint_controls(self):
        """Physical trace: 0x0F printer, 0x41 disk, frame 04 FF 03.

        No virtual drive is installed. CLOSE ALL must still return success,
        exactly as Windows CE140F.CommandClose(0xFF) does. SI/SO control
        characters must not turn into visible garbage in the print window.
        """
        def script(peer):
            peer.connect()
            peer.write([SOH, 3, 0x0F])
            for value in (0x0F, ord("O"), ord("K"), 0x0E, 13):
                peer.write([SOH, 4, value])
                time.sleep(.01)
            peer.write([SOH, 3, 0x41])
            peer.write([SOH, 8, STX, 0x04, 0xFF, 0x03, ETX])
            peer.expect(bytes([SOH, 8, 0, 1, 0]))
            peer.write([ACK])
            peer.expect(bytes([0x00]))  # SUCCESS, not the earlier 0xFF
            peer.write([ACK])
            peer.expect(bytes([CAN]))

        self.make_driver(script)
        printed, logs = "", []
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.peer.errors:
                raise self.peer.errors[0]
            try:
                kind, value = self.events.get(timeout=.1)
            except queue.Empty:
                continue
            if kind == "print":
                printed += value
            if kind == "log":
                logs.append(value)
            if kind == "error":
                self.fail(value)
            if "OK" in printed and "CE-140F response: 00" in logs:
                break
        self.assertEqual(printed, "OK\n")
        self.assertIn("CE-140F response: 00; no virtual drive", logs)
        self.assertTrue(any("CLOSE ALL" in entry for entry in logs))
        self.assertTrue(any("device selected: 0x0F" in entry for entry in logs))
        self.assertTrue(any("device selected: 0x41" in entry for entry in logs))
        self.assertTrue(any("LPRINT control SI" in entry for entry in logs))
        self.assertTrue(any("LPRINT control SO" in entry for entry in logs))
        self.action("disconnect")
        self.peer.thread.join(1)
        self.assertFalse(self.peer.errors)

    def test_malformed_close_all_is_not_implicitly_accepted(self):
        """Only a proper checksum 04+FF=03 is acknowledged as CLOSE ALL."""
        def script(peer):
            peer.connect()
            peer.write([SOH, 8, STX, 0x04, 0xFF, 0x04, ETX])
            peer.expect(bytes([SOH, 8, 0, 1, 0]))
            peer.write([ACK])
            peer.expect(bytes([0xFF]))
            peer.write([ACK])
            peer.expect(bytes([CAN]))

        self.make_driver(script)
        logs = []
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            if self.peer.errors:
                raise self.peer.errors[0]
            try:
                kind, value = self.events.get(timeout=.1)
            except queue.Empty:
                continue
            if kind == "log":
                logs.append(value)
                if "CE-140F response" in value:
                    break
            if kind == "error":
                self.fail(value)
        self.assertTrue(any("CE-140F response: ff" in x for x in logs), logs)
        self.action("disconnect")
        self.peer.thread.join(1)
        self.assertFalse(self.peer.errors)

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
