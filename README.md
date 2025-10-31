# InterviewVideoGenerator API

A FastAPI-based REST API that generates simulated YouTube interview video scripts using AI. The system creates realistic technical interview conversations with conversation memory, where a YouTuber interviewer asks questions and a candidate provides answers.

## Features

- **AI-Powered Script Generation**: Uses DeepSeek (or other OpenAI-compatible models) to generate engaging interview content
- **Conversation Memory**: Both the interviewer and candidate remember previous exchanges for coherent, progressive discussions
- **Flexible Model Support**: Easily switch between different AI models through configuration or API parameters
- **MongoDB Persistence**: Stores complete video scripts and dialogues
- **RESTful API**: Clean endpoints for generation and retrieval
- **Production-Ready**: Clean architecture with service layers, logging, and error handling
- **FFmpeg Support**: Audio processing capabilities for future TTS integration
- **Docker Support**: Fully containerized with Docker and Docker Compose
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Endpoints (/api)                    │   │
│  │  - POST /videos/generate                             │   │
│  │  - GET  /videos/{id}                                 │   │
│  │  - GET  /videos                                      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │ ScriptGenerationService                     │     │   │
│  │  │  - Orchestrates script generation           │     │   │
│  │  │  - Maintains conversation memory            │     │   │
│  │  │  - Generates intro, dialogues, conclusion   │     │   │
│  │  └────────┬────────────────────────────────────┘     │   │
│  │           │                                           │   │
│  │  ┌────────▼─────────────┐  ┌────────────────────┐   │   │
│  │  │ AIService             │  │ VideoService       │   │   │
│  │  │  - DeepSeek/OpenAI   │  │  - MongoDB ops     │   │   │
│  │  │  - Model switching    │  │  - CRUD operations │   │   │
│  │  └──────────────────────┘  └────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   MongoDB     │
                    │  - videos     │
                    │  - dialogues  │
                    └───────────────┘
```

## Database Schema

### Videos Collection
```javascript
{
  id: UUID,
  title: String,
  topic: String,
  introduction: TEXT,
  conclusion: TEXT,
  created_at: ISO datetime
}
```

### Dialogues Collection
```javascript
{
  id: UUID,
  role: "YOUTUBER" | "CANDIDATE",
  text: TEXT,
  question_number: Integer,
  video_id: UUID (references Video)
}
```

## API Endpoints

### 1. Generate Video Script
**POST** `/api/videos/generate`

Generates a complete interview video script with conversation memory.

**Request Body:**
```json
{
  "topic": "Spring Boot Security",
  "num_questions": 5,
  "model": "deepseek-chat"  // optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Simulated Interview: Spring Boot Security",
  "topic": "Spring Boot Security",
  "introduction": "Welcome back! Today we'll test...",
  "conclusion": "That's it for today's interview...",
  "created_at": "2025-10-31T02:22:45.718625Z",
  "dialogues": [
    {
      "id": "uuid",
      "role": "YOUTUBER",
      "text": "Can you explain how Spring Security handles authentication?",
      "question_number": 1
    },
    {
      "id": "uuid",
      "role": "CANDIDATE",
      "text": "Spring Security uses a chain of filters...",
      "question_number": 1
    }
  ]
}
```

### 2. Get Video by ID
**GET** `/api/videos/{video_id}`

Retrieves a specific video with all its dialogues.

**Response:** Same as generate endpoint

### 3. List All Videos
**GET** `/api/videos`

Lists all generated videos (without dialogues), sorted by creation date.

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Simulated Interview: Spring Boot Security",
    "topic": "Spring Boot Security",
    "introduction": "...",
    "conclusion": "...",
    "created_at": "2025-10-31T02:22:45.718625Z"
  }
]
```

### 4. Health Check
**GET** `/api/`

Returns API status.

## Installation & Setup

You can run this application in three ways:
1. **🐳 Docker** (Recommended - Cross-platform, includes ffmpeg)
2. **💻 Local Development** (Windows with VS Code)
3. **🐧 Native Installation** (Linux/macOS)

---

## 🐳 Docker Installation (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- MongoDB Atlas account (or local MongoDB)
- DeepSeek API key

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd interview-video-generator
```

2. **Configure environment variables**

Copy the `.env` file in the backend folder and update with your credentials:
```bash
# MongoDB Atlas Configuration
MONGO_USERNAME="your_username"
MONGO_PASSWORD="your_password"
MONGO_CLUSTER="cluster0.xxxxx.mongodb.net"
MONGO_APP_NAME="Cluster0"
DB_NAME="interview_video_generator"
CORS_ORIGINS="*"

# AI Configuration
DEEPSEEK_API_KEY="your-api-key-here"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"

# AWS Polly Configuration (optional)
AWS_ACCESS_KEY_ID="your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_DEFAULT_REGION="us-east-1"
```

3. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8001`

4. **View logs**
```bash
docker-compose logs -f backend
```

5. **Stop the application**
```bash
docker-compose down
```

### Using Pre-built Docker Image from GitHub Registry

1. **Pull the image**
```bash
docker pull ghcr.io/<your-github-username>/interview-video-generator:latest
```

