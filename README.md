# Art Interpretation API

A Litestar-based web API that uses AI vision models to provide detailed art interpretation and analysis from uploaded images.

## Features

- 📸 Upload artwork images for interpretation
- 🎨 Professional art analysis covering composition, context, symbolism, and emotional reading
- 🤖 Multiple AI provider support (OpenAI GPT-4o, Google Gemini, Anthropic Claude)
- 🔌 Dependency injection for clean architecture
- 🚀 Fast and modern ASGI-based API using Litestar
- 🔒 Secure image processing with validation and optimization
- 🌐 CORS-enabled for frontend integration

## Prerequisites

- Python 3.9+
- API key for at least one of the supported providers:
  - OpenAI API key (for GPT-4o)
  - Google API key (for Gemini)
  - Anthropic API key (for Claude)

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd art-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (copy from `.env.example`):
```bash
# Choose your AI provider (openai, gemini, or anthropic)
AI_PROVIDER=gemini

# Add the API key for your chosen provider
GOOGLE_API_KEY=your_google_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
# or
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Running the Server

Start the development server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Interpret Art
**POST** `/api/interpret-art`

Analyzes an uploaded artwork image and returns a detailed interpretation.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Image file (JPEG, PNG, etc.)

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/interpret-art \
  -F "data=@/path/to/artwork.jpg"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/interpret-art"
files = {"data": open("artwork.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "interpretation": "**Formal Description:**\n[Detailed analysis...]\n\n**Context and Influences:**\n[Historical context...]\n\n**Symbolic Interpretation:**\n[Symbolic meanings...]\n\n**Emotional or Psychological Reading:**\n[Emotional analysis...]"
}
```

### 2. Health Check
**POST** `/api/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Art Interpretation Structure

The API provides interpretations structured in four sections:

1. **Formal Description:** Analyzes composition, color, texture, form, and technique
2. **Context and Influences:** Relates the work to artistic movements and historical references
3. **Symbolic Interpretation:** Explores deeper meanings and archetypes
4. **Emotional or Psychological Reading:** Discusses mood and emotional tone

## Image Processing

- Automatically validates and processes uploaded images
- Converts images to RGB format if needed
- Resizes large images to optimize API calls (max 2000px)
- Supports common image formats (JPEG, PNG, etc.)

## AI Provider Configuration

The API is configured via dependency injection to use one AI provider at a time. You configure the provider in your `.env` file:

```bash
AI_PROVIDER=gemini  # Options: openai, gemini, anthropic
```

### Provider Comparison

| Provider | Model | Strengths |
|----------|-------|-----------|
| **OpenAI** | GPT-4o | Excellent general-purpose vision analysis, strong contextual understanding |
| **Gemini** | Gemini 2.5 Flash | Fast responses, high-quality analysis, cost-effective |
| **Anthropic** | Claude 3.5 Sonnet | Detailed and nuanced interpretations, excellent for creative analysis |

The provider is configured at application startup using dependency injection, ensuring clean separation of concerns and easy testing.

## Development

### Project Structure
```
art-backend/
├── app.py                      # Main application file
├── config/
│   ├── prompts.py             # AI prompts
│   └── settings.py            # Application settings
├── controllers/
│   └── art_controller.py      # Business logic
├── dependencies/
│   └── ai_provider.py         # Dependency injection for AI services
├── services/
│   ├── openai_service.py      # OpenAI integration
│   ├── gemini_service.py      # Google Gemini integration
│   └── anthropic_service.py   # Anthropic Claude integration
├── middleware/
│   └── error_handler.py       # Error handling
├── utils/
│   ├── image_processor.py     # Image validation and processing
│   └── response_cleaner.py    # XML response cleaning
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
└── README.md                  # This file
```

### Configuration

The API uses environment variables for configuration:
- `AI_PROVIDER`: AI provider to use - `openai`, `gemini`, or `anthropic` (required)
- `OPENAI_API_KEY`: Your OpenAI API key (required if using OpenAI)
- `GOOGLE_API_KEY`: Your Google API key (required if using Gemini)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required if using Anthropic)

## CORS Configuration

The API is configured with CORS enabled for all origins (`*`) by default. For production, update the `allow_origins` in `app.py` to specify your frontend domain:

```python
cors_config = CORSConfig(
    allow_origins=["https://your-frontend-domain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Error Handling

The API includes comprehensive error handling:
- Invalid image formats are caught and reported
- API errors are gracefully handled
- Detailed error messages for debugging

## Docker Deployment

### Local Development with Docker

Build and run with Docker:
```bash
# Build the image
docker build -t art-backend .

# Run with Docker Compose
docker-compose up -d
```

### Production Deployment

The project includes automated Docker image builds via GitHub Actions. When you push to the `main` branch, a Docker image is automatically built and published to GitHub Container Registry (GHCR).

**Using the pre-built image:**
```bash
# Pull the latest image (replace <your-github-username> with your GitHub username)
docker pull ghcr.io/<your-github-username>/art-backend:latest

# Run in production
docker-compose -f docker-compose.prod.yml up -d
```

**Image tags available:**
- `latest` - Most recent build from main
- `main-<commit-sha>` - Specific commit version
- `main` - Latest from main branch

For detailed deployment instructions including Kubernetes, cloud platforms, and CI/CD setup, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Manual Production Deployment (without Docker)

For production deployment without Docker:

1. Update CORS configuration with your frontend domain
2. Use a production ASGI server like Gunicorn with Uvicorn workers:
```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. Set up environment variables securely
4. Consider adding rate limiting and authentication
5. Use HTTPS in production

## License

MIT License - feel free to use this project for your art interpretation needs!

