# Logging Configuration

This document explains the logging setup for the Art Backend API.

## Overview

The application now uses **Litestar's native logging and exception handling** instead of custom middleware. This provides:

- ✅ Automatic exception logging with full stack traces
- ✅ Structured logging throughout the application
- ✅ Custom XML error responses for API clients
- ✅ Request/response flow tracking

## Configuration

### Logging Setup (`app.py`)

The application uses Litestar's `LoggingConfig` with the following settings:

```python
logging_config = LoggingConfig(
    root={"level": logging.getLevelName(logging.INFO), "handlers": ["console"]},
    formatters={
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    loggers={
        "app": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "litestar": {"level": "INFO", "handlers": ["console"], "propagate": False},
    }
)
```

### Exception Handlers (`middleware/error_handler.py`)

Instead of custom middleware, we use Litestar's exception handlers defined in `error_handler.py`:

- **ValueError** → `value_error_handler()` → Returns 400 Bad Request with XML error
- **Exception** (generic) → `generic_exception_handler()` → Returns 500 Internal Server Error with XML error

These handlers are imported in `app.py` and registered with Litestar. Litestar automatically logs all exceptions with full tracebacks before calling the exception handler.

## What Gets Logged

### 1. Application Startup
```
INFO:     Application startup complete.
```

### 2. Incoming Requests
```
2025-10-11 15:30:45 - controllers.art_controller - INFO - Received art interpretation request: filename=artwork.jpg, content_type=image/jpeg
2025-10-11 15:30:45 - controllers.art_controller - INFO - Read uploaded file: 245678 bytes
```

### 3. Image Processing
```
2025-10-11 15:30:45 - utils.image_processor - INFO - Starting image validation (received 245678 bytes)
2025-10-11 15:30:45 - utils.image_processor - INFO - Image opened successfully: format=JPEG, size=(1920, 1080), mode=RGB
2025-10-11 15:30:45 - utils.image_processor - INFO - Image processed successfully (198234 bytes)
```

### 4. AI Service Calls
```
2025-10-11 15:30:45 - services.gemini_service - INFO - Starting Gemini API request for artwork interpretation
2025-10-11 15:30:45 - services.gemini_service - INFO - Image loaded: size=(1920, 1080), mode=RGB
2025-10-11 15:30:45 - services.gemini_service - INFO - Sending request to Gemini API...
2025-10-11 15:30:48 - services.gemini_service - INFO - Received response from Gemini API
2025-10-11 15:30:48 - services.gemini_service - INFO - XML response cleaned and validated
```

### 5. Successful Responses
```
2025-10-11 15:30:48 - controllers.art_controller - INFO - Successfully generated art interpretation response
INFO:     127.0.0.1:59523 - "POST /api/interpret-art HTTP/1.1" 200 OK
```

### 6. Validation Errors (400)
```
2025-10-11 15:30:45 - utils.image_processor - ERROR - Image processing failed: cannot identify image file <_io.BytesIO object at 0x...>
Traceback (most recent call last):
  File "/Users/eduardo/art-backend/utils/image_processor.py", line 29, in validate_and_process_image
    img = Image.open(io.BytesIO(image_data))
  ...
PIL.UnidentifiedImageError: cannot identify image file
INFO:     127.0.0.1:59523 - "POST /api/interpret-art HTTP/1.1" 400 Bad Request
```

### 7. Server Errors (500)
```
2025-10-11 15:30:45 - services.gemini_service - ERROR - Error in Gemini API call: API key not found
Traceback (most recent call last):
  File "/Users/eduardo/art-backend/services/gemini_service.py", line 68, in interpret_artwork_with_ai
    response = model.generate_content([full_prompt, image])
  ...
Exception: API key not found
INFO:     127.0.0.1:59523 - "POST /api/interpret-art HTTP/1.1" 500 Internal Server Error
```

## Log Levels

The application uses these log levels:

- **INFO**: Normal flow of operations (requests, successful processing)
- **WARNING**: Validation errors and client-side issues
- **ERROR**: Server errors and exceptions (always includes stack trace)
- **DEBUG**: Detailed debugging information (set level to DEBUG to enable)

## Changing Log Level

### For Development (more verbose):
Edit `app.py` and change:
```python
root={"level": logging.getLevelName(logging.DEBUG), "handlers": ["console"]},
```

### For Production (less verbose):
```python
root={"level": logging.getLevelName(logging.WARNING), "handlers": ["console"]},
```

## Viewing Logs in Production

When running with uvicorn:
```bash
# Default (logs to console)
uvicorn app:app --host 0.0.0.0 --port 8000

# Save logs to file
uvicorn app:app --host 0.0.0.0 --port 8000 2>&1 | tee app.log

# Run in background with logs
uvicorn app:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

## Benefits of This Approach

1. **Litestar handles logging automatically** - Exception stack traces are logged by the framework
2. **Custom error responses** - Clients still receive XML error messages
3. **Separation of concerns** - Exception handlers focus on responses, Litestar handles logging
4. **Better debugging** - Full context with file names, line numbers, and stack traces
5. **Production ready** - Can easily integrate with log aggregation services

## Troubleshooting

If you don't see logs:
1. Check that `debug=True` in the Litestar app configuration
2. Verify `logging_config` is passed to the Litestar constructor
3. Check console output is not being suppressed
4. Try setting log level to DEBUG for more verbose output

## Example Error Output

When an error occurs, you'll see:

```
2025-10-11 15:30:45 - services.gemini_service - ERROR - Error in Gemini API call: 'NoneType' object has no attribute 'text'
Traceback (most recent call last):
  File "/Users/eduardo/art-backend/services/gemini_service.py", line 72, in interpret_artwork_with_ai
    raw_content = response.text
AttributeError: 'NoneType' object has no attribute 'text'
```

This tells you:
- **When**: 2025-10-11 15:30:45
- **Where**: services.gemini_service
- **What**: Error in Gemini API call
- **Why**: AttributeError with full stack trace
- **Which line**: Line 72 in gemini_service.py