2. **Run the container**
```bash
docker run -d \
  --name interview-video-generator \
  -p 8001:8001 \
  --env-file backend/.env \
  -v $(pwd)/backend/audio_files:/app/audio_files \
  ghcr.io/<your-github-username>/interview-video-generator:latest
```

### Building and Pushing Your Own Docker Image

1. **Build the image**
```bash
cd backend
docker build -t interview-video-generator:latest .
```

2. **Tag for GitHub Container Registry**
```bash
docker tag interview-video-generator:latest ghcr.io/<your-github-username>/interview-video-generator:latest
```

3. **Login to GitHub Container Registry**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <your-github-username> --password-stdin
```

4. **Push to registry**
```bash
docker push ghcr.io/<your-github-username>/interview-video-generator:latest
```

### Automated Build with GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds and pushes the Docker image when you push to `main` branch or create a tag.

The workflow file is located at `.github/workflows/docker-build-push.yml`

**To trigger automatic build:**
```bash
git push origin main
# or create a version tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 💻 Local Development Setup (Windows with VS Code)

### Prerequisites
- Python 3.11+
- Visual Studio Code
- MongoDB Atlas account or local MongoDB
- DeepSeek API key

### Automated Setup

#### For Windows (CMD):
```cmd
setup-windows.bat
```

#### For Git Bash:
```bash
./setup-gitbash.sh
```

### Manual Setup

1. **Install FFmpeg on Windows**

**Option 1: Using Chocolatey (Recommended)**
```cmd
choco install ffmpeg
```

**Option 2: Using winget**
```cmd
winget install Gyan.FFmpeg
```

**Option 3: Manual Installation**
- Download from: https://github.com/BtbN/FFmpeg-Builds/releases
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to your system PATH

2. **Create virtual environment**
```cmd
cd backend
python -m venv venv
```

3. **Activate virtual environment**

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

4. **Install Python dependencies**
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configure environment variables**

Create `backend/.env` with your credentials (see Docker section for format)

6. **Run the API**
```cmd
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### VS Code Integration

The repository includes VS Code configuration that automatically:
- Activates the virtual environment when opening a terminal
- Configures Python interpreter
- Sets up debugging for FastAPI
- Provides recommended extensions

**Recommended Extensions** (will be suggested automatically):
- Python
- Pylance
- Black Formatter
- Flake8
- Docker
- YAML

**To debug in VS Code:**
1. Open the project folder in VS Code
2. Press `F5` or go to Run → Start Debugging
3. Select "Python: FastAPI" configuration

---

## 🐧 Native Installation (Linux/macOS)

### Automated Setup

```bash
chmod +x setup-linux.sh
./setup-linux.sh
```

### Manual Setup

1. **Install FFmpeg**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Fedora/RHEL:**
```bash
sudo dnf install ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

2. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
```

3. **Activate virtual environment**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configure environment**

Create `backend/.env` with your credentials

6. **Run the API**
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at `http://localhost:8001`

## Model Configuration

### Switching AI Models

The API is designed to be model-agnostic. You can switch models in three ways:

#### 1. Default Model (Environment Variable)
Set in `.env`:
```bash
DEFAULT_AI_MODEL="deepseek-chat"
```

#### 2. Per-Request Model
Pass model parameter in the API request:
```json
{
  "topic": "Kubernetes",
  "num_questions": 3,
  "model": "gpt-4"
}
```

#### 3. Different Providers

To use OpenAI instead of DeepSeek:
```bash
DEEPSEEK_API_KEY="sk-your-openai-key"
DEEPSEEK_BASE_URL="https://api.openai.com/v1"
DEFAULT_AI_MODEL="gpt-4"
```

To use other OpenAI-compatible providers:
```bash
DEEPSEEK_API_KEY="your-api-key"
DEEPSEEK_BASE_URL="https://your-provider.com/v1"
DEFAULT_AI_MODEL="provider-model-name"
```

## Conversation Memory

The system maintains full conversation memory throughout script generation:

1. **System Prompt**: Sets the context for both YOUTUBER and CANDIDATE personas
2. **Question Generation**: The YouTuber can reference and follow up on previous answers
3. **Answer Generation**: The candidate remembers and builds upon previous topics
4. **Progressive Difficulty**: Questions naturally become more challenging based on previous answers

### Example Conversation Flow
```
Q1: "What are the benefits of async Python?"
A1: "Async provides performance benefits for I/O-bound operations..."

Q2: "You mentioned async handling I/O - how does the event loop work?"
   ↑ (References previous answer)

A2: "When FastAPI encounters await, it yields control to the event loop..."

Q3: "That's a great explanation. What pitfalls should developers watch out for?"
   ↑ (Acknowledges previous context)
```

## Logging

All conversation flows are logged to the console for debugging:

```
================================================================================
CONVERSATION START: FastAPI and Async Python
================================================================================

[Question 1] YOUTUBER: What are the key benefits...
[Answer 1] CANDIDATE: FastAPI's async support provides...

[Question 2] YOUTUBER: You mentioned async handling...
[Answer 2] CANDIDATE: When FastAPI encounters an async function...

================================================================================
CONVERSATION END
================================================================================
```

