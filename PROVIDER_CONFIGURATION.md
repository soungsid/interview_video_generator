# Configuration Guide: AI & Audio Providers

This guide explains how to configure and switch between different AI and audio providers in the InterviewVideoGenerator application.

## Table of Contents
1. [AI Providers Configuration](#ai-providers-configuration)
2. [Audio Providers Configuration](#audio-providers-configuration)
3. [Voice Configuration](#voice-configuration)
4. [Quick Reference](#quick-reference)

---

## AI Providers Configuration

The application supports multiple AI providers for script generation. You can easily switch between them by updating the `.env` file.

### Supported AI Providers

1. **DeepSeek** (Default)
2. **OpenAI** (GPT-4o, GPT-4-turbo, etc.)
3. **Gemini** (Gemini 2.0 Flash Exp, Gemini 1.5 Pro, etc.)

### Configuration Steps

#### 1. Set Default Provider

In `/app/backend/.env`, set the `DEFAULT_AI_PROVIDER` variable:

```bash
# Choose one: deepseek, openai, or gemini
DEFAULT_AI_PROVIDER="deepseek"
```

#### 2. Configure Provider-Specific Settings

##### DeepSeek Configuration
```bash
DEEPSEEK_API_KEY="your-deepseek-api-key"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEEPSEEK_MODEL="deepseek-chat"
```

##### OpenAI Configuration
```bash
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o"  # or gpt-4-turbo, gpt-3.5-turbo
```

##### Gemini Configuration
```bash
GEMINI_API_KEY="your-gemini-api-key"
GEMINI_MODEL="gemini-2.0-flash-exp"  # or gemini-1.5-pro
```

#### 3. Restart the Backend

After updating the `.env` file:

```bash
sudo supervisorctl restart backend
```

### Switching Models

You can override the default model per request without changing the configuration:

```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python FastAPI",
    "num_questions": 3,
    "language": "en",
    "model": "gpt-4o"
  }'
```

---

## Audio Providers Configuration

The application supports multiple audio providers for text-to-speech generation.

### Supported Audio Providers

1. **Amazon Polly** (Default)
2. **OpenAI TTS**
3. **ElevenLabs**

### Configuration Steps

#### 1. Set Default Audio Provider

In `/app/backend/.env`, set the `DEFAULT_AUDIO_PROVIDER` variable:

```bash
# Choose one: polly, openai-tts, or elevenlabs
DEFAULT_AUDIO_PROVIDER="polly"
```

#### 2. Configure Provider-Specific Settings

##### Amazon Polly Configuration
```bash
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_DEFAULT_REGION="us-east-1"
POLLY_VOICE_INTERVIEWER="Matthew"
POLLY_VOICE_CANDIDATE="Joanna"
```

**Available Polly Neural Voices:**
- **Male**: Matthew, Joey, Justin, Kevin, Stephen
- **Female**: Joanna, Kendra, Kimberly, Salli, Amy, Emma, Olivia
- **Multilingual**: See [AWS Polly Voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

##### OpenAI TTS Configuration
```bash
OPENAI_TTS_API_KEY="your-openai-api-key"
OPENAI_TTS_VOICE_INTERVIEWER="onyx"
OPENAI_TTS_VOICE_CANDIDATE="nova"
```

**Available OpenAI TTS Voices:**
- `alloy` - Neutral
- `echo` - Male
- `fable` - British accent
- `onyx` - Deep male (recommended for interviewer)
- `nova` - Female (recommended for candidate)
- `shimmer` - Soft female

##### ElevenLabs Configuration
```bash
ELEVENLABS_API_KEY="your-elevenlabs-api-key"
ELEVENLABS_VOICE_INTERVIEWER="Brian"
ELEVENLABS_VOICE_CANDIDATE="Jessica"
```

**Finding ElevenLabs Voice IDs:**
1. Visit [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Browse and select voices
3. Copy the Voice ID
4. Update the `.env` file with the Voice ID or name

**Popular ElevenLabs Voices:**
- **Male**: Brian, Daniel, George, Callum, Charlie
- **Female**: Jessica, Rachel, Domi, Bella, Elli

#### 3. Restart the Backend

```bash
sudo supervisorctl restart backend
```

---

## Voice Configuration

### How to Change Voices

#### Method 1: Update Environment Variables (Recommended)

1. Open `/app/backend/.env`
2. Update the voice variables for your chosen provider
3. Restart the backend

**Example for OpenAI TTS:**
```bash
# Change to different voices
OPENAI_TTS_VOICE_INTERVIEWER="echo"  # Changed from "onyx"
OPENAI_TTS_VOICE_CANDIDATE="shimmer"  # Changed from "nova"
```

#### Method 2: Test Multiple Voices

Create a test script to compare different voices:

```bash
# Test script
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Voice Test",
    "num_questions": 1,
    "language": "en"
  }'
```

Then listen to the generated audio to decide which voices work best.

### Voice Selection Tips

#### For Interviewers (Professional, Authoritative)
- **Polly**: Matthew, Stephen (English), Mathieu (French)
- **OpenAI TTS**: onyx, echo
- **ElevenLabs**: Brian, Daniel, George

#### For Candidates (Clear, Professional)
- **Polly**: Joanna, Kendra (English), Céline (French)
- **OpenAI TTS**: nova, alloy
- **ElevenLabs**: Jessica, Rachel, Bella

#### For Multilingual Support
- **French Interviews:**
  - Polly: Mathieu (male), Céline (female)
  - ElevenLabs has excellent multilingual support
  - OpenAI TTS voices work with multiple languages

### Voice Quality Comparison

| Provider | Quality | Speed | Cost | Multilingual |
|----------|---------|-------|------|--------------|
| **Amazon Polly** | Good | Fast | Low | Excellent |
| **OpenAI TTS** | Very Good | Fast | Medium | Good |
| **ElevenLabs** | Excellent | Medium | High | Excellent |

---

## Quick Reference

### Environment Variables Summary

```bash
# ========================================
# AI PROVIDERS
# ========================================
DEFAULT_AI_PROVIDER="deepseek"  # deepseek, openai, gemini

# DeepSeek
DEEPSEEK_API_KEY="sk-..."
DEEPSEEK_MODEL="deepseek-chat"

# OpenAI
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4o"

# Gemini
GEMINI_API_KEY="..."
GEMINI_MODEL="gemini-2.0-flash-exp"

# ========================================
# AUDIO PROVIDERS
# ========================================
DEFAULT_AUDIO_PROVIDER="polly"  # polly, openai-tts, elevenlabs

# Amazon Polly
POLLY_VOICE_INTERVIEWER="Matthew"
POLLY_VOICE_CANDIDATE="Joanna"

# OpenAI TTS
OPENAI_TTS_VOICE_INTERVIEWER="onyx"
OPENAI_TTS_VOICE_CANDIDATE="nova"

# ElevenLabs
ELEVENLABS_VOICE_INTERVIEWER="Brian"
ELEVENLABS_VOICE_CANDIDATE="Jessica"
```

### Common Commands

```bash
# Restart backend after configuration changes
sudo supervisorctl restart backend

# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Test video generation
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test", "num_questions": 2}'
```

### Troubleshooting

#### Provider Not Working
1. Check API key is correctly set in `.env`
2. Verify provider name is correct (deepseek, openai, gemini)
3. Check backend logs for error messages
4. Ensure backend was restarted after changes

#### Voice Not Changing
1. Confirm voice ID/name is correct for the provider
2. Check that the correct provider is selected (`DEFAULT_AUDIO_PROVIDER`)
3. Restart the backend service
4. Clear any cached audio files if testing the same content

#### API Rate Limits
- Reduce `num_questions` in requests
- Switch to a less expensive model/provider
- Check your API provider's rate limits and usage

---

## Advanced Configuration

### Using Different Providers for Different Languages

You can programmatically switch providers based on language in your code, or simply configure the provider that works best for your primary language.

### Cost Optimization

1. **Development:** Use DeepSeek or GPT-3.5-turbo for script generation, Polly for audio
2. **Production:** Use GPT-4o for script generation, ElevenLabs for audio (best quality)
3. **Budget:** Use DeepSeek for script generation, Polly for audio

### Model-Specific Features

- **GPT-4o**: Best for complex technical interviews
- **Gemini 2.0 Flash**: Fast and good for general topics
- **DeepSeek**: Cost-effective with good quality

---

## Support

For more information:
- [OpenAI TTS Documentation](https://platform.openai.com/docs/guides/text-to-speech)
- [Amazon Polly Voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)
- [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
