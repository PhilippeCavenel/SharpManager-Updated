# SharpManager PC-1403 for Linux

**Linux V5.2** port, added on 6 October 2026 from the archived
macOS V5.2 Python / Tkinter application. Intended for testing on Ubuntu Desktop
with the FTDI cable, Pro Mini and Sharp PC-1403 used by this project.

The application sends `.tap` files or numbered BASIC `.bas` sources through
`CLOAD`, receives `CSAVE` into `.tap` and, when possible, `.bas`, and displays
`LPRINT` output. It uses the same Arduino driver 1.3 and continuous-stream
V5 firmware as the Mac version. CE-140F disk emulation and firmware flashing
are not implemented in this port.

## Install and start on Ubuntu

Install the system dependencies:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk gcc make git
```

Clone the repository using your usual GitHub authentication, or update your
existing checkout with `git pull`. Then run:

```bash
git clone https://github.com/PhilippeCavenel/SharpManager-Updated.git
cd SharpManager-Updated/linux
./setup-linux.sh
./run-linux.sh
```

Setup creates a local `.venv`, installs pySerial 3.5 and compiles the three
PocketTools converters for your Linux architecture. It does not install
system packages or change device permissions. Internet access is needed for
the first Python dependency installation. Run the application as your normal
user, in a graphical desktop session. Tkinter must be available to the Python
interpreter used for setup; `SHARP_PYTHON=/path/to/python3 ./setup-linux.sh`
can select another interpreter.

## Serial access

1. Connect the FTDI adapter. Click **Refresh** and choose its port, normally
   `/dev/ttyUSB0`. USB CDC devices such as `/dev/ttyACM0` also appear. FTDI
   devices are listed first. The port field is editable and accepts a stable
   `/dev/serial/by-id/...` path.
2. If opening the port reports **Permission denied**, inspect its permissions
   with `ls -l /dev/ttyUSB0`, substituting your actual port. On a standard
   Ubuntu installation the serial group is usually `dialout`. Add your user
   to that group if needed:

   ```bash
   sudo usermod -aG dialout "$USER"
   ```

   Log out of the desktop session and log in again, then restart the app.
   Adapt the group name if your system uses a different serial-device group.
3. Close any Arduino Serial Monitor or other application using the same port.
   Click **Connect**, then **Ping**. The driver uses **115200 baud** and
   verifies protocol version **1.3**. The connection log should identify the
   firmware with `flux continu V5` for continuous streaming.

Use the existing firmware in [`../firmware/SharpStreamSafe`](../firmware/SharpStreamSafe/)
and follow its wiring instructions. The connection can pulse FTDI RTS through
the Pro Mini's DTR/reset connection after synchronization fails. Linux port
support does not replace correct hardware wiring or firmware.

## First Ubuntu hardware test

- Start with [`BONJOUR.bas`](../examples/basic/BONJOUR.bas). Put the Sharp in
  **RUN** mode and enter `CLOAD`, then use **Send BASIC .bas** and confirm.
- Use **Send .tap** with the [64-byte and 65-byte test files](../examples/tests-transfert/)
  to check the transition between one and two serial blocks.
- Use **Receive CSAVE**, confirm, then enter `CSAVE` on the Sharp in RUN mode.
  Save the received TAP; the app also tries to decode it to BASIC and asks
  before replacing an existing BASIC file.
- Check `LPRINT "HELLO"` on the Sharp while the app is connected and idle.
- Try a longer program after the short tests pass, checking that the
  tokenized program and its variables fit in the Sharp's memory.

Transfers use 64-byte blocks and wait up to 20 seconds per block ACK in
continuous mode. The app also waits for the final ETX before reporting that
the cassette signal has ended. That message does not establish that the
Sharp completed `CLOAD` successfully: check its display and program contents.

For a test report, record the Ubuntu version and architecture, FTDI port and
adapter, firmware identifier, example used, result on the Sharp, and the
application log.

## Optional standalone bundle

Build on the Linux architecture where the application will run:

```bash
sudo apt install binutils
./build-linux.sh
./dist/SharpManager-Linux/SharpManager-Linux
```

The build installs PyInstaller 6 in `.venv` and includes the converters,
Tkinter dependencies, pySerial and notices. Keep the **whole**
`dist/SharpManager-Linux` directory, including `_internal`. This build does
not produce a Windows executable or a macOS app. Linux bundles depend on the
build system's architecture and glibc; build on the oldest Ubuntu release
you intend to support. System device permissions and a graphical session
are still required. Generated executables and build directories are excluded
from Git; this repository contains the sources and build scripts.

## Automated checks and validation limits

After setup, run:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests require Linux and the repository's `../examples` directory. They
compile no firmware and do not access a physical USB adapter.

Checks performed on **Ubuntu 24.04.3, x86_64** on 6 October 2026:

- All three PocketTools converters compiled with GCC; their preserved legacy
  C sources produce compiler warnings.
- BASIC → TAP → BASIC conversion matched the Bonjour source.
- Linux USB port filtering and FTDI preference passed.
- Real pySerial over a Linux pseudo-terminal passed connection, Ping,
  64/65-byte transfers with block ACKs and final ETX, escaped CSAVE reception,
  LPRINT, and disconnection after a rejected block.
- The PyInstaller directory bundle built successfully. Headless startup
  reports that a graphical desktop session is required.

**Status at the original 6 October delivery:** visual checks and physical FTDI / Pro Mini / PC-1403 tests were pending.

**Update, 8 October 2026:** Philippe Cavenel reports that the Ubuntu application works with his physical setup, as do the Mac and Windows versions. Exact OS builds and per-operation results were not supplied; see [the validation report](../docs/VALIDATION-2026-10-08.md). Serial simulations do not verify reset wiring,
cassette waveforms, timing on the Sharp or USB-driver behavior.

## Attribution and licensing

Based on [SharpManager by Wayne Venables / Codaris](https://github.com/codaris/SharpManager),
copyright 2024, Apache 2.0. See [`LICENSE-SharpManager.txt`](LICENSE-SharpManager.txt)
and the repository [`NOTICE`](../NOTICE). The Linux application and protocol
files identify the changes made from the macOS V5.2 sources.

PocketTools sources and their [`NOTICE.txt`](PocketTools/NOTICE.txt) are
preserved unchanged from the Mac delivery. They have separate terms;
the SharpManager license does not replace those terms. See the repository's
[publication conditions](../docs/PUBLICATION.md).

**Queen's Quest was published by Patrick Zumstein on the Facebook page
“80's Sharp pocket computers” and remains his property.** The game's
[examples and adaptations](../examples/queens-quest/README.md) retain that
attribution and are not covered automatically by SharpManager's Apache
license. A Facebook publication is not a redistribution license.

Technical references: [pySerial port discovery](https://pyserial.readthedocs.io/en/latest/tools.html),
[pySerial API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html),
[PyInstaller usage](https://pyinstaller.org/en/stable/usage.html), and Ubuntu
24.04 packages [python3-tk](https://packages.ubuntu.com/noble/python3-tk)
and [python3-venv](https://packages.ubuntu.com/noble/python3-venv).