## Testing

### Test Video Generation
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Docker and Containerization",
    "num_questions": 3
  }'
```

### Test Retrieval
```bash
# List all videos
curl http://localhost:8001/api/videos

# Get specific video
curl http://localhost:8001/api/videos/{video_id}
```

### Test Different Models
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "GraphQL vs REST",
    "num_questions": 4,
    "model": "gpt-4"
  }'
```

## Code Structure

```
/app/
├── backend/                      # Backend application
│   ├── api/                      # API Layer (routes)
│   │   ├── __init__.py
│   │   └── routes.py            # REST endpoints
│   ├── clients/                  # External clients
│   │   ├── __init__.py
│   │   └── ai_client.py         # LLM client (DeepSeek, OpenAI, etc.)
│   ├── config/                   # Configuration
│   │   ├── __init__.py
│   │   ├── database.py          # MongoDB connection
│   │   └── dependencies.py      # Dependency injection
│   ├── entities/                 # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── dialogue.py          # Dialogue & Role models
│   │   ├── requests.py          # Request DTOs
│   │   └── video.py            # Video models
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── script_generation_service.py  # Script generation
│   │   └── video_service.py     # Video persistence
│   ├── audio_files/             # Generated audio files
│   ├── server.py                # Application entry point
│   ├── Dockerfile               # Docker image definition
│   ├── .dockerignore            # Docker ignore patterns
│   ├── .env                     # Environment configuration
│   └── requirements.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── docker-build-push.yml # GitHub Actions CI/CD
├── .vscode/                     # VS Code configuration
│   ├── settings.json            # Editor settings
│   ├── launch.json              # Debug configuration
│   └── extensions.json          # Recommended extensions
├── docker-compose.yml           # Docker Compose configuration
├── setup-windows.bat            # Windows setup script
├── setup-linux.sh               # Linux setup script
├── setup-gitbash.sh             # Git Bash setup script
└── README.md                    # This file
```

**Architecture Pattern**: Layered architecture with dependency injection
- **API Layer** (`api/`): HTTP routing and request handling
- **Service Layer** (`services/`): Business logic and orchestration
- **Client Layer** (`clients/`): External API communication
- **Entity Layer** (`entities/`): Data models and validation
- **Config Layer** (`config/`): Configuration and dependencies

See [STRUCTURE.md](/app/STRUCTURE.md) for detailed architecture documentation.

## Future Enhancements

The codebase is prepared for future audio generation:

1. Add TTS integration endpoint
2. Generate audio files from dialogue text
3. Store audio URLs in Video model
4. Support multiple voices for YOUTUBER and CANDIDATE

## Error Handling

The API includes comprehensive error handling:

- **500**: AI generation errors (API issues, network problems)
- **404**: Video not found
- **422**: Validation errors (invalid num_questions, missing fields)

All errors include detailed messages for debugging.

## Production Considerations

### Docker in Production

When deploying the Docker container in production:

1. **Use specific version tags** instead of `latest`
```bash
docker pull ghcr.io/<your-username>/interview-video-generator:v1.0.0
```

2. **Use Docker secrets for sensitive data**
```bash
docker secret create deepseek_api_key /path/to/key/file
```

3. **Enable health checks** (already configured in Dockerfile)

4. **Use volume mounts for persistent data**
```bash
docker run -v /host/audio:/app/audio_files ...
```

5. **Configure resource limits**
```bash
docker run --memory="2g" --cpus="2" ...
```

### General Best Practices

- **API Key Security**: Store API keys in environment variables or secrets manager, never in code
- **Rate Limiting**: Consider adding rate limiting for the generation endpoint
- **Caching**: Cache generated scripts if regenerating the same topic
- **Monitoring**: Use logging to track API usage and AI token consumption
- **Database Indexing**: Add indexes on video_id and created_at for faster queries
- **FFmpeg**: Ensure ffmpeg is available (included in Docker image)

## Troubleshooting

### FFmpeg Issues

**Docker:** FFmpeg is pre-installed in the Docker image, no action needed.

**Windows:** If ffmpeg command not found:
1. Verify installation: `ffmpeg -version`
2. Check PATH includes ffmpeg bin directory
3. Restart terminal/VS Code after PATH changes

**Linux/macOS:** Install via package manager (see setup scripts)

### VS Code Virtual Environment Not Activating

1. Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Check `.vscode/settings.json` exists
3. Verify `python.defaultInterpreterPath` points to venv

### Docker Build Issues

**Error: "Cannot connect to MongoDB"**
- Ensure `.env` file has correct MongoDB credentials
- Check MongoDB Atlas allows connections from your IP

**Error: "Permission denied"**
- On Linux, add user to docker group: `sudo usermod -aG docker $USER`
- Logout and login again

### GitHub Container Registry

**Error: "unauthorized: authentication required"**
```bash
# Create personal access token with packages:read and packages:write
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin
```

## Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [ARCHITECTURE.md](/app/ARCHITECTURE.md) for detailed design
3. Check GitHub Issues

## License

This project is for demonstration purposes.
