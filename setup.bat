@echo off
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    powershell -Command "Invoke-WebRequest -Uri 'https://fe.wibu.me/Python311.zip' -OutFile 'Python311.zip'"
    powershell -Command "Expand-Archive -Path 'Python311.zip' -DestinationPath 'C:\Program Files\Python311' -Force"
    setx /M PATH "C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
    set "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
)

where python >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Python installation failed or PATH not updated. Please reboot manually.
    pause
    exit /b
)

pip install flask requests

if exist main.py (
    python main.py
) else (
    echo main.py not found.
)

pause
