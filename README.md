# SharpManager-Updated

Source code and examples from Philippe Cavenel's **Sharp PC-1403** project, archived as of **6 October 2026**.
This project is based on [SharpManager by Wayne Venables / Codaris](https://github.com/codaris/SharpManager).

| Component | Reference version | Directory |
| --- | --- | --- |
| macOS application, Python / Tkinter, Apple Silicon | V5.2: connection recovery and continuous streaming | [macos](macos/) |
| Windows application, C# / WPF, .NET 10 | V5.2: continuous streaming | [windows](windows/) |
| Pro Mini ATmega328P firmware, 5 V / 16 MHz | V5: continuous streaming with a 64-byte buffer guard | [firmware](firmware/) |
| BASIC and TAP examples: Bonjour, stopwatch, 64/65-byte tests, Queen's Quest | All recovered variants, including the corrected French 8K version | [examples](examples/) |
| Earlier versions and copies of delivered sources | macOS, Windows and Arduino | [archives](archives/) |

## Build and use

- **Mac**: read [macos/README.md](macos/README.md), then run `macos/build-macos.command` on macOS arm64 with Python 3 / Tkinter and the Xcode command-line tools.
- **Windows**: use the .NET 10 SDK to build; run `BuildWindowsBasic.bat` from the `windows` directory. The published application requires the .NET 10 Desktop x64 runtime. See the [V5.2 instructions](windows/LIRE-MOI-WINDOWS-V52.txt).
- **Arduino**: open `firmware/SharpStreamSafe/SharpStreamSafe.ino` in Arduino IDE and select the Pro Mini ATmega328P 5 V / 16 MHz profile. See the [firmware instructions](firmware/LIRE-MOI.txt).
- Build scripts, resources, existing tests, converter source code and supplied HEX firmware files are included alongside the application sources.

Transfers use 64-byte serial blocks, an Arduino ring buffer and Timer1 to generate a continuous cassette signal. V5.2 waits up to 20 seconds for each ACK and distinguishes a block ACK from the final ETX signal. The limitations and test results documented in each delivery still apply: archiving does not constitute a new hardware test.

## Provenance and integrity

**Source code and firmware are preserved without content changes.** README and LIRE-MOI files were translated into English on 6 October 2026; their original text remains available in Git history at [the initial archive commit](https://github.com/PhilippeCavenel/SharpManager-Updated/tree/2737fe4916bee1ff1dda7640e8b0242335d22ae7). The [inventory](docs/INVENTAIRE.md) lists the deliveries and their original checksums. The [manifest](docs/source-manifest.json) records file checksums and identifies translated documentation separately.

Windows application executables, caches and generated website documentation are excluded from the source archive. PocketTools utilities included in the source packages are retained.

The older `SharpManager_BASIC_PC1403_Sources.zip` is truncated within a generated website documentation entry. The preceding 394 entries were recovered and checked against their recorded sizes and CRCs, including 49 identified `.cs`, `.py`, `.ino`, `.c` and `.h` source files. Recovery cannot establish what may have followed the truncated entry. The macOS and Windows V5.2 source archives are complete. See the [inventory](docs/INVENTAIRE.md) for details.

## License and publication

**The original SharpManager is licensed under Apache 2.0**, which permits modification and public redistribution, including commercial redistribution, subject to the license conditions. The original license and attribution are retained in [LICENSE](LICENSE) and [NOTICE](NOTICE).

The main license must not automatically be applied to independent components. **Redistribution rights for the PocketTools converters and Queen's Quest still need to be confirmed.** This archive repository remains private; these points must be resolved before publishing its full contents. See the [detailed publication conditions](docs/PUBLICATION.md) (in French).
