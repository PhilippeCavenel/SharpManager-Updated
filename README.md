# SharpManager-Updated

Source code and examples from Philippe Cavenel's **Sharp PC-1403** project, archived as of **6 October 2026**.
This project is based on [SharpManager by Wayne Venables / Codaris](https://github.com/codaris/SharpManager).

| Component | Reference version | Directory |
| --- | --- | --- |
| macOS application, Python / Tkinter, Apple Silicon | V5.2: connection recovery and continuous streaming | [macos](macos/) |
| Windows application, C# / WPF, .NET 10 | V5.2: continuous streaming | [windows](windows/) |
| Linux application, Python / Tkinter | Experimental V5.2 port for Ubuntu testing | [linux](linux/) |
| Pro Mini ATmega328P firmware, 5 V / 16 MHz | V5: continuous streaming with a 64-byte buffer guard | [firmware](firmware/) |
| BASIC and TAP examples: Bonjour, stopwatch, 64/65-byte tests, Queen's Quest | All recovered variants, including the corrected French 8K version | [examples](examples/) |
| Earlier versions and copies of delivered sources | macOS, Windows and Arduino | [archives](archives/) |

## Build and use

- **Mac**: read [macos/README.md](macos/README.md), then run `macos/build-macos.command` on macOS arm64 with Python 3 / Tkinter and the Xcode command-line tools.
- **Windows**: first install the **.NET 10 SDK inside Windows**, then reopen your terminal and check `dotnet --version`. Run `BuildWindowsBasic.bat` from `windows`, then launch `publish-windows/SharpManagerBasicPc1403.exe`. See [windows/README.md](windows/README.md) for x64 / Windows ARM setup, runtime requirements and troubleshooting, and the [V5.2 transfer instructions](windows/LISEZ-MOI-WINDOWS-V52.txt).
- **Linux / Ubuntu**: install Python 3, `python3-venv`, `python3-tk`, GCC and Make, then run `./setup-linux.sh` and `./run-linux.sh` from `linux`. See [linux/README.md](linux/README.md) for USB permissions, the optional standalone build and the hardware test procedure. Software checks were performed on Ubuntu 24.04.3 x86_64; desktop and physical Sharp tests are pending.
- **Arduino**: open `firmware/SharpStreamSafe/SharpStreamSafe.ino` in Arduino IDE and select the Pro Mini ATmega328P 5 V / 16 MHz profile. See the [firmware instructions](firmware/LISEZ-MOI.txt).
- Build scripts, resources, existing tests, converter source code and supplied HEX firmware files are included alongside the application sources.

Transfers use 64-byte serial blocks, an Arduino ring buffer and Timer1 to generate a continuous cassette signal. V5.2 waits up to 20 seconds for each ACK and distinguishes a block ACK from the final ETX signal. The limitations and test results documented in each delivery still apply: archiving does not constitute a new hardware test.

## Provenance and integrity

**Archived application and firmware source code is preserved without functional changes.** The new Linux port is derived from macOS V5.2 and identifies its modifications in its application and protocol files. README and LISEZ-MOI files were translated into English on 6 October 2026; their original text remains available in Git history at [the initial archive commit](https://github.com/PhilippeCavenel/SharpManager-Updated/tree/2737fe4916bee1ff1dda7640e8b0242335d22ae7). The [inventory](docs/INVENTAIRE.md) lists the deliveries and their original checksums. The [manifest](docs/source-manifest.json) records file checksums and identifies translated documentation and new Linux files separately.

Windows application executables, caches and generated website documentation are excluded from the source archive. PocketTools utilities included in the source packages are retained.

The older `SharpManager_BASIC_PC1403_Sources.zip` is truncated within a generated website documentation entry. The preceding 394 entries were recovered and checked against their recorded sizes and CRCs, including 49 identified `.cs`, `.py`, `.ino`, `.c` and `.h` source files. Recovery cannot establish what may have followed the truncated entry. The macOS and Windows V5.2 source archives are complete. See the [inventory](docs/INVENTAIRE.md) for details.

## License and publication

**The original SharpManager is licensed under Apache 2.0**, which permits modification and public redistribution, including commercial redistribution, subject to the license conditions. The original license and attribution are retained in [LICENSE](LICENSE) and [NOTICE](NOTICE).

**Queen's Quest was published by Patrick Zumstein on the Facebook page “80's Sharp pocket computers” and remains his property.** This attribution applies to the original program and its archived translations, adaptations and TAP files. See the [game's attribution](examples/queens-quest/README.md).

The main license must not automatically be applied to independent components. **Redistribution rights for the PocketTools converters and Queen's Quest still need to be confirmed.** This archive repository remains private; these points must be resolved before publishing its full contents. See the [detailed publication conditions](docs/PUBLICATION.md) (in French).

On 8 October 2026, instruction files were renamed from `LIRE`-`MOI` to `LISEZ-MOI`. Build-script references and the source manifest were updated; explicit Windows SDK installation instructions and a missing-SDK diagnostic were added. Original delivery paths and checksums remain recorded in the manifest and Git history.
