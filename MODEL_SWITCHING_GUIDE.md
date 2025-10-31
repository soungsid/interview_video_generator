# Model Switching Guide

## Overview
The InterviewVideoGenerator API is designed to be model-agnostic and works with any OpenAI-compatible API. This guide shows you how to easily switch between different AI providers.

## Configuration Options

### 1. DeepSeek (Default)
```bash
# .env configuration
DEEPSEEK_API_KEY="sk-your-deepseek-key"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"
```

**Test:**
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Docker", "num_questions": 2}'
```

### 2. OpenAI GPT-4
```bash
# .env configuration
DEEPSEEK_API_KEY="sk-your-openai-key"
DEEPSEEK_BASE_URL="https://api.openai.com/v1"
DEFAULT_AI_MODEL="gpt-4"
```

**Test:**
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Kubernetes", "num_questions": 2}'
```

### 3. OpenAI GPT-3.5-turbo (Faster, Cheaper)
```bash
# .env configuration
DEEPSEEK_API_KEY="sk-your-openai-key"
DEEPSEEK_BASE_URL="https://api.openai.com/v1"
DEFAULT_AI_MODEL="gpt-3.5-turbo"
```

### 4. Azure OpenAI
```bash
# .env configuration
DEEPSEEK_API_KEY="your-azure-key"
DEEPSEEK_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
DEFAULT_AI_MODEL="gpt-4"
```

### 5. Other OpenAI-Compatible Providers

Many providers offer OpenAI-compatible APIs:

#### Together.ai
```bash
DEEPSEEK_API_KEY="your-together-key"
DEEPSEEK_BASE_URL="https://api.together.xyz/v1"
DEFAULT_AI_MODEL="mistralai/Mixtral-8x7B-Instruct-v0.1"
```

#### Anyscale
```bash
DEEPSEEK_API_KEY="your-anyscale-key"
DEEPSEEK_BASE_URL="https://api.endpoints.anyscale.com/v1"
DEFAULT_AI_MODEL="meta-llama/Llama-2-70b-chat-hf"
```

#### Perplexity
```bash
DEEPSEEK_API_KEY="your-perplexity-key"
DEEPSEEK_BASE_URL="https://api.perplexity.ai"
DEFAULT_AI_MODEL="llama-3-sonar-large-32k-online"
```

## Runtime Model Switching

You can override the default model on a per-request basis:

```bash
# Generate with a specific model
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "GraphQL",
    "num_questions": 3,
    "model": "gpt-4-turbo-preview"
  }'
```

## Model Selection Strategy

### For Production
- **GPT-4**: Best quality, most coherent conversations
- **DeepSeek**: Good balance of quality and cost
- **GPT-3.5-turbo**: Fastest, most cost-effective

### For Development/Testing
- **GPT-3.5-turbo**: Fast iteration, low cost
- **DeepSeek**: Good for testing conversation memory

### For Specific Use Cases
- **Code-focused interviews**: GPT-4, DeepSeek
- **General technical topics**: GPT-3.5-turbo, DeepSeek
- **Complex reasoning**: GPT-4

## Switching Steps

### Step 1: Update Environment Variables
Edit `/app/backend/.env`:
```bash
nano /app/backend/.env
```

Change the three variables:
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEFAULT_AI_MODEL`

### Step 2: Restart Backend
```bash
sudo supervisorctl restart backend
```

### Step 3: Verify
```bash
# Check logs to confirm new model
tail -f /var/log/supervisor/backend.err.log

# Test generation
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Topic", "num_questions": 1}'
```

## Testing Multiple Models

You can test different models without changing configuration:

```bash
# Test DeepSeek
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "num_questions": 2, "model": "deepseek-chat"}'

# Test GPT-4 (requires OpenAI key in DEEPSEEK_API_KEY if using OpenAI base URL)
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "num_questions": 2, "model": "gpt-4"}'
```

## Troubleshooting

### Invalid API Key
```
Error: AI generation error: 401 Unauthorized
```
**Solution**: Verify your API key is correct in `.env`

### Model Not Found
```
Error: AI generation error: Model 'xyz' not found
```
**Solution**: Check that the model name is correct for your provider

### Rate Limit Exceeded
```
Error: AI generation error: 429 Too Many Requests
```
**Solution**: 
- Reduce `num_questions` in requests
- Add delay between requests
- Upgrade your API plan

### Connection Timeout
```
Error: AI generation error: Connection timeout
```
**Solution**: 
- Check `DEEPSEEK_BASE_URL` is correct
- Verify network connectivity
- Check provider status page

## Cost Optimization

### Reduce Token Usage
1. Lower `num_questions` (fewer API calls)
2. Use GPT-3.5-turbo instead of GPT-4
3. Set lower `max_tokens` in `AIService.generate_completion()`

### Monitor Usage
Check logs for token consumption:
```bash
grep "Completion generated" /var/log/supervisor/backend.err.log
```

## Example: Switching from DeepSeek to OpenAI

**Before (.env):**
```bash
DEEPSEEK_API_KEY="sk-8589f0a371da4c5eaf8982790287c8a5"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEFAULT_AI_MODEL="deepseek-chat"
```

**After (.env):**
```bash
DEEPSEEK_API_KEY="sk-proj-abc123..."  # Your OpenAI key
DEEPSEEK_BASE_URL="https://api.openai.com/v1"
DEFAULT_AI_MODEL="gpt-4"
```

**Restart:**
```bash
sudo supervisorctl restart backend
```

**Test:**
```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Microservices", "num_questions": 2}'
```

## Best Practices

1. **Test in Development First**: Always test model changes with small requests first
2. **Monitor Quality**: Compare output quality between models for your use case
3. **Cost Tracking**: Keep track of API costs per model
4. **Fallback Strategy**: Have a backup model configured if primary fails
5. **Version Control**: Document which model works best for each topic type
6. **Rate Limiting**: Implement rate limiting for expensive models

## Advanced: Multi-Model Support

For production systems, consider implementing:

```python
# Example: Route based on topic complexity
def select_model(topic: str, num_questions: int) -> str:
    if num_questions > 10:
        return "gpt-4"  # Complex conversations
    elif "advanced" in topic.lower():
        return "gpt-4"
    else:
        return "gpt-3.5-turbo"  # Simple topics
```

This could be added to the `ScriptGenerationService` for automatic model selection.
