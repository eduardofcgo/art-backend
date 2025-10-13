# Deployment Guide

## GitHub Actions CI/CD

This project uses GitHub Actions to automatically build and push Docker images to GitHub Container Registry (GHCR) whenever code is pushed to the `main` branch.

### What happens on push to main:

1. The workflow builds a Docker image
2. Tags it with:
   - `latest` (for the most recent build)
   - Git commit SHA (e.g., `main-abc123f`)
   - Branch name (e.g., `main`)
3. Pushes to GitHub Container Registry
4. Builds for both `linux/amd64` and `linux/arm64` platforms

### Accessing the Docker Image

The built image is available at:
```
ghcr.io/<your-github-username>/art-backend:latest
```

Replace `<your-github-username>` with your actual GitHub username or organization name.

### Authenticating with GitHub Container Registry (for Private Images)

If your repository is private, the container images will also be private. To pull them in production, you need to authenticate:

#### 1. Create a GitHub Personal Access Token (PAT)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Production Server - art-backend")
4. Select scopes:
   - ✅ `read:packages` - Download packages from GitHub Package Registry
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

#### 2. Login to GHCR on Your Production Server

```bash
# Method 1: Using docker login
echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Method 2: Using environment variable
export CR_PAT=YOUR_GITHUB_PAT
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Once authenticated, you can pull private images.

## Production Deployment

### Option 1: Pull and Run Directly

```bash
# Step 1: Login to GitHub Container Registry (required for private repos)
export GITHUB_PAT=your_personal_access_token_here
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Step 2: Pull the latest image
docker pull ghcr.io/<your-github-username>/art-backend:latest

# Step 3: Run the container
docker run -d \
  --name art-backend \
  -p 8000:8000 \
  -e AI_PROVIDER=gemini \
  -e GOOGLE_API_KEY=your_api_key_here \
  --restart unless-stopped \
  ghcr.io/<your-github-username>/art-backend:latest
```

### Option 2: Using Docker Compose in Production

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  art-backend:
    image: ghcr.io/<your-github-username>/art-backend:latest
    container_name: art-backend
    ports:
      - "8000:8000"
    environment:
      - AI_PROVIDER=${AI_PROVIDER}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.post('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Deploy with:
```bash
# First, login to GHCR (for private images)
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Then deploy
docker-compose -f docker-compose.prod.yml up -d
```

**Note**: Docker Compose will use your authenticated credentials automatically after you've logged in.

### Option 3: Kubernetes Deployment

For private images, you need to create an image pull secret first:

```bash
# Create a secret for pulling private images from GHCR
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=your-email@example.com

# Or using a secret from a file
kubectl create secret generic art-backend-secrets \
  --from-literal=ai-provider=gemini \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY
```

Create a `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: art-backend
  labels:
    app: art-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: art-backend
  template:
    metadata:
      labels:
        app: art-backend
    spec:
      imagePullSecrets:
      - name: ghcr-secret  # Required for private images
      containers:
      - name: art-backend
        image: ghcr.io/<your-github-username>/art-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: AI_PROVIDER
          valueFrom:
            secretKeyRef:
              name: art-backend-secrets
              key: ai-provider
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: art-backend-secrets
              key: google-api-key
        livenessProbe:
          httpPost:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpPost:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: art-backend-service
spec:
  selector:
    app: art-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy with:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Option 4: Cloud Platforms (with Private Images)

#### AWS ECS/Fargate

For private GHCR images, create a secret in AWS Secrets Manager:

```bash
# 1. Create a secret with your GitHub PAT
aws secretsmanager create-secret \
  --name ghcr-credentials \
  --description "GitHub Container Registry credentials" \
  --secret-string '{"username":"YOUR_GITHUB_USERNAME","password":"YOUR_GITHUB_PAT"}'

# 2. Update your ECS task definition to reference the secret for authentication
# In your task definition JSON:
{
  "containerDefinitions": [{
    "image": "ghcr.io/<your-github-username>/art-backend:latest",
    "repositoryCredentials": {
      "credentialsParameter": "arn:aws:secretsmanager:region:account-id:secret:ghcr-credentials"
    }
  }]
}
```

#### Google Cloud Run

```bash
# 1. Create a service account key with access to GHCR
# 2. Create a secret in Google Secret Manager with your GitHub PAT

# 3. Deploy with authentication
gcloud run deploy art-backend \
  --image ghcr.io/<your-github-username>/art-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AI_PROVIDER=gemini,GOOGLE_API_KEY=your_key

# For private images, you may need to use Artifact Registry as a mirror
# or configure docker credentials in Cloud Build
```

#### Azure Container Instances

```bash
# 1. Create a registry credential secret
az container create \
  --resource-group myResourceGroup \
  --name art-backend \
  --image ghcr.io/<your-github-username>/art-backend:latest \
  --registry-login-server ghcr.io \
  --registry-username YOUR_GITHUB_USERNAME \
  --registry-password YOUR_GITHUB_PAT \
  --dns-name-label art-backend \
  --ports 8000 \
  --environment-variables AI_PROVIDER=gemini GOOGLE_API_KEY=your_key
```

## Making Repository Images Public

If your GitHub repository is private, the container images are also private by default. To make them public:

1. Go to your GitHub repository
2. Click on "Packages" in the right sidebar
3. Click on your package (art-backend)
4. Click "Package settings"
5. Scroll down to "Danger Zone"
6. Click "Change visibility" and select "Public"

## Image Tags

- `latest` - Always points to the most recent build from main
- `main-<commit-sha>` - Specific commit version (e.g., `main-abc123f`)
- `main` - Latest from main branch

For production, it's recommended to use specific commit SHA tags instead of `latest` for reproducibility:
```bash
docker pull ghcr.io/<your-github-username>/art-backend:main-abc123f
```

## Environment Variables

Required environment variables for production:

| Variable | Description | Required |
|----------|-------------|----------|
| `AI_PROVIDER` | AI provider to use (openai, gemini, or anthropic) | Yes |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI |
| `GOOGLE_API_KEY` | Google API key | If using Gemini |
| `ANTHROPIC_API_KEY` | Anthropic API key | If using Anthropic |

## Monitoring

The application includes a health check endpoint at `/health` that returns "healthy" when the service is running properly.

## Updating Production

To update your production deployment with the latest image:

```bash
# Pull the latest image
docker pull ghcr.io/<your-github-username>/art-backend:latest

# Restart the container
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

Or with Kubernetes:
```bash
kubectl rollout restart deployment/art-backend
```

