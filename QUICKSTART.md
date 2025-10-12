# Quick Start Guide

Get your Art Interpretation API up and running in 5 minutes!

## Step 1: Set up your environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure your API keys

Create a `.env` file in the project root:

```bash
# For OpenAI (GPT-4o)
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# For Google Gemini (optional, for alternative provider)
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env
```

Replace the placeholder values with your actual API keys:
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys
- **Google API Key**: Get from https://makersuite.google.com/app/apikey

> **Note**: You can use either provider or both. If you only want to use OpenAI, just set `OPENAI_API_KEY`.

## Step 3: Start the server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 4: Test the API

### Available Endpoints

The API now supports two AI providers:

1. **`/api/interpret-art`** - Uses OpenAI GPT-4o (Primary)
2. **`/api/interpret-art-gemini`** - Uses Google Gemini 1.5 Pro (Alternative)

Both endpoints accept the same input format and return the same XML structure.

### Option 1: Using the test script

```bash
# Test with OpenAI
python test_api.py path/to/artwork.jpg

# Test with Gemini (if you update the script endpoint)
python test_api.py path/to/artwork.jpg
```

### Option 2: Using curl

```bash
# OpenAI GPT-4o
curl -X POST http://localhost:8000/api/interpret-art \
  -F "data=@path/to/artwork.jpg"

# Google Gemini 1.5 Pro
curl -X POST http://localhost:8000/api/interpret-art-gemini \
  -F "data=@path/to/artwork.jpg"
```

### Option 3: Using Python

```python
import requests

# Using OpenAI
response = requests.post(
    "http://localhost:8000/api/interpret-art",
    files={"data": open("artwork.jpg", "rb")}
)
print(response.text)  # Returns XML

# Using Google Gemini
response = requests.post(
    "http://localhost:8000/api/interpret-art-gemini",
    files={"data": open("artwork.jpg", "rb")}
)
print(response.text)  # Returns XML
```

## What to expect

The API will analyze your artwork and return a structured interpretation covering:

1. **Formal Description** - Composition, color, texture, form
2. **Context and Influences** - Art movements, historical references
3. **Symbolic Interpretation** - Deeper meanings, archetypes
4. **Emotional Reading** - Mood and psychological tone

## Next Steps

- Check out the full [README.md](README.md) for detailed documentation
- Integrate with your frontend application
- Customize the CORS settings for production
- Add authentication if needed

## Troubleshooting

**Server won't start?**
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Check that all dependencies are installed: `pip install -r requirements.txt`

**API returns errors?**
- Verify your `.env` file has the correct API key(s)
- Check that your image file exists and is a valid format (JPEG, PNG)
- Ensure you have internet connection for API calls
- For Gemini endpoint: Make sure you have set `GOOGLE_API_KEY` in `.env`

**CORS errors from frontend?**
- Update the `allow_origins` in `app.py` to include your frontend URL

