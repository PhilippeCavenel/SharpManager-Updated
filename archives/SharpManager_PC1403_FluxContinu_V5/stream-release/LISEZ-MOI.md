# SharpManager PC-1403 · macOS V5 continuous streaming

*English translation of the delivery notes, 6 October 2026.*

This version is intended for the SharpStream firmware supplied in the same archive.
It retains TAP/BASIC sending and CSAVE reception. With this firmware, the Mac
receives an ACK as soon as each 64-byte block is accepted into the ring buffer.
Timer1 generates the cassette signal in parallel. When the buffer is empty,
XIN maintains a tone of 1 bits; ETX signals the actual end of the pulses.
The log then displays “Signal cassette terminé” (cassette signal finished).
However, the Sharp does not send confirmation that CLOAD succeeded.

## Build on the Mac mini M4

Install Python 3 with Tkinter and the Xcode command-line tools. After extracting
the entire archive, open `build-macos.command`. The application is created at
`dist/SharpManager-PC1403-V5-Flux.app`. The `.app` must be built on the Mac;
this archive contains sources and the script, without a macOS binary.

## Test

Back up the Sharp program first. Close SharpManager and disconnect the Sharp
connector from the Pro Mini before uploading the firmware. Open
`SharpStream/SharpStream.ino` in Arduino IDE, select Arduino Pro or Pro Mini,
ATmega328P 5 V / 16 MHz and the FTDI port, then upload. The compiled
`SharpStream.hex` file is also supplied for compatible AVR tools.
Reconnect the Sharp and open the V5 application. The connection should show
“synchro 2s - flux continu V5”. Start CLOAD and send the TAP as before.
Try the same file several times and record successful loads and ERROR 8 failures.
Do not add a 1 ms delay between bytes in `Tape.ino`.

To return to the previous version, upload the original firmware from
`SharpOriginalV5/SharpOriginalV5.ino` and use the macOS V4 application again.

The new signal generation has not yet been tested with a real Sharp. The firmware
uses Timer1 and Arduino pin D4 (PD4) for XIN, matching the current wiring.
The AVR compiler reported 8,144 flash bytes and 670 static RAM bytes.
The firmware sources are derived from SharpManager (Apache 2.0).
