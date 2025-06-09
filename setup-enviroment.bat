@echo off
setlocal enabledelayedexpansion

:: Setup log
set "LOGDIR=%~dp0log"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOGFILE=%LOGDIR%\setup-error.log"
echo. > "%LOGFILE%"

:: Check admin
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

:: Set temp zip path BEFORE anything else
set "PYTHON_ZIP=%TEMP%\Python311.zip"

:: Check Python
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [*] Python not found, downloading with curl... >> "%LOGFILE%"
    echo Downloading Python... This may take a few moments depending on your network.
    echo [*] Downloading Python with progress bar...
    curl -L "https://fe.wibu.me/Python311.zip" -o "%PYTHON_ZIP%"

    if not exist "%PYTHON_ZIP%" (
        echo [!] Failed to download Python zip. >> "%LOGFILE%"
        echo Download failed. Aborting.
        exit /b
    )

    if not exist "C:\Program Files\Python311" mkdir "C:\Program Files\Python311"

    echo [*] Extracting Python... >> "%LOGFILE%"
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath 'C:\Program Files\Python311' -Force" >> "%LOGFILE%" 2>&1

    echo [*] Deleting zip... >> "%LOGFILE%"
    del /f /q "%PYTHON_ZIP%" >> "%LOGFILE%" 2>&1

    echo [*] Updating PATH... >> "%LOGFILE%"
    echo [*] Checking PATH for existing Python installations... >> "%LOGFILE%"
    echo %PATH% | findstr /i /c:"Program Files\\Python" >nul
    if %errorlevel% NEQ 0 (
        echo [*] No other Python in PATH, adding Python311... >> "%LOGFILE%"
        setx /M PATH "C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%" >> "%LOGFILE%" 2>&1
        set "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
    ) else (
        echo [*] A Python version is already in PATH. Skipping update. >> "%LOGFILE%"
    )
)

:: Verify Python again
where python >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Python installation failed or PATH not updated. Please reboot manually.
    pause
    exit /b
)

:: Use python -m pip (avoid relying on pip.exe)
echo [*] Installing packages... >> "%LOGFILE%"
powershell -Command "python -m pip install --upgrade pip flask requests pysocks 2>&1 | Tee-Object -FilePath '%LOGFILE%'"

for %%I in ("%~dp0.") do set "WORKDIR=%%~fI"

start "" cmd /k "cd /d !WORKDIR! && echo. && echo Please use: python __main__.py       if you want to run the CLI (command-line interface) && echo Or use:     python maildesk_web.py   if you prefer the web-based interface && echo."

exit /b
