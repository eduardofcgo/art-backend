# Grounding DINO Integration

Precise spatial localization using Grounding DINO on Replicate.

## Overview

Instead of having the LLM guess coordinates (which it's bad at), we use a two-stage approach:

1. **LLM Stage**: Generates interpretive content + simple visual queries
2. **Vision Stage**: Grounding DINO locates those elements precisely

## How It Works

### Stage 1: LLM Generates Queries

The LLM analyzes the artwork and generates details with `query` attributes:

```xml
<details>
  <detail query="woman's face" title="Psychological Alienation">
    This deliberate avoidance of direct eye contact symbolizes...
  </detail>
  <detail query="red brushstrokes upper right" title="Emotional Dissonance">
    The jarring red tones signal passion and violence...
  </detail>
</details>
```

**Query Guidelines:**
- Keep it simple and literal (2-6 words)
- Describe what's visually there, not what it means
- Good: "face looking left", "dark shadow area", "red brushstrokes"
- Bad: "alienation", "mortality", "symbolism"

### Stage 2: Grounding DINO Localizes

Each query is sent to Grounding DINO which returns:
- Bounding box coordinates
- Center point (x%, y%)
- Confidence score

The hotspots then appear at the precise locations!

## Setup

### 1. Get Replicate API Token

```bash
# Sign up at https://replicate.com
# Get your API token from https://replicate.com/account/api-tokens

export REPLICATE_API_TOKEN=r8_your_token_here
```

### 2. Install Dependencies

```bash
pip install replicate
```

### 3. Run with Grounding

```bash
# Without grounding (fast, uses center point fallback)
python test_api.py artwork.jpg

# With grounding (slower, precise localization)
python test_api.py artwork.jpg --ground
```

## Usage

### Basic (No Grounding)

```bash
python test_api.py cat.jpg
```

- Fast
- Free
- Uses center point (50%, 50%) for all details
- Good enough for many cases

### With Grounding DINO

```bash
python test_api.py cat.jpg --ground
```

- Takes ~5-10 seconds per image
- Uses Replicate API (~$0.001-0.01 per image)
- Precise localization
- Shows confidence scores

### Example Output

```
🔍 Localizing details with Grounding DINO...
✅ Localized 12 details
   ✓ Psychological Alienation: (45.2%, 28.3%) conf=0.89
   ✓ Emotional Dissonance: (72.1%, 35.7%) conf=0.76
   ⚠ Abstract Form: (50.0%, 50.0%) conf=0.12
   ✓ Shadow Play: (18.5%, 67.2%) conf=0.82
```

## How Queries Work

### Good Queries

These work well with Grounding DINO:

✅ **Objects**: "woman", "face", "hand", "flower", "building"
✅ **Colors + Objects**: "red dress", "blue sky", "dark shadow"
✅ **Positions**: "face in center", "figure on left", "background landscape"
✅ **Visual Features**: "brushstrokes", "geometric shapes", "textured area"

### Bad Queries

These don't work well:

❌ **Abstract**: "alienation", "emotion", "meaning"
❌ **Art Terms**: "chiaroscuro", "sfumato", "impasto"
❌ **Too Vague**: "composition", "style", "technique"
❌ **Too Long**: Full sentences or detailed descriptions

### Tips for Better Queries

1. **Be specific**: "woman's face" > "person"
2. **Add location if ambiguous**: "face on left" > "face" (if there are multiple faces)
3. **Use visible features**: "red area" > "warm tones"
4. **Keep it short**: 2-4 words is ideal

## Cost & Performance

### Replicate Pricing

- **Grounding DINO**: ~$0.001-0.005 per query
- **Per artwork**: ~$0.01-0.05 (for 10-12 details)
- **Free tier**: 100 predictions/month

### Performance

- **Without grounding**: Instant
- **With grounding**: 5-10 seconds per artwork
- **Accuracy**: 70-90% depending on query quality

## Fallback Behavior

If Grounding DINO can't find something:
- Confidence score < 0.3 → Shows warning ⚠
- Falls back to center position (50%, 50%)
- Still displays interpretation (most important part!)

## Integration in Production

### Option 1: On-Demand (Current)

User runs with `--ground` flag when they want precise localization.

**Pros**: 
- No extra cost unless requested
- Fast for basic usage

**Cons**:
- User needs Replicate token
- Extra step

### Option 2: Backend Endpoint

Add an endpoint that automatically uses Grounding DINO:

```python
@app.post("/api/ai/artwork/explain-with-grounding")
async def explain_with_grounding(data: UploadFile):
    # Generate interpretation
    xml = await generate_interpretation(data)
    
    # Localize with Grounding DINO
    coordinates = grounding_service.localize_from_xml(image, xml)
    
    # Return with precise coordinates
    return add_coordinates_to_xml(xml, coordinates)
```

**Pros**:
- Seamless for users
- Centralized API token

**Cons**:
- Costs per request
- Slower response

### Option 3: Batch Processing

Pre-process all artworks with Grounding DINO and cache results.

**Pros**:
- Fast for users
- Can optimize costs

**Cons**:
- Requires storage
- Upfront processing

## Example: Full Workflow

```bash
# 1. Generate interpretation with queries
python test_api.py starry_night.jpg

# Output includes queries:
# <detail query="swirling sky" title="Cosmic Turbulence">...</detail>
# <detail query="cypress tree" title="Natural Monument">...</detail>

# 2. Localize precisely
python test_api.py starry_night.jpg --ground

# Output shows:
# ✓ Cosmic Turbulence: (52.3%, 28.7%) conf=0.84
# ✓ Natural Monument: (73.1%, 65.4%) conf=0.91

# 3. Open HTML to see precise hotspots
open interpretation_starry_night_*.html
```

## Troubleshooting

### "Replicate API token not found"

```bash
export REPLICATE_API_TOKEN=r8_your_token
# Or add to .env file:
echo "REPLICATE_API_TOKEN=r8_your_token" >> .env
```

### "Low confidence scores"

- Queries may be too abstract
- Try simpler, more concrete descriptions
- Add location hints: "face on left" vs "face"

### "No detection found"

- Element might not be prominent enough
- Try broader query: "figure" instead of "person's left hand"
- Falls back to center - interpretation still works!

### "ImportError: No module named 'replicate'"

```bash
pip install replicate
```

## Model Details

- **Model**: `adirik/grounding-dino`
- **Input**: Image + text query
- **Output**: Bounding boxes with confidence scores
- **Capabilities**: Open-vocabulary object detection
- **Languages**: Works best with English

## Future Improvements

1. **Caching**: Store results to avoid re-computing
2. **Confidence Filtering**: Only use high-confidence detections
3. **Multiple Detections**: Handle cases with multiple matches
4. **Segmentation**: Use Grounded-SAM for pixel-perfect masks
5. **Batch API**: Process multiple queries in one call

