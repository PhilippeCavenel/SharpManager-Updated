# SharpManager PC-1403 · macOS V5.1 continuous streaming

*English translation of the delivery notes, 6 October 2026.*

This version fixes acknowledgment waiting for long TAP transfers.
It is compatible with the “synchro 2s - flux continu V5” firmware already
installed on the Pro Mini. Reflashing the firmware is not required.

## Build on the Mac mini M4

After extracting the entire archive, open `build-macos.command`. It uses
Python 3 with Tkinter and the Xcode command-line tools to build
`dist/SharpManager-PC1403-V5.1-Flux.app`. The `.app` must be built on the Mac;
this archive does not contain a macOS binary.

Close the older V5 application before launching V5.1. Select the FTDI port,
connect and check that the log displays “flux continu V5”. Start CLOAD on
the Sharp and send the TAP as before.

For each 64-byte block, SharpManager V5.1 now waits up to 20 seconds for the
ACK instead of 5 seconds, or 8 seconds for the first block. The log reports
the accepted byte count every eight frames. On failure, the message reports
the block number and affected byte range. After the final ACK, the application
still waits for ETX. This means the cassette pulses have finished; it does
not mean the Sharp completed CLOAD successfully.

If a block error becomes “Erreur Arduino 1” (Arduino error 1), the firmware's
internal timeout has expired and must be corrected on the Arduino side.
A new “20 s” error would indicate a missing or lost acknowledgment. Record
the reported block number to continue diagnosis.

SharpManager sources are licensed under Apache 2.0. The included Pocket Tools
sources have their own conditions; see `PocketTools/NOTICE.txt`.
