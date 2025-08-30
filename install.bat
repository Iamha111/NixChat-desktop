@echo off

set PYTHON_VERSION=3.10.0
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_PTH_PREFIX=python310
set DIR=%LOCALAPPDATA%\NixChat
set OLD_DIR=%CD%

echo Installing NixChat...

mkdir %DIR%
mkdir %DIR%\python


echo Copying files...

xcopy /Y /I "%~dp0main.py" "%DIR%" >nul
xcopy /Y /I "%~dp0uninstall.bat" "%DIR%" >nul
xcopy /E /Y /I "%~dp0assets" "%DIR%\assets" >nul
rename "%DIR%\main.py" main.pyw

echo Installing runtime (Python %PYTHON_VERSION%)...

bitsadmin /transfer PythonDownload /download /priority normal %PYTHON_URL% "%TEMP%\nixchat-python.zip"
powershell -command "& {$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace((Get-Item '%TEMP%\nixchat-python.zip').FullName); $dest = $shell.NameSpace((Get-Item '%LOCALAPPDATA%\NixChat\python').FullName); $dest.CopyHere($zip.Items(), 64)}"
del "%TEMP%\nixchat-python.zip"
bitsadmin /transfer PipDownload /download /priority normal https://bootstrap.pypa.io/get-pip.py "%DIR%\python\get-pip.py"

(
echo %PYTHON_PTH_PREFIX%.zip
echo .
echo %DIR%
echo.
echo import site
) > "%DIR%\python\%PYTHON_PTH_PREFIX%._pth"

cd /d "%DIR%\python"
"%DIR%\python\python.exe" get-pip.py

"%DIR%\python\python.exe" -m pip install -r "%OLD_DIR%\requirements.txt"

echo Creating entries...

powershell -command "& {$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\NixChat.lnk'); $s.TargetPath = '%DIR%\python\python.exe'; $s.Arguments = '%DIR%\main.pyw'; $s.WorkingDirectory = '%DIR%'; $s.IconLocation = '%DIR%\assets\logo.ico'; $s.WindowStyle = 1; $s.save()}"

powershell -command "& {$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\NixChat.lnk'); $s.TargetPath = '%DIR%\python\python.exe'; $s.Arguments = '%DIR%\main.pyw -H'; $s.WorkingDirectory = '%DIR%'; $s.IconLocation = '%DIR%\assets\logo.ico'; $s.WindowStyle = 1; $s.save()}"

echo NixChat was succesfully installed!

pause
