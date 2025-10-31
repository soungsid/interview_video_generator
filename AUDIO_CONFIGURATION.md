# Audio Files Configuration

This document explains how to configure and manage audio file storage in the InterviewVideoGenerator API.

## Overview

The application generates audio files for interview dialogues using AWS Polly (Text-to-Speech). The location where these files are stored can be configured via the `AUDIO_FILES_PATH` environment variable.

---

## Configuration

### Environment Variable

```bash
AUDIO_FILES_PATH="./audio_files"
```

**Location:** Add this to `backend/.env` file

### Default Behavior

- **Default path:** `./audio_files` (created in current working directory)
- **Auto-creation:** Directory is created automatically if it doesn't exist
- **Permissions:** Application must have write permissions

---

## Path Options

### 1. Relative Path (Recommended for Development)

```bash
AUDIO_FILES_PATH="./audio_files"
```

- Creates folder relative to where application is running
- Good for development and testing
- Easy to locate and manage

### 2. Absolute Path (Recommended for Production)

**Linux/macOS:**
```bash
AUDIO_FILES_PATH="/var/app/audio_files"
```

**Windows:**
```bash
AUDIO_FILES_PATH="C:\\projects\\interview-gen\\audio_files"
```

- Full path specification
- Consistent location regardless of working directory
- Better for production deployments

### 3. Docker Path

In Docker container (default):
```bash
AUDIO_FILES_PATH="/app/audio_files"
```

With custom volume mount:
```bash
AUDIO_FILES_PATH="/data/audio"
```

---

## Docker Configuration

### Using docker-compose.yml

The default configuration uses a named volume:

```yaml
services:
  backend:
    environment:
      - AUDIO_FILES_PATH=/app/audio_files
    volumes:
      - audio_data:/app/audio_files

volumes:
  audio_data:
    driver: local
```

### Custom Volume Location

**Bind mount to host directory:**

```yaml
services:
  backend:
    environment:
      - AUDIO_FILES_PATH=/app/audio_files
    volumes:
      - ./my_audio_files:/app/audio_files
```

Or with custom path:

```yaml
services:
  backend:
    environment:
      - AUDIO_FILES_PATH=/data/audio
    volumes:
      - /host/path/audio:/data/audio
```

### Using Docker CLI

```bash
docker run -d \
  --name interview-video-generator \
  -e AUDIO_FILES_PATH=/app/audio_files \
  -v /host/audio:/app/audio_files \
  interview-video-generator:latest
```

---

## Directory Structure

Generated files are organized by video ID:

```
audio_files/
├── {video-id-1}/
│   ├── intro.mp3
│   ├── dialogue_1.mp3
│   ├── dialogue_2.mp3
│   ├── conclusion.mp3
│   └── final.mp3
├── {video-id-2}/
│   ├── intro.mp3
│   ├── dialogue_1.mp3
│   └── ...
└── ...
```

**File types:**
- `intro.mp3` - Introduction audio
- `dialogue_N.mp3` - Individual dialogue segments
- `conclusion.mp3` - Conclusion audio
- `final.mp3` - Complete concatenated audio

---

## Storage Considerations

### Disk Space

**Estimate per video:**
- Short video (3 questions): ~5-10 MB
- Medium video (5 questions): ~10-20 MB
- Long video (10 questions): ~20-40 MB

**Planning:**
- 100 videos: ~1-2 GB
- 1000 videos: ~10-20 GB

### Cleanup

Audio files are **not automatically deleted**. Implement cleanup strategies:

#### Manual Cleanup

```bash
# Delete audio for specific video
rm -rf audio_files/{video-id}

# Delete all audio files older than 30 days
find audio_files -type d -mtime +30 -exec rm -rf {} +
```

#### Automated Cleanup Script

Create `cleanup_old_audio.sh`:

```bash
#!/bin/bash
AUDIO_DIR="${AUDIO_FILES_PATH:-./audio_files}"
DAYS_OLD=30

echo "Cleaning up audio files older than ${DAYS_OLD} days..."
find "${AUDIO_DIR}" -type d -mtime +${DAYS_OLD} -exec rm -rf {} +
echo "Cleanup complete!"
```

