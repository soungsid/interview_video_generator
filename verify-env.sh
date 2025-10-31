#!/bin/bash

echo "======================================"
echo "Environment Verification"
echo "======================================"
echo ""

ERRORS=0

echo "[1/5] Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo "  ✅ OK: Python installed"
else
    echo "  ❌ FAIL: Python not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[2/5] Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -n 1
    echo "  ✅ OK: FFmpeg installed"
else
    echo "  ❌ FAIL: FFmpeg not found"
    echo "  Install: sudo apt-get install ffmpeg (Ubuntu/Debian)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[3/5] Checking Virtual Environment..."
if [ -f "backend/venv/bin/python" ]; then
    echo "  ✅ OK: Virtual environment exists at backend/venv"
else
    echo "  ❌ FAIL: Virtual environment not found"
    echo "  Run: cd backend && python3 -m venv venv"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[4/5] Checking Environment File..."
if [ -f "backend/.env" ]; then
    echo "  ✅ OK: .env file exists"
else
    echo "  ⚠️  WARN: .env file not found"
    echo "  Copy: backend/.env.example to backend/.env"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "[5/5] Checking Docker..."
if command -v docker &> /dev/null; then
    docker --version
    echo "  ✅ OK: Docker installed"
else
    echo "  ⚠️  WARN: Docker not installed (optional)"
    echo "  Install from: https://docs.docker.com/get-docker/"
fi
echo ""

echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Result: All checks passed!"
    echo "You can start developing."
else
    echo "❌ Result: $ERRORS error(s) found"
    echo "Please fix the issues above"
fi
echo "======================================"
echo ""

echo "Next steps:"
echo "  1. Activate venv: source backend/venv/bin/activate"
echo "  2. Install deps: pip install -r backend/requirements.txt"
echo "  3. Configure: Edit backend/.env"
echo "  4. Run server: uvicorn server:app --reload"
echo ""
