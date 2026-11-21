@echo off
setlocal
cd /d "%~dp0"

set "APP=src\gui\card_gui.py"
set "PYW=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\pythonw.exe"

if exist "%PYW%" (
  start "" "%PYW%" "%APP%"
  goto :done
)

py -3.12w -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
  start "" py -3.12w "%APP%"
  goto :done
)

python -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
  start "" pythonw "%APP%"
  goto :done
)

echo [ERROR] No Python with tkinter found.
echo Install Python 3.12+ with tcl/tk, or run: py -3.12 src\gui\card_gui.py
pause
exit /b 1

:done
endlocal
