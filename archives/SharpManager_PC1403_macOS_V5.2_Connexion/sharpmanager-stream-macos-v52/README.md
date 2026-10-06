# SharpManager PC-1403 · macOS V5.2 continuous streaming

*English translation of the delivery notes, 6 October 2026.*

This version builds on the macOS V5.1 sources and the already installed
“synchro 2s - flux continu V5” firmware. It retains the 20-second ACK timeout
and block progress reporting during long transfers. The Pro Mini does not
need to be reflashed.

## Connection recovery fix

After an interrupted transfer, the firmware may still be busy with CLOAD and
stop responding to SYN bytes. V5.2 first tries three SYN attempts. If none
receives a reply, it pulses RTS, connected to DTR/reset in this setup, waits
for the bootloader to finish and tries again. A sending error closes the port
so that recovery can run on the next connection. This reset can interrupt an
active transfer; it is used only during connection when no SYN received a reply.

## Build on the Mac mini M4

Extract the entire archive and open `build-macos.command`. Python 3 with
Tkinter and the Xcode command-line tools are required. The application is
created at `dist/SharpManager-PC1403-V5.2-Flux.app`. Close the old SharpManager
before launching it. This ZIP contains sources, not a ready-to-run macOS binary.

## Supplied test file

The `queen's quest.bas` program supplied by Philippe converts to a 5,717-byte
TAP containing 90 serial blocks. It decodes back to 258 BASIC lines.
The `test/queens_quest_PC1403.tap` file in the archive allows direct testing
of **Envoyer .tap** (Send .tap). The original source file is not modified.

If sending fails, record the complete message, especially the block number
and whether it reports an Arduino error or a timeout. The message
“Signal cassette terminé” (cassette signal finished) confirms the end of
transmission, not successful CLOAD on the Sharp.

SharpManager sources are licensed under Apache 2.0. See `PocketTools/NOTICE.txt`
for the converters' conditions.
