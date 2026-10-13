# PC-1403 CLOAD / LPRINT serial diagnostics (October 2026)

## Observed physical results

- On Philippe's PC-1403, testLprint.bas loads when BASIC cassette
  conversion omits the bin2wav --name option. The checkbox
  "CLOAD compatible (sans nom)" is enabled by default.
- During program execution, macOS reports
  "Commande Arduino non prise en charge : 8" and the Sharp displays
  ERROR 8. A Linux/Nano USB-C user reported the same command message.
- It is NOT confirmed yet that the new host-side disk response eliminates
  the physical Sharp error. A real-hardware retest is necessary.

## Code-level diagnosis

Arduino firmware Manager.ino version 1.3 uses:

| Serial packet | Meaning |
| --- | --- |
| SOH 03 <device> | Device Select; value 0x41 initiates disk capture |
| SOH 04 <character> | LPRINT/printer character |
| SOH 08 STX ... ETX | CE-140F disk command (not a printer character) |

The previous Mac/Linux idle readers treated 8 as unknown, wrote NAK/03,
and left the unread STX/payload/ETX in the serial stream. This could
interrupt an active transaction.

The updated code now consumes the entire framed disk request with DLE
unescaping, logging the device and disk opcode. It sends the expected
Arduino disk-response envelope (SOH/08, capture flag, 16-bit length,
then 64-byte ACK-checked blocks). Since no virtual drive is configured
on Mac/Linux, it returns a negative CE-140F operation result, or an
empty FILES listing. It does not silently write host files.

IMPORTANT: This is safe frame handling, NOT full CE-140F emulation.
If the Sharp selects device 0x41 unexpectedly in an LPRINT command,
the physical ERROR 8 may remain. The new logs will distinguish these.

## Real device regression

1. Close the prior application and rebuild the latest Mac version.
2. Connect FTDI/Arduino and Ping; record the firmware identification.
3. Keep the nameless BASIC CLOAD compatibility checkbox enabled.
4. On the real PC-1403 run CLOAD and send testLprint.bas (in examples).
   Confirm that the asterisk appears and the program loads.
5. Test a tiny BASIC program: 10 LPRINT "OK" / 20 END, and run it.
6. Run testLprint.bas, recording the full LPRINT log until failure.
7. In the log, inspect "Sharp device selected: 0xXX", "CE-140F: 0xXX",
   "CE-140F response", and printed lines. Record any Sharp ERROR 8.

No Arduino firmware change or reflashing is required for this host patch.

## Scope of automated validation

Linux pseudo-terminal integration tests emulate CE-140F command 8 with
DLE escaping and handshake ACKs, followed by regular LPRINT characters.
Tests also compare named and nameless BASIC tapes, showing unchanged
tokenized program data. They do NOT reproduce electrical timing on the
Sharp expansion connector.

## Additional physical trace: ERROR 1 during LPRINT (13 October 2026)

The user's next test showed:

    Sharp device selected: 0x0F
    [LPRINT SI/SO control characters; some visible 0.]
    Sharp device selected: 0x41
    CE-140F: 0x04, 3 bytes: 04 ff 03
    CE-140F response: ff; no virtual drive

The packet is **CLOSE ALL**:
- 0x04 = CE-140F file CLOSE
- 0xFF = all file handles
- 0x03 = (0x04 + 0xFF) & 0xFF checksum.

The previous no-drive CE140F fallback incorrectly returned FF (error) to
this perfectly valid close-all operation. The Windows CE140F implementation
calls CommandClose(0xFF), always returning CreateResult(true), one byte 00.
The Mac and Linux implementations now match that behavior exactly, after
validating the three-byte frame and its checksum.

The host additionally strips printer formatting bytes 0x0F (SI) and 0x0E
(SO) from the visible output and records their hex values. Each complete
LPRINT record writes a "LPRINT raw bytes" diagnostic. If device 0x41 is
selected before a printer record completes, the program logs "LPRINT
interrupted" with the raw bytes collected so far.

**Important limits:** This addresses one known host response error that can
cause the physical calculator to report ERROR 1, not necessarily the original
hardware LPRINT failure. It does not add a CE-140F filesystem, change
firmware timing, or prove that the Sharp emits all intended print characters.
A hardware retest is necessary.

## Character rendering instead of hexadecimal memory values (October 2026)

With the physical PC-1403, CLOAD and LPRINT work. The old test program
`testLprint.bas` printed `HEX (PEEK A)` and therefore deliberately generated
text like `E034. - 41.`. That text is NOT a serial decoder failure.

The test file now uses `C$=CHR$ X` for printable byte values
(decimal 32..126), and `.` for controls, BASIC token bytes and
other non-ASCII codes (for example 0xFF, 0x00 and 0xA7).
It keeps the memory address in HEX as a location reference:
`E034. - A`, `E035. - =`, `E037. - &` and `E038. - F`.
An unchanged diagnostic copy is available as `testLprint-hex.bas`.

The Mac and Linux apps additionally have an unchecked-by-default
`LPRINT HEX bytes (diagnostics)` option. Normal printed characters remain
visible; internal `LPRINT raw bytes`, `LPRINT control SO/SI` and
`LPRINT interrupted: raw` log entries are hidden unless the option is on.
This does not modify the FTDI, Arduino firmware, timing or the cassette
transfer protocol. Critical CE-140F protocol logs and errors remain visible.

On physical hardware: use RUN mode, start `CLOAD`, send the new
`examples/tests-transfert/testLprint.bas`, then `RUN`. Unlike the old
program it prints characters instead of their hexadecimal values.
The graphical Studio's ROM-free BASIC interpreter still does NOT model
full Sharp PEEK memory mapping, so this example is for the real PC-1403.
