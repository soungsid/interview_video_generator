@echo off
echo ======================================
echo Environment Verification
echo ======================================
echo.

set ERRORS=0

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   FAIL: Python not found
    set /a ERRORS+=1
) else (
    python --version
    echo   OK: Python installed
)
echo.

echo [2/5] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo   FAIL: FFmpeg not found
    echo   Install: choco install ffmpeg
    set /a ERRORS+=1
) else (
    ffmpeg -version | findstr "ffmpeg version"
    echo   OK: FFmpeg installed
)
echo.

echo [3/5] Checking Virtual Environment...
if exist "backend\venv\Scripts\python.exe" (
    echo   OK: Virtual environment exists at backend\venv
) else (
    echo   FAIL: Virtual environment not found
    echo   Run: cd backend ^&^& python -m venv venv
    set /a ERRORS+=1
)
echo.

echo [4/5] Checking Environment File...
if exist "backend\.env" (
    echo   OK: .env file exists
) else (
    echo   WARN: .env file not found
    echo   Copy: backend\.env.example to backend\.env
    set /a ERRORS+=1
)
echo.

echo [5/5] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo   WARN: Docker not installed (optional)
    echo   Install from: https://www.docker.com/products/docker-desktop
) else (
    docker --version
    echo   OK: Docker installed
)
echo.

echo ======================================
if %ERRORS% EQU 0 (
    echo Result: All checks passed!
    echo You can start developing.
) else (
    echo Result: %ERRORS% error(s) found
    echo Please fix the issues above
)
echo ======================================
echo.

echo Next steps:
echo   1. Activate venv: backend\venv\Scripts\activate
echo   2. Install deps: pip install -r backend\requirements.txt
echo   3. Configure: Edit backend\.env
echo   4. Run server: uvicorn server:app --reload
echo.
pause
