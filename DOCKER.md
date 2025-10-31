# Docker Quick Reference

## Quick Commands

### Using Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Using Docker Directly

```bash
# Build the image
docker build -t interview-video-generator:latest ./backend

# Run the container
docker run -d \
  --name interview-video-generator \
  -p 8001:8001 \
  --env-file backend/.env \
  -v $(pwd)/backend/audio_files:/app/audio_files \
  interview-video-generator:latest

# View logs
docker logs -f interview-video-generator

# Stop and remove container
docker stop interview-video-generator
docker rm interview-video-generator
```

## GitHub Container Registry

### Pull Image

```bash
docker pull ghcr.io/<your-github-username>/interview-video-generator:latest
```

### Push Image

1. Login to GitHub Container Registry:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <your-github-username> --password-stdin
```

2. Tag your image:
```bash
docker tag interview-video-generator:latest ghcr.io/<your-github-username>/interview-video-generator:latest
```

3. Push to registry:
```bash
docker push ghcr.io/<your-github-username>/interview-video-generator:latest
```

### Automated Builds

The repository includes GitHub Actions workflow that automatically builds and pushes Docker images.

**Trigger build by:**
- Pushing to `main` branch
- Creating a version tag (e.g., `v1.0.0`)

```bash
# Push to main
git push origin main

# Or create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Environment Variables

Required environment variables are loaded from `backend/.env`:

```bash
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
MONGO_CLUSTER=cluster0.xxxxx.mongodb.net
DEEPSEEK_API_KEY=sk-your-api-key
# ... (see .env.example for complete list)
```

## Health Checks

The container includes automatic health checks:
- Endpoint: `http://localhost:8001/api/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' interview-video-generator
```

## FFmpeg

FFmpeg is pre-installed in the Docker image. Verify:

```bash
docker exec interview-video-generator ffmpeg -version
```

## Volumes

The container uses volumes for persistent data:
- `./backend/audio_files:/app/audio_files` - Generated audio files

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs backend
# or
docker logs interview-video-generator
```

### MongoDB connection issues

1. Verify `.env` has correct credentials
2. Check MongoDB Atlas allows Docker container's IP
3. Test connection from container:
```bash
docker exec -it interview-video-generator python -c "from config.database import get_database; print(get_database())"
```

### FFmpeg not working

FFmpeg should be pre-installed. If issues persist:
```bash
# Enter container
docker exec -it interview-video-generator bash

# Check ffmpeg
ffmpeg -version
```

## Production Deployment

### Resource Limits

```bash
docker run -d \
  --name interview-video-generator \
  --memory="2g" \
  --cpus="2" \
  -p 8001:8001 \
  --env-file backend/.env \
  interview-video-generator:latest
```

### Use Specific Versions

Instead of `latest`, use version tags:
```bash
docker pull ghcr.io/<your-username>/interview-video-generator:v1.0.0
```

### Docker Compose with Resource Limits

```yaml
services:
  backend:
    image: ghcr.io/<your-username>/interview-video-generator:v1.0.0
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```
