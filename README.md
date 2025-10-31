# InterviewVideoGenerator API

A FastAPI-based REST API that generates simulated YouTube interview video scripts using AI. The system creates realistic technical interview conversations with conversation memory, where a YouTuber interviewer asks questions and a candidate provides answers.

## Features

- **AI-Powered Script Generation**: Uses DeepSeek (or other OpenAI-compatible models) to generate engaging interview content
- **Conversation Memory**: Both the interviewer and candidate remember previous exchanges for coherent, progressive discussions
- **Flexible Model Support**: Easily switch between different AI models through configuration or API parameters
- **MongoDB Persistence**: Stores complete video scripts and dialogues
- **RESTful API**: Clean endpoints for generation and retrieval
- **Production-Ready**: Clean architecture with service layers, logging, and error handling

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

### Prerequisites
- Python 3.11+
- MongoDB
- DeepSeek API key (or other OpenAI-compatible API)

### Environment Variables

Create `/app/backend/.env`:
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="interview_video_generator"
CORS_ORIGINS="*"

# AI Configuration
DEEPSEEK_API_KEY="your-api-key-here"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"
```

### Install Dependencies
```bash
cd /app/backend
pip install -r requirements.txt
```

### Run the API
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
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
/app/backend/
├── api/                      # API Layer (routes)
│   ├── __init__.py
│   └── routes.py            # REST endpoints
├── clients/                  # External clients
│   ├── __init__.py
│   └── ai_client.py         # LLM client (DeepSeek, OpenAI, etc.)
├── config/                   # Configuration
│   ├── __init__.py
│   ├── database.py          # MongoDB connection
│   └── dependencies.py      # Dependency injection
├── entities/                 # Data models (Pydantic)
│   ├── __init__.py
│   ├── dialogue.py          # Dialogue & Role models
│   ├── requests.py          # Request DTOs
│   └── video.py            # Video models
├── services/                 # Business logic
│   ├── __init__.py
│   ├── script_generation_service.py  # Script generation
│   └── video_service.py     # Video persistence
├── server.py                # Application entry point
├── .env                     # Environment configuration
├── .env.example             # Environment template
└── requirements.txt         # Python dependencies
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

- **API Key Security**: Store API keys in environment variables, never in code
- **Rate Limiting**: Consider adding rate limiting for the generation endpoint
- **Caching**: Cache generated scripts if regenerating the same topic
- **Monitoring**: Use logging to track API usage and AI token consumption
- **Database Indexing**: Add indexes on video_id and created_at for faster queries

## Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## License

This project is for demonstration purposes.
