@REM @echo off
@REM setlocal ENABLEDELAYEDEXPANSION

@REM REM ==============================
@REM REM Check for Python 3.10 or higher
@REM REM ==============================
@REM where py >nul 2>&1
@REM if errorlevel 1 (
@REM     echo Error: Python launcher ^(py^) not found. Please install Python 3.x from python.org with "py" enabled.
@REM     goto :EOF
@REM )

@REM REM Get latest Python 3.x version
@REM for /f "tokens=2 delims= " %%v in ('py -3 --version 2^>nul') do (
@REM     set PYVER=%%v
@REM )
@REM if not defined PYVER (
@REM     echo Error: No Python 3.x installation found.
@REM     goto :EOF
@REM )

@REM REM Parse major.minor from X.Y.Z
@REM for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
@REM     set MAJOR=%%a
@REM     set MINOR=%%b
@REM )

@REM if not "%MAJOR%"=="3" (
@REM     echo Error: Python 3.x required, found %PYVER%.
@REM     goto :EOF
@REM )

@REM if %MINOR% LSS 10 (
@REM     echo Error: Python 3.10 or newer is required, found %PYVER%.
@REM     goto :EOF
@REM )

@REM echo Using Python version %PYVER%.
@REM echo.

@REM REM ==============================
@REM REM Check if port 5500 is in use
@REM REM ==============================
@REM set PID=
@REM for /f "tokens=5" %%P in ('netstat -aon ^| findstr :5500 ^| findstr LISTENING') do (
@REM     set PID=%%P
@REM )

@REM if defined PID (
@REM     echo Error: Port 5500 is already in use by process ID %PID%.
@REM     set /p CHOICE=Do you want to stop this process? [y/N]:
@REM     if /I "%CHOICE%"=="Y" (
@REM         taskkill /PID %PID% /F
@REM         echo Process %PID% killed.
@REM     ) else (
@REM         echo Please stop the process manually or choose another port.
@REM         goto :EOF
@REM     )
@REM )
@REM echo.

@REM REM ==============================
@REM REM Check for venv and activate
@REM REM ==============================
@REM if exist "venv" (
@REM     echo Activating virtual environment...
@REM     call venv\Scripts\activate.bat

@REM     echo Installing dependencies...
@REM     py -3 -m pip install -r requirements.txt
@REM ) else (
@REM     echo Virtual environment 'venv' not found.
@REM     set /p CREATE_VENV=Do you want to create it now? [y/N]:
@REM     if /I "%CREATE_VENV%"=="Y" (
@REM         py -3 -m venv venv
@REM         echo Virtual environment 'venv' created.
@REM         call venv\Scripts\activate.bat
@REM         echo Installing dependencies...
@REM         py -3 -m pip install -r requirements.txt
@REM     ) else (
@REM         echo Please create the virtual environment and install dependencies manually.
@REM         goto :EOF
@REM     )
@REM )
echo.

REM ==============================
REM Create logs directory
REM ==============================
if not exist logs (
    mkdir logs
)

echo --------------------[ Starting Server - %date% %time% ]-------------------- >> logs\access.log
echo --------------------[ Starting Server - %date% %time% ]-------------------- >> logs\error.log

REM ==============================
REM Start the server with Gunicorn
REM ==============================
echo Starting server on http://localhost:5500 and http://0.0.0.0:5500
echo Health check: http://localhost:5500/health
echo.

REM Note: Gunicorn does not support Windows natively; this is suitable for WSL or Linux.
REM If gunicorn is installed as a script in the venv, this will run it:
gunicorn ^
    --worker-class eventlet ^
    --workers 1 ^
    --bind 0.0.0.0:5500 ^
    --timeout 60 ^
    --keep-alive 2 ^
    --max-requests 1000 ^
    --access-logfile logs/access.log ^
    --error-logfile logs/error.log ^
    --capture-output ^
    --log-level info ^
    --reload ^
    app:app ^

REM Alternatively, you can use:
REM py -3 -m gunicorn ^
REM     --worker-class eventlet ^
REM     --workers 1 ^
REM     --bind 0.0.0.0:5500 ^
REM     --timeout 60 ^
REM     --keep-alive 2 ^
REM     --max-requests 1000 ^
REM     --access-logfile logs/access.log ^
REM     --error-logfile logs/error.log ^
REM     --capture-output ^
REM     --log-level info ^
REM     --reload ^
REM     app:app ^

echo.
echo Server process exited.
endlocal