Run via cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/cleanup_old_audio.sh
```

---

## Permissions

### Linux/macOS

Ensure write permissions:

```bash
chmod 755 audio_files
```

For specific user:
```bash
chown -R myuser:mygroup audio_files
```

### Docker

Container runs as root by default, but you can specify user:

```dockerfile
# In Dockerfile
USER 1000:1000
```

Or in docker-compose.yml:
```yaml
services:
  backend:
    user: "1000:1000"
```

---

## Cloud Storage

For production, consider cloud storage:

### AWS S3

Modify AudioService to upload to S3:

```python
import boto3

s3_client = boto3.client('s3')
s3_client.upload_file(
    local_path,
    'my-bucket',
    f'audio_files/{video_id}/final.mp3'
)
```

### Google Cloud Storage

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('my-bucket')
blob = bucket.blob(f'audio_files/{video_id}/final.mp3')
blob.upload_from_filename(local_path)
```

---

## Troubleshooting

### Error: "Permission denied"

**Linux/macOS:**
```bash
sudo chmod -R 755 audio_files
```

**Docker:**
```bash
# Check volume permissions
docker exec interview-video-generator ls -la /app/audio_files
```

### Error: "No such file or directory"

**Solution:** Ensure path is correct and parent directories exist

**Check path resolution:**
```python
from pathlib import Path
import os

audio_path = os.environ.get('AUDIO_FILES_PATH', './audio_files')
resolved = Path(audio_path).resolve()
print(f"Audio files will be stored in: {resolved}")
```

### Error: "Disk space full"

**Check disk usage:**
```bash
df -h audio_files
du -sh audio_files/*
```

**Clean up old files:**
```bash
# Delete oldest 50% of videos
cd audio_files
ls -t | tail -n +$(( $(ls | wc -l) / 2 + 1 )) | xargs rm -rf
```

### Docker: Files not persisting

**Issue:** Files disappear when container restarts

**Solution:** Use volumes in docker-compose.yml:
```yaml
volumes:
  - audio_data:/app/audio_files

volumes:
  audio_data:
```

---

## Best Practices

### Development

1. **Use relative paths** for portability
2. **Add to .gitignore** to avoid committing audio files
3. **Keep sample files** for testing

```bash
# Add to .gitignore
audio_files/*
!audio_files/.gitkeep
```

### Production

1. **Use absolute paths** for consistency
2. **Mount volumes** for persistence (Docker)
3. **Implement cleanup** to manage disk space
4. **Monitor disk usage** with alerts
5. **Consider cloud storage** for scalability
6. **Backup important files** regularly

### Security

1. **Restrict permissions** (755 for directories, 644 for files)
2. **Don't expose** audio directory via web server
3. **Validate paths** to prevent directory traversal
4. **Use signed URLs** if serving files publicly

---

## Verification

### Check Configuration

```bash
# View current configuration
cat backend/.env | grep AUDIO_FILES_PATH

# Test directory creation
python -c "
from pathlib import Path
import os
audio_path = os.environ.get('AUDIO_FILES_PATH', './audio_files')
p = Path(audio_path).resolve()
p.mkdir(parents=True, exist_ok=True)
print(f'Audio directory: {p}')
print(f'Exists: {p.exists()}')
print(f'Writable: {os.access(p, os.W_OK)}')
"
```

### Test Audio Generation

```bash
curl -X POST http://localhost:8001/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Test Audio",
    "num_questions": 1
  }'
```

Check if files were created:
```bash
ls -lh audio_files/
```

---

## Related Documentation

- [ENV_VARIABLES.md](ENV_VARIABLES.md) - All environment variables
- [DOCKER.md](DOCKER.md) - Docker configuration
- [README.md](README.md) - Main documentation

---

## Need Help?

- Check application logs for audio service errors
- Verify AWS Polly credentials (if using TTS)
- Ensure ffmpeg is installed for audio processing
- Review [ENV_VARIABLES.md](ENV_VARIABLES.md) for AWS Polly setup
