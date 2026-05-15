# Google Imagen 4 API

Generate images using Google's Imagen 4 API for presentation visuals.

## API Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}
```

## Request Format

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${GOOGLE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [{"prompt": "YOUR PROMPT HERE"}],
    "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
  }'
```

## Response Handling

```bash
# Save image from response
curl -s -X POST "..." | python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
open('output.png','wb').write(base64.b64decode(d['predictions'][0]['bytesBase64Encoded']))
"
```

## Recommended Prompts for All-Hands Decks

### Hero (Title Slide)
```
Abstract futuristic digital network with glowing blue and cyan nodes connected by streams of light, dark navy background, cinematic professional, minimal corporate tech aesthetic
```

### Growth
```
Rocket launching upward with bright orange flames against dark space background, growth and momentum, cinematic epic shot, minimal
```

### AI Brain
```
Glowing AI robot brain made of blue light circuits and neural networks, floating in dark space, futuristic technology concept, professional corporate tech aesthetic
```

### Target/Goal
```
Abstract target bullseye with glowing green rings and arrow hitting center, dark background, achievement success concept, minimal corporate
```

### Team/Celebration
```
Team of diverse professionals celebrating success with raised fists, silhouettes against bright blue and orange sunrise, victorious energy, cinematic
```

### Finale/Sunrise
```
Epic sunrise over mountains with golden light rays breaking through clouds, new beginning, hope and energy, cinematic inspiring, professional photography
```

## Best Practices

1. **Use 16:9 aspect ratio** for slide backgrounds
2. **Dark backgrounds** work better with light text overlays
3. **Minimal/abstract** imagery avoids distraction from text
4. **Avoid text in images** — Imagen sometimes generates distracting text
5. **Generate multiple options** if first result has issues

## Fallback Models

If Imagen 4 is unavailable:
- `imagen-4.0-fast-generate-001` — Faster, slightly lower quality
- `gemini-2.5-flash-image` — Gemini's image generation
