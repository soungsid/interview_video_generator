@echo off
echo ======================================
echo Testing Docker Build
echo ======================================
echo.

cd /d "%~dp0backend"

echo [1/3] Building Docker image...
docker build -t interview-video-generator:test .

if errorlevel 1 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Verifying FFmpeg installation in image...
docker run --rm interview-video-generator:test ffmpeg -version

if errorlevel 1 (
    echo ERROR: FFmpeg not found in Docker image!
    pause
    exit /b 1
)

echo.
echo [3/3] Checking Python packages...
docker run --rm interview-video-generator:test pip list | findstr "fastapi pymongo openai"

echo.
echo ======================================
echo Docker build test completed successfully!
echo ======================================
echo.
echo To run the container:
echo   docker-compose up -d
echo.
echo To clean up test image:
echo   docker rmi interview-video-generator:test
echo.
pause
