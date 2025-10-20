# JWT Authentication Testing Guide

This guide explains how to test the JWT authentication flow with Supabase in the Art Backend API.

## Overview

The application uses Litestar's JWT authentication with Supabase integration:

- **JWT Secret**: Uses `SUPABASE_JWT_SECRET` from environment variables
- **Token Expiration**: 1 hour (3600 seconds)
- **Public Endpoints**: `/health`, `/api/artwork`, `/api/expansion`
- **Protected Endpoints**: All `/api/ai/*` and `/api/user/*` endpoints require valid JWT tokens

## Prerequisites

1. **Supabase Configuration**: Ensure your `.env` file contains:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   ```

2. **Running Server**: Start your API server:
   ```bash
   uvicorn app:app --reload
   ```

## Testing Methods

### 1. Automated Testing Script

Use the provided test script for comprehensive JWT testing:

```bash
# Test without token (public endpoints and auth failures)
python test_jwt_auth.py

# Test with a valid Supabase JWT token
python test_jwt_auth.py YOUR_SUPABASE_JWT_TOKEN
```

The script will test:
- ✅ Public endpoints (should work without auth)
- ❌ Protected endpoints without token (should return 401)
- ❌ Protected endpoints with invalid tokens (should return 401)
- ✅ Protected endpoints with valid token (should work)

### 2. Get Supabase JWT Token

Use the helper script to get a valid JWT token:

```bash
python get_supabase_token.py
```

This script will:
1. Prompt for your Supabase email/password
2. Authenticate with Supabase
3. Retrieve the JWT token
4. Save it to `supabase_token.txt` for easy testing

### 3. Manual Testing with curl

#### Test Public Endpoints (No Auth Required)
```bash
# Health check
curl http://localhost:8000/health

# Public artwork endpoint
curl http://localhost:8000/api/artwork
```

#### Test Protected Endpoints (Auth Required)
```bash
# Without token (should return 401)
curl http://localhost:8000/api/ai/artwork/explain

# With valid token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/ai/artwork/explain

# With invalid token (should return 401)
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:8000/api/ai/artwork/explain
```

### 4. Testing with Postman

1. **Create a new request**
2. **Set the URL** to your protected endpoint (e.g., `http://localhost:8000/api/ai/artwork/explain`)
3. **Add Authorization header**:
   - Type: `Bearer Token`
   - Token: Your Supabase JWT token
4. **Send the request**

## Expected Responses

### Successful Authentication (200)
```json
{
  "message": "Success",
  "data": "..."
}
```

### Unauthorized (401)
```json
{
  "detail": "Authentication required"
}
```

### Method Not Allowed (405)
For GET requests on POST-only endpoints:
```json
{
  "detail": "Method not allowed"
}
```

## Troubleshooting

### Common Issues

1. **"Invalid token" errors**
   - Check that `SUPABASE_JWT_SECRET` matches your Supabase project's JWT secret
   - Verify the token hasn't expired (1-hour default)
   - Ensure the token is properly formatted

2. **"Connection refused" errors**
   - Make sure your API server is running on `http://localhost:8000`
   - Check if the port is correct

3. **"Supabase authentication failed"**
   - Verify your Supabase URL and API key
   - Check if the user account exists and is active
   - Ensure RLS (Row Level Security) policies allow access

### Debug Mode

Enable debug logging in your application by setting:
```python
# In app.py
debug=True  # Already enabled
```

This will provide detailed error messages in the console.

## Token Structure

Supabase JWT tokens contain:
- `sub`: User ID (used by `retrieve_user_handler`)
- `iss`: Issuer (Supabase URL)
- `aud`: Audience
- `exp`: Expiration timestamp
- `email`: User email
- `role`: User role (authenticated/anonymous)

## Security Considerations

1. **Never commit JWT tokens** to version control
2. **Use HTTPS** in production
3. **Validate token expiration** on the client side
4. **Implement proper error handling** for expired tokens
5. **Use environment variables** for sensitive configuration

## Integration with Frontend

For frontend integration, you'll typically:

1. **Authenticate with Supabase** using their client library
2. **Store the JWT token** in localStorage or sessionStorage
3. **Include the token** in API requests:
   ```javascript
   const token = localStorage.getItem('supabase_token');
   fetch('/api/ai/artwork/explain', {
     headers: {
       'Authorization': `Bearer ${token}`
     }
   });
   ```

## Testing Checklist

- [ ] Public endpoints work without authentication
- [ ] Protected endpoints return 401 without token
- [ ] Protected endpoints return 401 with invalid token
- [ ] Protected endpoints work with valid token
- [ ] Token expiration is handled correctly
- [ ] User ID is properly extracted from token
- [ ] Error messages are informative but not revealing
- [ ] CORS is configured correctly for frontend requests

## Next Steps

1. **Set up Supabase project** with proper authentication
2. **Configure RLS policies** for your database tables
3. **Implement user registration/login** in your frontend
4. **Add token refresh logic** for long-lived sessions
5. **Set up monitoring** for authentication failures
