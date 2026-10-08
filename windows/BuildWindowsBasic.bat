@echo off
setlocal
rem Updated 8 October 2026: check SDK availability and use LISEZ-MOI names.
where dotnet >nul 2>&1
if errorlevel 1 (
  echo ERROR: dotnet was not found. Install the .NET 10 SDK inside Windows.
  echo Download: https://dotnet.microsoft.com/en-us/download/dotnet/10.0
  echo Close all terminal windows and open PowerShell again after installation.
  exit /b 1
)
dotnet --list-sdks | findstr /B /C:"10." >nul
if errorlevel 1 (
  echo ERROR: the .NET 10 SDK is required. The Desktop Runtime alone cannot build.
  echo See README.md for installation instructions.
  exit /b 1
)
dotnet publish Desktop\SharpManager\SharpManager.csproj -c Release -r win-x64 --self-contained false -p:EnableWindowsTargeting=true -o publish-windows
if errorlevel 1 exit /b 1
copy LISEZ-MOI-WINDOWS-V52.txt publish-windows\LISEZ-MOI.txt
if not exist publish-windows\Firmware mkdir publish-windows\Firmware
copy Desktop\SharpManager.Common\Firmware\SharpStreamSafe.hex publish-windows\Firmware\
xcopy ContinuousFirmware publish-windows\Firmware\Arduino\ /E /I /Y
