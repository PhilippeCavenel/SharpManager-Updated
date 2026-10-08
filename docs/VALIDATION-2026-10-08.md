# Hardware validation reported on 8 October 2026

Philippe Cavenel reports that SharpManager now works with his physical
FTDI / Pro Mini / Sharp PC-1403 setup on **macOS, Ubuntu and Windows**.
These are user-reported hardware results, additional to the earlier software
and serial-simulation checks. They are not a new automated test run.

| Platform | Reported result | Setup / recovery observed |
| --- | --- | --- |
| macOS | Working after rebuilding from the cloned sources | Connection succeeded after the connection troubleshooting steps. The precise cause of the initial failure was not isolated. |
| Ubuntu | Working | Installed dependencies, authenticated to the private GitHub repository and launched the Linux application. |
| Windows under Parallels | Working, reported to behave like Mac and Linux | Made `dotnet` accessible through PATH and installed the FTDI ARM64 driver for the Windows virtual machine. |

The setup uses an FTDI FT232R USB UART cable and a Pro Mini ATmega328P
5 V / 16 MHz with the continuous-stream V5 firmware. The Windows instructions
cover Parallels on Apple Silicon and an x64 application build.

The exact OS build numbers and a separate pass/fail record for each operation
(CLOAD, CSAVE, LPRINT, short/long files and 64/65-byte boundaries) were not
provided with this report. The overall success must not be read as an
exhaustive compatibility matrix for all computers, adapters or operations.

## Windows installation lessons

- Building from the repository requires the .NET 10 **SDK**, installed
  inside Windows. The Desktop Runtime alone cannot compile the program.
- On Windows ARM, use the ARM64 SDK. The current script builds `win-x64`;
  running it requires x64 emulation and the x64 .NET 10 Desktop Runtime.
- `C:\Program Files\dotnet\dotnet.exe` existed but `dotnet` was initially
  absent from the terminal PATH. Adding its directory for that PowerShell
  session allowed the build commands to find it.
- Windows detected `FT232R USB UART` with a warning icon. Use the FTDI
  **ARM64 VCP** driver in a Windows ARM guest, not an x64 kernel driver.
- When Device Manager did not find the driver through its folder search,
  the subsequent troubleshooting used a complete extracted driver package
  copied to `C:\FTDI` and PnPUtil installation from an administrator terminal.
  The user subsequently confirmed the driver and application worked.

See [the Windows guide](../windows/README.md) for the exact commands.
The working Pro Mini firmware is shared across the three platforms and does
not need to be reflashed simply because the host operating system changes.

## Provenance and redistribution facts

PocketTools is bundled without modification. Queen's Quest was published
by Patrick Zumstein on the public Facebook page “80's Sharp pocket computers”,
without an accompanying licence, according to Philippe Cavenel.
The original author attribution is retained for the game and its adaptations.
These facts do not establish a new redistribution licence; see
[publication conditions](PUBLICATION.md). No visibility change is part of
this documentation update.
