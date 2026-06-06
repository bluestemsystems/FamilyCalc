@echo off
REM ============================================================
REM  Build FamilyCalc.exe  (run this on a Windows machine)
REM  Requires Python 3 installed (https://www.python.org/downloads/).
REM  Produces:  dist\FamilyCalc.exe   (a single, self-contained .exe)
REM ============================================================
setlocal
cd /d "%~dp0"

REM Prefer the Windows "py" launcher; fall back to "python".
where py >nul 2>nul && (set "PY=py") || (set "PY=python")

echo Installing / updating PyInstaller...
%PY% -m pip install --upgrade pyinstaller || goto :err

echo Building FamilyCalc.exe ...
%PY% -m PyInstaller --noconfirm --onefile --noconsole ^
  --name FamilyCalc ^
  --icon FamilyCalc.ico ^
  --add-data "index.html;." ^
  server.py || goto :err

echo.
echo ============================================================
echo  Done.  Your app is here:   dist\FamilyCalc.exe
echo  Double-click it to run, or build the installer with
echo  Inno Setup (see FamilyCalc.iss) for a real installer.
echo ============================================================
pause
exit /b 0

:err
echo.
echo BUILD FAILED. Make sure Python 3 is installed and on PATH.
pause
exit /b 1
