# SharpManager PC-1403 for Windows

## Build from this GitHub repository

The repository contains source code and build scripts, not a ready-to-run
Windows installer. Building requires the **.NET 10 SDK**; the Desktop Runtime
alone cannot compile the application.

1. On Windows, open https://dotnet.microsoft.com/en-us/download/dotnet/10.0.
2. Under **Build apps - SDK**, download and install the Windows SDK:
   - **x64** for Windows on an Intel or AMD computer.
   - **Arm64** for Windows ARM in a virtual machine on an Apple Silicon Mac,
     including the Mac mini M4. Install it inside Windows, not on macOS.
3. Completely close Windows Terminal / PowerShell, then open a new terminal
   so it receives the updated PATH.
4. Verify the installation:

   ```powershell
   dotnet --version
   dotnet --list-sdks
   ```

   A .NET 10 SDK (`10.0.xxx`) must appear. If `dotnet` is not recognized,
   finish the SDK installation and restart the terminal before continuing.
5. Clone the repository with GitHub Desktop or your usual GitHub credentials.
   In PowerShell, enter the cloned repository's `windows` directory and run:

   ```powershell
   .\BuildWindowsBasic.bat
   ```

6. When the build succeeds, launch:

   ```powershell
   .\publish-windows\SharpManagerBasicPc1403.exe
   ```

Keep the **entire `publish-windows` directory**, including its DLLs and
`PocketTools` folder. No separate SharpManager installer is required.

The current build script targets **win-x64**, even when the build SDK is
Arm64. On Windows ARM, the resulting application needs x64 emulation and the
**.NET 10 Desktop Runtime for Windows x64**. If prompted at launch, install
that runtime from the same Microsoft download page, under **Run apps -
Runtime / .NET Desktop Runtime**. The ARM64 SDK does not supply the x64
Desktop Runtime. This is not a native ARM64 application; Philippe Cavenel reported successful operation under Parallels on 8 October
2026; see [the validation report](../docs/VALIDATION-2026-10-08.md).

## If you already have a compiled application

Extract the whole supplied application archive into a new directory, keep
all accompanying files, and launch `SharpManagerBasicPc1403.exe`. If it asks
for .NET, install the **.NET 10 Desktop Runtime x64**. An SDK is required only
when building from sources.

## Connect and test

Keep the working `flux continu V5 - garde 64` firmware already on the Pro Mini.
Close any Arduino Serial Monitor or other program using the FTDI port.
Select its COM port in SharpManager and click **Connect**. Start with
`../examples/basic/BONJOUR.bas`: on the Sharp, select RUN and enter `CLOAD`,
then send the BASIC file from the application.

See [LISEZ-MOI-WINDOWS-V52.txt](LISEZ-MOI-WINDOWS-V52.txt) for transfer,
CSAVE, firmware and validation details. Existing simulation results do not
establish that the Windows application works with the physical FTDI link.

## Troubleshooting: dotnet exists but is not recognized

Check the installed host:

```powershell
Test-Path "C:\Program Files\dotnet\dotnet.exe"
```

If it returns `True`, add the directory to PATH for the current terminal:

```powershell
$env:Path = "C:\Program Files\dotnet;$env:Path"
dotnet --list-sdks
.\BuildWindowsBasic.bat
```

A `10.0.xxx` SDK must be listed. This PATH change lasts only for this terminal
session. Close all terminal windows and reopen them to check whether the
installer has also registered the path permanently.

## FTDI cable in Parallels / Windows ARM

If Device Manager shows **FT232R USB UART** with a warning icon, Windows
detects the USB device but does not have a working driver for it. On a
Windows ARM guest, the driver must be **ARM64**, even though SharpManager is
an x64 application.

1. Connect the USB cable to the Windows guest in Parallels, then close any
   Mac application or serial monitor that uses the cable.
2. Download the **ARM** package in the **Windows (Desktop)** row from
   https://ftdichip.com/drivers/vcp-drivers/ (2.12.36.20A was the version
   referenced during this troubleshooting).
3. Extract the complete package to a local Windows directory, for example
   `C:\FTDI`, keeping its subdirectories and accompanying SYS/CAT files.
4. In Device Manager, update the FT232R driver, browse to that directory and
   include subfolders. If **USB Serial Port** then needs a driver, repeat
   the operation for it with the same directory.
5. If folder browsing cannot find the driver, open **Terminal / PowerShell
   as administrator** and run:

   ```powershell
   pnputil /add-driver "C:\FTDI\*.inf" /subdirs /install
   ```

   This imports the driver packages and installs them on matching devices;
   it does not override hardware or architecture compatibility. If it still
   fails, inspect the output and the device's hardware IDs.
6. Confirm **USB Serial Port (COMx)** appears under **Ports (COM & LPT)**,
   then select that COM port in SharpManager and connect.

The INF files may appear as `FTDIBUS` and `FTDIPORT` when Explorer hides
filename extensions. Windows x64 on an Intel/AMD PC needs the corresponding
x64 driver instead of the ARM64 package.

Microsoft command reference:
https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax

## Hardware report - 8 October 2026

Philippe Cavenel reports successful operation on Windows under Parallels,
behaving like the Mac and Ubuntu versions after the installation fixes.
See [the validation report](../docs/VALIDATION-2026-10-08.md) for the scope of
this user-reported result. This does not establish a per-operation test
matrix for every adapter and Windows version.
