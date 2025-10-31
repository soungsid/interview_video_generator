#!/bin/bash

echo "========================================"
echo "Interview Video Generator - Git Bash Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Checking Python version..."
python --version

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/5] Creating virtual environment..."
    python -m venv venv
else
    echo "[2/5] Virtual environment already exists"
fi

# Activate virtual environment (Git Bash on Windows)
echo "[3/5] Activating virtual environment..."
source venv/Scripts/activate

# Install dependencies
echo "[4/5] Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check if ffmpeg is installed
echo "[5/5] Checking ffmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "WARNING: ffmpeg is not installed or not in PATH"
    echo ""
    echo "Please install ffmpeg:"
    echo "1. Download from: https://github.com/BtbN/FFmpeg-Builds/releases"
    echo "2. Extract to a folder (e.g., C:\\ffmpeg)"
    echo "3. Add C:\\ffmpeg\\bin to your system PATH"
    echo ""
    echo "Alternatively, use Chocolatey:"
    echo "    choco install ffmpeg"
    echo ""
    echo "Or use winget:"
    echo "    winget install Gyan.FFmpeg"
    echo ""
else
    echo "ffmpeg is installed:"
    ffmpeg -version | head -n 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To activate the environment manually:"
echo "    cd backend"
echo "    source venv/Scripts/activate"
echo ""
echo "To run the server:"
echo "    uvicorn server:app --reload --host 0.0.0.0 --port 8001"
echo ""