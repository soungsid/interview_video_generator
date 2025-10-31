# Quick Start Guide

Choose your preferred setup method:

## 🐳 Docker (Recommended)

**Fastest way to get started - works on all platforms!**

```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd interview-video-generator

# 2. Configure environment
# Edit backend/.env with your credentials

# 3. Start with Docker Compose
docker-compose up -d

# 4. Access API
# Open http://localhost:8001/docs
```

**That's it!** FFmpeg and all dependencies are included.

---

## 💻 Local Development (Windows + VS Code)

**For active development with debugging**

### Quick Setup

```cmd
# Run the setup script
setup-windows.bat
```

**Manual steps:**
1. Install FFmpeg (see [VSCODE_SETUP.md](VSCODE_SETUP.md))
2. Create virtual environment: `python -m venv backend/venv`
3. Activate: `backend\venv\Scripts\activate.bat`
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Configure `backend/.env`
6. Run: `uvicorn server:app --reload --host 0.0.0.0 --port 8001`

### VS Code Integration

Open project in VS Code:
```cmd
code .
```

- Virtual environment auto-activates
- Press `F5` to debug
- See [VSCODE_SETUP.md](VSCODE_SETUP.md) for details

---

## 🐧 Linux/macOS

### Quick Setup

```bash
# Run the setup script
chmod +x setup-linux.sh
./setup-linux.sh
```

**Manual steps:**
1. Install FFmpeg: `sudo apt-get install ffmpeg` (Ubuntu/Debian)
2. Create venv: `python3 -m venv backend/venv`
3. Activate: `source backend/venv/bin/activate`
4. Install: `pip install -r backend/requirements.txt`
5. Configure `backend/.env`
6. Run: `uvicorn server:app --reload --host 0.0.0.0 --port 8001`

---

## 🚀 GitHub Actions (CI/CD)

Push Docker images automatically:

```bash
# Push to main branch (triggers build)
git push origin main

# Or create a version tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Images are published to: `ghcr.io/<your-username>/interview-video-generator`

---

## 📚 Documentation

- **Full Setup Guide**: [README.md](README.md)
- **Docker Guide**: [DOCKER.md](DOCKER.md)
- **VS Code Setup**: [VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ✅ Verify Installation

### Test FFmpeg
```bash
ffmpeg -version
```

### Test API
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Docker Basics",
    "num_questions": 2
  }'
```

### Access Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

---

## 🆘 Need Help?

1. Check [README.md](README.md) troubleshooting section
2. Review platform-specific guides
3. Check GitHub Issues

---

## 🎯 Quick Commands Reference

### Docker
```bash
docker-compose up -d              # Start
docker-compose logs -f backend    # View logs
docker-compose down               # Stop
docker-compose up -d --build      # Rebuild
```

### Local Development
```bash
# Activate venv
source backend/venv/bin/activate  # Linux/Mac
backend\venv\Scripts\activate     # Windows

# Run server
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Run tests
pytest backend/tests/
```

### Docker Registry
```bash
# Pull image
docker pull ghcr.io/<username>/interview-video-generator:latest

# Build and push
docker build -t interview-video-generator:latest backend/
docker tag interview-video-generator:latest ghcr.io/<username>/interview-video-generator:latest
docker push ghcr.io/<username>/interview-video-generator:latest
```
