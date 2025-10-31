# VS Code Development Setup for Windows

This guide helps you set up your local development environment with Visual Studio Code on Windows.

## Prerequisites

- ✅ Python 3.11+ installed
- ✅ Visual Studio Code installed
- ✅ Git (optional, for Git Bash)

## Quick Setup

### Option 1: Automated Setup (CMD)

```cmd
setup-windows.bat
```

### Option 2: Automated Setup (Git Bash)

```bash
./setup-gitbash.sh
```

### Option 3: Manual Setup

See detailed steps below.

## Detailed Manual Setup

### 1. Install FFmpeg

FFmpeg is required for audio processing capabilities.

#### Method A: Chocolatey (Recommended)

```cmd
choco install ffmpeg
```

#### Method B: winget

```cmd
winget install Gyan.FFmpeg
```

#### Method C: Manual Installation

1. Download FFmpeg: https://github.com/BtbN/FFmpeg-Builds/releases
2. Extract to `C:\ffmpeg` (or your preferred location)
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit `Path` under System variables
   - Add new entry: `C:\ffmpeg\bin`
   - Click OK and restart terminal

### 2. Set Up Python Virtual Environment

Open terminal in project root:

**CMD:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

**Git Bash:**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**PowerShell:**
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env` in the `backend` folder
2. Update with your credentials:
   - MongoDB credentials
   - DeepSeek API key
   - AWS credentials (optional)

### 4. Open Project in VS Code

```cmd
code .
```

## VS Code Configuration

The project includes pre-configured VS Code settings in `.vscode/`:

### Auto-activation of Virtual Environment

The virtual environment will automatically activate when you:
- Open a new terminal in VS Code
- Start debugging

Configuration in `.vscode/settings.json`:
- Python interpreter points to `backend/venv/Scripts/python.exe`
- Terminal automatically activates venv

### Recommended Extensions

VS Code will suggest installing these extensions (see `.vscode/extensions.json`):

1. **Python** - Python language support
2. **Pylance** - Fast Python language server
3. **Black Formatter** - Code formatting
4. **Flake8** - Linting
5. **Docker** - Docker support
6. **YAML** - YAML language support
7. **Code Spell Checker** - Spell checking

Install all recommended extensions:
1. Press `Ctrl+Shift+P`
2. Type "Show Recommended Extensions"
3. Click "Install All"

### Debugging Configuration

Debug configuration is pre-configured in `.vscode/launch.json`.

**To start debugging:**
1. Press `F5` or click Run → Start Debugging
2. Select "Python: FastAPI" configuration
3. Set breakpoints in your code
4. The API will start at `http://localhost:8001`

### Code Formatting

- **Format on Save** is enabled
- **Black** is configured as the default formatter
- Imports are automatically organized

## Verify Installation

### 1. Check Python Virtual Environment

Open a new terminal in VS Code and verify:

```cmd
python --version
# Should show Python 3.11+

pip list | findstr fastapi
# Should show fastapi version
```

### 2. Check FFmpeg

```cmd
ffmpeg -version
# Should show ffmpeg version and configuration
```

### 3. Run the Application

```cmd
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Open browser to: `http://localhost:8001/docs`

## Common Issues

### Virtual Environment Not Activating

**Solution 1:** Reload VS Code window
- Press `Ctrl+Shift+P`
- Type "Developer: Reload Window"

**Solution 2:** Select Python interpreter manually
- Press `Ctrl+Shift+P`
- Type "Python: Select Interpreter"
- Choose `.\backend\venv\Scripts\python.exe`

### FFmpeg Not Found

**Error:** `'ffmpeg' is not recognized as an internal or external command`

**Solution:**
1. Verify FFmpeg is installed: `where ffmpeg`
2. If not found, install using one of the methods above
3. Restart VS Code after PATH changes
4. Open new terminal in VS Code

### PowerShell Execution Policy Error

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Import Errors in VS Code

**Error:** Red underlines on imports even though code runs

**Solution:**
1. Ensure Pylance extension is installed
2. Check Python interpreter is set to venv
3. Reload VS Code window

## Terminal Options

VS Code supports multiple terminal types on Windows:

### CMD (Default)
```cmd
cd backend
venv\Scripts\activate.bat
```

### PowerShell
```powershell
cd backend
venv\Scripts\Activate.ps1
```

### Git Bash
```bash
cd backend
source venv/Scripts/activate
```

Change default terminal:
1. Press `Ctrl+Shift+P`
2. Type "Terminal: Select Default Profile"
3. Choose your preferred terminal

## Keyboard Shortcuts

Useful VS Code shortcuts for Python development:

- `F5` - Start debugging
- `Ctrl+Shift+P` - Command palette
- `Ctrl+`` - Toggle terminal
- `Ctrl+Shift+`` - New terminal
- `Shift+Alt+F` - Format document
- `F12` - Go to definition
- `Ctrl+.` - Quick fix
- `Ctrl+Space` - Trigger suggestions

## Running Tests

Run tests from VS Code terminal:

```cmd
cd backend
pytest tests/
```

Or use VS Code's Testing panel:
1. Click Testing icon in sidebar
2. Click "Configure Python Tests"
3. Select pytest
4. Tests will appear in Testing panel

## Next Steps

1. Review the API documentation at `http://localhost:8001/docs`
2. Check [README.md](README.md) for API usage
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for code structure
4. Start developing!

## Getting Help

If you encounter issues:
1. Check this document's "Common Issues" section
2. Review the main [README.md](README.md)
3. Check the project's GitHub issues

## Additional Resources

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
