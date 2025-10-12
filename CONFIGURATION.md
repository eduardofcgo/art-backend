# Configuration Guide

## AI Provider Setup

The Art Backend API uses **dependency injection** to configure which AI provider to use. This means:

1. ✅ **Provider is configured in code only** (via `.env` file)
2. ✅ **No provider parameter needed in API requests**
3. ✅ **Clean separation of concerns**
4. ✅ **Easy to test and maintain**

## How It Works

### 1. Configuration (`.env` file)

```bash
AI_PROVIDER=gemini  # Options: openai, gemini, anthropic
GOOGLE_API_KEY=your_key_here
```

### 2. Dependency Injection Flow (Constructor Injection Pattern)

```
1. Settings (config/settings.py)
   - Loads AI_PROVIDER and API keys from environment
   - Validates configuration at startup
   ↓
2. Dependency Provider (dependencies/ai_provider.py)
   - Reads configuration from Settings
   - Creates service instance with injected API key
   - Returns: OpenAIService(api_key) | GeminiService(api_key) | AnthropicService(api_key)
   ↓
3. Litestar App (app.py)
   - @post("/api/interpret-art", dependencies={"ai_service": Provide(get_ai_service)})
   - Automatically calls get_ai_service() and injects result
   ↓
4. Controller (controllers/art_controller.py)
   - Receives configured service instance
   - Calls: ai_service.interpret_artwork_with_ai(image_data)
   - Controller doesn't know which provider it's using
```

### 3. Key Architecture Principles

✅ **Dependency Inversion Principle**: Services depend on injected configuration, not environment variables  
✅ **Constructor Injection**: API keys are passed to service constructors  
✅ **Single Responsibility**: Each service only handles its AI provider logic  
✅ **Configuration Isolation**: Only Settings module touches environment variables  
✅ **Testability**: Easy to mock services by injecting test API keys

### 3. Usage

Simply call the API without any provider parameter:

```bash
curl -X POST http://localhost:8000/api/interpret-art \
  -F "data=@artwork.jpg"
```

The API will automatically use the provider configured in your `.env` file.

## Switching Providers

To switch providers, simply:

1. Update `AI_PROVIDER` in your `.env` file
2. Ensure the corresponding API key is set
3. Restart the server

```bash
# Switch to OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key

# Switch to Gemini  
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_google_key

# Switch to Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
```

## Benefits of This Approach

- **Single Responsibility**: Each service only handles its specific AI provider
- **Type Safety**: Dependencies are properly typed
- **Testability**: Easy to mock services in tests
- **Configuration**: All config in one place (Settings)
- **No Coupling**: Controllers don't need to know about different providers
- **Validation**: Settings are validated at startup

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   .env file                          │
│   AI_PROVIDER=gemini                                 │
│   GOOGLE_API_KEY=xxx                                 │
└────────────────────┬─────────────────────────────────┘
                     │ (loaded once at startup)
                     ▼
┌──────────────────────────────────────────────────────┐
│              config/settings.py                      │
│   • Loads environment variables                      │
│   • Validates configuration                          │
│   • Exposes: AI_PROVIDER, API keys                   │
└────────────────────┬─────────────────────────────────┘
                     │ (referenced by)
                     ▼
┌──────────────────────────────────────────────────────┐
│         dependencies/ai_provider.py                  │
│   • Reads Settings.AI_PROVIDER                       │
│   • Instantiates service with API key:               │
│     GeminiService(api_key=Settings.GOOGLE_API_KEY)   │
└────────────────────┬─────────────────────────────────┘
                     │ (provides service instance)
                     ▼
┌──────────────────────────────────────────────────────┐
│                    app.py                            │
│   @post("/api/interpret-art",                        │
│         dependencies={"ai_service": Provide(...)})   │
│   • Litestar calls get_ai_service()                  │
│   • Injects result into handler                      │
└────────────────────┬─────────────────────────────────┘
                     │ (passes service instance)
                     ▼
┌──────────────────────────────────────────────────────┐
│         controllers/art_controller.py                │
│   interpret_art_handler(data, ai_service):           │
│     • Calls: ai_service.interpret_artwork_with_ai()  │
│     • Doesn't know which provider                    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              Service Classes                         │
│   ┌───────────────────────────────────────────────┐  │
│   │ class OpenAIService:                          │  │
│   │   def __init__(self, api_key: str)            │  │
│   │     self.client = OpenAI(api_key=api_key)     │  │
│   └───────────────────────────────────────────────┘  │
│   ┌───────────────────────────────────────────────┐  │
│   │ class GeminiService:                          │  │
│   │   def __init__(self, api_key: str)            │  │
│   │     genai.configure(api_key=api_key)          │  │
│   └───────────────────────────────────────────────┘  │
│   ┌───────────────────────────────────────────────┐  │
│   │ class AnthropicService:                       │  │
│   │   def __init__(self, api_key: str)            │  │
│   │     self.client = Anthropic(api_key=api_key)  │  │
│   └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘

📝 Note: Services NEVER import from .env or os.getenv()
         Configuration flows DOWN from Settings → Services
```

