#!/bin/bash

echo "========================================"
echo "Interview Video Generator - Linux Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ using your package manager"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[2/5] Virtual environment already exists"
fi

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[4/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if ffmpeg is installed
echo "[5/5] Checking ffmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "WARNING: ffmpeg is not installed"
    echo ""
    echo "Please install ffmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  Fedora/RHEL:   sudo dnf install ffmpeg"
    echo "  Arch:          sudo pacman -S ffmpeg"
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
echo "    source venv/bin/activate"
echo ""
echo "To run the server:"
echo "    uvicorn server:app --reload --host 0.0.0.0 --port 8001"
echo ""