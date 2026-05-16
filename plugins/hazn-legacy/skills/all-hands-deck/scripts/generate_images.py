#!/usr/bin/env python3
"""
Generate images for All Hands deck using Google Imagen 4 API.
Usage: python3 generate_images.py --api-key YOUR_KEY --output-dir ./deck-images
"""

import argparse
import base64
import json
import os
import urllib.request

PROMPTS = {
    "hero": "Abstract futuristic digital network with glowing blue and cyan nodes connected by streams of light, dark navy background, cinematic professional, minimal corporate tech aesthetic",
    "growth": "Rocket launching upward with bright orange flames against dark space background, growth and momentum, cinematic epic shot, minimal",
    "ai-brain": "Glowing AI robot brain made of blue light circuits and neural networks, floating in dark space, futuristic technology concept, professional corporate tech aesthetic",
    "target": "Abstract target bullseye with glowing green rings and arrow hitting center, dark background, achievement success concept, minimal corporate",
    "team": "Team of diverse professionals celebrating success with raised fists, silhouettes against bright blue and orange sunrise, victorious energy, cinematic",
    "finale": "Epic sunrise over mountains with golden light rays breaking through clouds, new beginning, hope and energy, cinematic inspiring, professional photography",
}

def generate_image(api_key: str, prompt: str, output_path: str):
    """Generate a single image using Imagen 4 API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
    
    data = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.load(resp)
    
    img_data = base64.b64decode(result["predictions"][0]["bytesBase64Encoded"])
    
    with open(output_path, "wb") as f:
        f.write(img_data)
    
    print(f"✓ Saved {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate All Hands deck images")
    parser.add_argument("--api-key", required=True, help="Google API key")
    parser.add_argument("--output-dir", default="./deck-images", help="Output directory")
    parser.add_argument("--images", nargs="*", choices=list(PROMPTS.keys()), 
                        help="Specific images to generate (default: all)")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    images_to_generate = args.images or list(PROMPTS.keys())
    
    for name in images_to_generate:
        prompt = PROMPTS[name]
        output_path = os.path.join(args.output_dir, f"{name}.png")
        print(f"Generating {name}...")
        try:
            generate_image(args.api_key, prompt, output_path)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

if __name__ == "__main__":
    main()
