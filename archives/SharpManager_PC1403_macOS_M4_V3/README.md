# SharpManager PC-1403 for macOS Apple Silicon

*English translation of the delivery notes, 6 October 2026.*

A macOS application for the PC-1403 and Pro Mini running **Arduino Driver 1.3**,
including the V5 “synchro 2s” variant. It uses the serial protocol and Pocket
Tools converters. CE-140F disk functionality and firmware upload are not implemented.

## Build on the Mac mini M4

1. Install Python 3 for macOS from python.org, with Tkinter. If the Apple
   command-line tools are missing, install them with `xcode-select --install`.
2. Extract the entire archive, then open `build-macos.command` from Finder.
   If macOS blocks it, right-click and choose Open. The script installs Python
   dependencies in a local `.venv` directory and builds Pocket Tools for
   Apple Silicon.
3. The resulting application is `dist/SharpManager-PC1403-V3.app`, with “macOS V3” in its title. It is unsigned and not notarized; on first launch, right-click
   and choose Open if macOS requests it.

The build must run on the Mac. This archive contains sources and the build
script, **not a prebuilt macOS binary**.

## Use

- Connect the FTDI cable, select its `/dev/cu.usbserial…` port and click
  **Connecter** (Connect), then **Ping**. Keep the other SharpManager closed.
- **Envoyer .tap** (Send .tap) or **Envoyer BASIC .bas** (Send BASIC .bas):
  select a file, start `CLOAD` on the Sharp in RUN mode, then confirm on the Mac.
  The application converts `.bas` in memory and sends its contents to the firmware.
- **Recevoir CSAVE** (Receive CSAVE): click the button, confirm the dialog,
  then start `CSAVE` on the Sharp. Choose a `.tap` filename. If the cassette
  contains unprotected BASIC, a `.bas` file with the same name is also created.
  Keep the `.tap` as the original backup and to check `CSAVE → CLOAD` round trips.
- `LPRINT` output appears in the log.

Conversion requires numbered BASIC lines in ascending order. Transfers must
be checked on the hardware; switching computers should not be assumed to
resolve the intermittent ERROR 8 observed on Windows.

This port uses SharpManager's Apache 2.0 sources and the included Pocket Tools
sources for personal, non-commercial use; see `PocketTools/NOTICE.txt`.
