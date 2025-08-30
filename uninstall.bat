@echo off

echo Uninstalling NixChat...

taskkill /f /im python.exe

rmdir /S /Q %LOCALAPPDATA%\NixChat
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\NixChat.lnk"
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\NixChat.lnk"

echo NixChat was succesfully uninstalled!

pause
