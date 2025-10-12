# Wikilink Explanation with Context Caching

## Overview

This implementation allows users to click on wikilinks in artwork interpretations and receive in-depth, contextual explanations without reprocessing the original image. For Gemini, this uses Google's Context Caching API to maintain full visual context while reducing costs by 50-90%.

## New Endpoints

### 1. `POST /api/ai/interpret-with-cache`

Interprets artwork with caching enabled (recommended for Gemini users).

**Request:**
```bash
curl -X POST http://localhost:8000/api/ai/interpret-with-cache \
  -F "data=@artwork.jpg"
```

**Response:**
- Body: XML interpretation (same as regular `/interpret` endpoint)
- Header: `X-Cache-ID` containing the cache identifier (e.g., `artwork_abc123`)

**Note:** The frontend should save this cache ID for subsequent wikilink requests.

---

### 2. `POST /api/ai/explain-term`

Explains a wikilink term in the context of the original artwork.

**Request:**
```bash
curl -X POST http://localhost:8000/api/ai/explain-term \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Impressionism",
    "original_interpretation": "<article>...</article>",
    "cache_name": "artwork_abc123"
  }'
```

**Request Body:**
- `term` (required): The wikilink term to explain (e.g., "Impressionism", "chiaroscuro")
- `original_interpretation` (required): The full XML interpretation from the original request
- `cache_name` (optional): Cache ID from the `X-Cache-ID` header (enables image reuse for Gemini)

**Response:**
- Body: XML explanation focused on the term in the artwork's context

---

## How It Works

### Gemini (Full Caching Support)
1. **Initial Request:** Image + system prompt cached for 60 minutes
2. **Wikilink Click:** Reuses cached image + adds new prompt
3. **Result:** AI has full visual context, 50-90% cost reduction

### OpenAI (Automatic Caching)
1. **Initial Request:** Automatic caching for prompts >1024 tokens
2. **Wikilink Click:** Text-only context (image not reused)
3. **Result:** Still cheaper than reprocessing, but less context than Gemini

### Anthropic (Text-Only for Now)
1. **Initial Request:** Regular interpretation
2. **Wikilink Click:** Text-only context
3. **Result:** Good explanations based on original analysis text
4. **Note:** Anthropic supports prompt caching but not yet implemented

---

## Frontend Integration Example

```javascript
// Step 1: Upload artwork with caching
const formData = new FormData();
formData.append('data', imageFile);

const interpretResponse = await fetch('/api/ai/interpret-with-cache', {
  method: 'POST',
  body: formData
});

const interpretation = await interpretResponse.text(); // XML
const cacheId = interpretResponse.headers.get('X-Cache-ID');

// Step 2: Store interpretation and cache ID
sessionStorage.setItem('interpretation', interpretation);
sessionStorage.setItem('cacheId', cacheId);

// Step 3: When user clicks a wikilink
async function handleWikilinkClick(term) {
  const response = await fetch('/api/ai/explain-term', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      term: term,
      original_interpretation: sessionStorage.getItem('interpretation'),
      cache_name: sessionStorage.getItem('cacheId')
    })
  });
  
  const explanation = await response.text(); // XML
  return explanation;
}
```

---

## Cost Comparison

### Gemini with Caching
- Initial interpretation: ~$0.001-0.005 (depends on image size)
- Each wikilink explanation: ~$0.0001-0.0005 (90% cheaper with cache)

### Without Caching (reprocessing image)
- Initial interpretation: ~$0.001-0.005
- Each wikilink explanation: ~$0.001-0.005 (full cost every time)

**Example:** 5 wikilink clicks saves ~$0.02-0.10 per user session

---

## Cache Lifecycle

- **Duration:** 60 minutes (Gemini)
- **Storage:** In-memory (per service instance)
- **Fallback:** If cache expires or unavailable, automatically falls back to text-only context
- **Production:** Consider using Redis or similar for multi-instance deployments

---

## Provider Comparison

| Feature | Gemini | OpenAI | Anthropic |
|---------|--------|--------|-----------|
| Explicit Caching | ✅ Yes | ⚠️ Automatic | ⚠️ Not yet implemented |
| Image Reuse | ✅ Yes | ❌ No | ❌ No |
| Cost Savings | 50-90% | ~50% (automatic) | None yet |
| Cache Duration | 60 min | 5-10 min | N/A |
| Context Quality | Full visual | Text only | Text only |

---

## Testing

You can test the new endpoints with the existing `cat.jpg` file:

```bash
# Test with caching
curl -X POST http://localhost:8000/api/ai/interpret-with-cache \
  -F "data=@cat.jpg" \
  -i | grep -i "X-Cache-ID"

# Test explain-term (save the cache ID from above)
curl -X POST http://localhost:8000/api/ai/explain-term \
  -H "Content-Type: application/json" \
  -d '{
    "term": "composition",
    "original_interpretation": "<article><title>Test</title></article>",
    "cache_name": "artwork_abc123"
  }'
```

