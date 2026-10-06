@echo off
setlocal
dotnet publish Desktop\SharpManager\SharpManager.csproj -c Release -r win-x64 --self-contained false -p:EnableWindowsTargeting=true -o publish-windows
if errorlevel 1 exit /b 1
copy LIRE-MOI-BASIC.txt publish-windows\LIRE-MOI.txt
if not exist publish-windows\Firmware mkdir publish-windows\Firmware
copy Desktop\SharpManager.Common\Firmware\ProMiniSync2s.hex publish-windows\Firmware\
xcopy Arduino publish-windows\Firmware\Arduino\ /E /I /Y
