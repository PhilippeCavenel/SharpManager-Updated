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
Desktop Runtime. This is not a native ARM64 application; physical FTDI tests
on Windows ARM have not been confirmed.

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
