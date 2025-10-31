@echo off
echo ========================================
echo Interview Video Generator - Windows Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

:: Navigate to backend directory
cd /d "%~dp0backend"

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/5] Virtual environment already exists
)

:: Activate virtual environment and install dependencies
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/5] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Check if ffmpeg is installed
echo [5/5] Checking ffmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: ffmpeg is not installed or not in PATH
    echo.
    echo Please install ffmpeg:
    echo 1. Download from: https://github.com/BtbN/FFmpeg-Builds/releases
    echo 2. Extract to a folder (e.g., C:\ffmpeg)
    echo 3. Add C:\ffmpeg\bin to your system PATH
    echo.
    echo Alternatively, use Chocolatey:
    echo    choco install ffmpeg
    echo.
    echo Or use winget:
    echo    winget install Gyan.FFmpeg
    echo.
) else (
    echo ffmpeg is installed:
    ffmpeg -version | findstr "ffmpeg version"
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To activate the environment manually:
echo    cd backend
echo    venv\Scripts\activate
echo.
echo To run the server:
echo    uvicorn server:app --reload --host 0.0.0.0 --port 8001
echo.
pause