# Environment Variables Guide

This document explains all environment variables used in the InterviewVideoGenerator API.

## Required Variables

### MongoDB Configuration

#### Using MongoDB Atlas (Recommended)

```bash
MONGO_USERNAME="your_mongodb_username"
MONGO_PASSWORD="your_mongodb_password"  
MONGO_CLUSTER="cluster0.xxxxx.mongodb.net"
MONGO_APP_NAME="Cluster0"
DB_NAME="interview_video_generator"
```

**How to get these values:**
1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a free cluster
3. Go to Database Access → Add New Database User
4. Copy username and password
5. Go to Database → Connect → Connect your application
6. Copy the connection string: `mongodb+srv://<username>:<password>@<cluster>/<dbname>`
7. Extract: `MONGO_CLUSTER` is `cluster0.xxxxx.mongodb.net`

#### Using Local MongoDB

```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="interview_video_generator"
```

### CORS Configuration

```bash
CORS_ORIGINS="*"
```

**Options:**
- `"*"` - Allow all origins (development only)
- `"http://localhost:3000"` - Specific origin
- `"http://localhost:3000,https://example.com"` - Multiple origins

### AI Configuration (DeepSeek)

```bash
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"
```

**How to get DeepSeek API key:**
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

**Available models:**
- `deepseek-chat` - General purpose chat model
- `deepseek-coder` - Code-focused model

---

## Optional Variables

### AWS Polly (Text-to-Speech)

Only needed if you plan to use AWS Polly for audio generation:

```bash
AWS_ACCESS_KEY_ID="your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_DEFAULT_REGION="us-east-1"
POLLY_VOICE_INTERVIEWER="Matthew"
POLLY_VOICE_CANDIDATE="Joanna"
```

**How to get AWS credentials:**
1. Sign up at [AWS Console](https://aws.amazon.com/)
2. Go to IAM → Users → Create User
3. Attach policy: `AmazonPollyFullAccess`
4. Create access key
5. Download credentials

**Available Polly voices:**
- English (US): Matthew, Joanna, Joey, Kendra, Kimberly
- English (GB): Amy, Emma, Brian
- See full list: [AWS Polly Voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

---

## Alternative AI Providers

### Using OpenAI

```bash
DEEPSEEK_API_KEY="sk-proj-xxxxxxxxxxxxxxxx"
DEEPSEEK_BASE_URL="https://api.openai.com/v1"
DEFAULT_AI_MODEL="gpt-4"
```

**Available OpenAI models:**
- `gpt-4` - Most capable model
- `gpt-4-turbo` - Faster GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective

**Get API key:** [OpenAI Platform](https://platform.openai.com/api-keys)

### Using Anthropic Claude

```bash
DEEPSEEK_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"
DEEPSEEK_BASE_URL="https://api.anthropic.com/v1"
DEFAULT_AI_MODEL="claude-3-opus-20240229"
```

**Available Claude models:**
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest

**Get API key:** [Anthropic Console](https://console.anthropic.com/)

### Using Azure OpenAI

```bash
DEEPSEEK_API_KEY="your-azure-api-key"
DEEPSEEK_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
DEFAULT_AI_MODEL="gpt-4"
```

---

## Environment File Setup

### For Local Development

1. Navigate to backend folder:
```bash
cd backend
```

2. Copy example file:
```bash
cp .env.example .env
```

3. Edit `.env` with your values:
```bash
# Windows
notepad .env

# Linux/Mac
nano .env
# or
vim .env
```

### For Docker

When using Docker Compose, the `.env` file is automatically loaded from `backend/.env`.

When using Docker directly:
```bash
docker run --env-file backend/.env ...
```

### For Production

**Never commit `.env` files to version control!**

Use one of these approaches:

#### 1. Environment Variables (Recommended)
```bash
export MONGO_USERNAME="username"
export DEEPSEEK_API_KEY="sk-xxx"
# ... etc
```

#### 2. Docker Secrets
```bash
echo "sk-xxxxx" | docker secret create deepseek_api_key -
```

#### 3. CI/CD Secrets
- GitHub Actions: Settings → Secrets and variables → Actions
- GitLab CI: Settings → CI/CD → Variables
- Azure DevOps: Pipelines → Library → Variable groups

---

## Security Best Practices

### ✅ DO

1. **Use strong, unique API keys**
2. **Rotate keys regularly**
3. **Use environment variables or secrets managers**
4. **Restrict MongoDB IP allowlist** (Atlas)
5. **Use different keys for dev/staging/prod**
6. **Enable MFA on cloud accounts**

### ❌ DON'T

1. **Never commit `.env` files to Git**
2. **Never hardcode credentials in code**
3. **Never share API keys in chat/email**
4. **Never use production keys in development**
5. **Never log sensitive values**

---

## Validation

### Check if variables are loaded:

**Python:**
```python
import os
print(os.environ.get('DEEPSEEK_API_KEY'))  # Should show your key
print(os.environ.get('MONGO_USERNAME'))     # Should show username
```

**Docker:**
```bash
docker exec -it interview-video-generator env | grep DEEPSEEK
```

### Test MongoDB connection:

```python
from config.database import get_database
db = get_database()
print(db.list_collection_names())  # Should connect successfully
```

### Test AI API:

```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test", "num_questions": 1}'
```

---

## Troubleshooting

### Error: "Missing required environment variable"

**Solution:** Ensure `.env` file exists in `backend/` folder with required variables.

### Error: "Authentication failed" (MongoDB)

**Solution:** 
1. Check username/password are correct
2. Verify MongoDB Atlas IP allowlist includes your IP
3. Test connection string manually

### Error: "Invalid API key" (DeepSeek/OpenAI)

**Solution:**
1. Verify key starts with correct prefix (`sk-` for most providers)
2. Check key is active on provider's dashboard
3. Ensure no extra spaces in `.env` file

### Docker: Environment variables not loaded

**Solution:**
1. Verify `.env` file path: `backend/.env`
2. Check docker-compose.yml references correct env_file
3. Restart containers: `docker-compose down && docker-compose up -d`

---

## Example `.env` File

```bash
# MongoDB Atlas Configuration
MONGO_USERNAME="myuser"
MONGO_PASSWORD="MySecurePassword123"
MONGO_CLUSTER="cluster0.abcde.mongodb.net"
MONGO_APP_NAME="Cluster0"
DB_NAME="interview_video_generator"
CORS_ORIGINS="*"

# AI Configuration
DEEPSEEK_API_KEY="sk-1234567890abcdef1234567890abcdef"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"

# AWS Polly (Optional)
AWS_ACCESS_KEY_ID="AKIA1234567890EXAMPLE"
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_DEFAULT_REGION="us-east-1"
POLLY_VOICE_INTERVIEWER="Matthew"
POLLY_VOICE_CANDIDATE="Joanna"
```

---

## Need Help?

- Review the main [README.md](README.md)
- Check [QUICKSTART.md](QUICKSTART.md)
- Visit your provider's documentation:
  - [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
  - [DeepSeek API Docs](https://platform.deepseek.com/docs)
  - [OpenAI API Docs](https://platform.openai.com/docs)
  - [AWS Polly Docs](https://docs.aws.amazon.com/polly/)
