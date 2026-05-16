#!/usr/bin/env python3
"""
Remove white background from logo images.
Usage: python3 make_transparent.py input.jpg output.png
"""

import sys
from PIL import Image

def make_transparent(input_path: str, output_path: str, threshold: int = 240):
    """Remove white/near-white pixels from image."""
    img = Image.open(input_path).convert('RGBA')
    pixels = list(img.getdata())
    
    new_pixels = []
    for r, g, b, a in pixels:
        if r > threshold and g > threshold and b > threshold:
            new_pixels.append((255, 255, 255, 0))  # Transparent
        else:
            new_pixels.append((r, g, b, a))
    
    img.putdata(new_pixels)
    img.save(output_path, 'PNG')
    print(f"✓ Saved {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 make_transparent.py input.jpg output.png [threshold]")
        sys.exit(1)
    
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 240
    make_transparent(sys.argv[1], sys.argv[2], threshold)
