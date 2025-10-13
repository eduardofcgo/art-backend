# Using Private Docker Images - Quick Guide

This guide shows you how to use your private Docker images from GitHub Container Registry in production.

## 🔐 Step 1: Create a GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Tokens (classic)"** → **"Generate new token (classic)"**
3. Give it a name: `Production Server - art-backend`
4. Select scope: **`read:packages`** ✅
5. Click **"Generate token"**
6. **COPY THE TOKEN** - you won't see it again!

## 🖥️ Step 2: Production Server Setup

### Quick Start (Docker Compose - Recommended)

```bash
# 1. Login to GitHub Container Registry
export GITHUB_PAT="ghp_xxxxxxxxxxxx"  # Your PAT from Step 1
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 2. Update docker-compose.prod.yml with your GitHub username
# Replace: ghcr.io/<your-github-username>/art-backend:latest
# With:    ghcr.io/YOUR_ACTUAL_USERNAME/art-backend:latest

# 3. Create .env.production file
cat > .env.production << 'EOF'
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_google_api_key_here
EOF

# 4. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 5. Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Alternative: Direct Docker Run

```bash
# 1. Login
export GITHUB_PAT="ghp_xxxxxxxxxxxx"
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 2. Pull image
docker pull ghcr.io/YOUR_GITHUB_USERNAME/art-backend:latest

# 3. Run
docker run -d \
  --name art-backend \
  -p 8000:8000 \
  -e AI_PROVIDER=gemini \
  -e GOOGLE_API_KEY=your_api_key \
  --restart unless-stopped \
  ghcr.io/YOUR_GITHUB_USERNAME/art-backend:latest
```

## 🔄 Updating to Latest Version

```bash
# 1. Pull latest image
docker-compose -f docker-compose.prod.yml pull

# 2. Restart with new image
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Or with direct docker:
docker pull ghcr.io/YOUR_GITHUB_USERNAME/art-backend:latest
docker stop art-backend
docker rm art-backend
docker run -d --name art-backend ... # (same run command as before)
```

## ☸️ Kubernetes Setup

```bash
# 1. Create image pull secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=your-email@example.com

# 2. Create app secrets
kubectl create secret generic art-backend-secrets \
  --from-literal=ai-provider=gemini \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY

# 3. Deploy (make sure k8s-deployment.yaml includes imagePullSecrets)
kubectl apply -f k8s-deployment.yaml
```

## 🔧 Troubleshooting

### "unauthorized: authentication required" error
- Your login expired or PAT is invalid
- Re-run the login command with a valid PAT

### "no such image" error
- Check your GitHub username is correct in the image URL
- Verify the image was built successfully (check GitHub Actions)
- Try pulling manually: `docker pull ghcr.io/USERNAME/art-backend:latest`

### Image pulls successfully but container won't start
- Check logs: `docker logs art-backend`
- Verify your API keys are set correctly
- Check health endpoint: `curl http://localhost:8000/health`

## 🔐 Security Best Practices

1. **Never commit** your GitHub PAT to version control
2. **Use environment variables** or secret management systems
3. **Rotate tokens** periodically (GitHub Settings → Tokens → Regenerate)
4. **Limit token scope** to only `read:packages`
5. **Set token expiration** when creating the PAT

## 📋 Checklist

- [ ] Created GitHub Personal Access Token with `read:packages` scope
- [ ] Logged in to ghcr.io on production server
- [ ] Updated docker-compose.prod.yml with your GitHub username
- [ ] Created .env.production with API keys
- [ ] Deployed and verified container is running
- [ ] Tested health endpoint: `curl http://YOUR_SERVER:8000/health`
- [ ] Stored PAT securely (password manager, secret manager, etc.)

## 🌐 Where is my image?

Your image URL format:
```
ghcr.io/YOUR_GITHUB_USERNAME/art-backend:TAG
```

Available tags:
- `latest` - most recent build from main
- `main` - same as latest
- `main-abc123` - specific commit SHA

Example with username "eduardo":
```
ghcr.io/eduardo/art-backend:latest
```

Check your GitHub repo → Packages section to see all published images.

