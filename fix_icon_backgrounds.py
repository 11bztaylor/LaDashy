#!/usr/bin/env python3
"""
Fix icon backgrounds - make white backgrounds transparent
"""
import os
from PIL import Image
import numpy as np

LOGO_DIR = "homelab_wizard/assets/logos"

def make_background_transparent(image_path, threshold=240):
    """Convert white/light backgrounds to transparent"""
    try:
        img = Image.open(image_path).convert("RGBA")
        data = np.array(img)
        
        # Find pixels that are nearly white
        red, green, blue, alpha = data.T
        white_areas = (red > threshold) & (blue > threshold) & (green > threshold)
        
        # Make those pixels transparent
        data[..., :-1][white_areas.T] = (255, 255, 255)
        data[..., -1][white_areas.T] = 0
        
        # Save with transparency
        new_img = Image.fromarray(data)
        new_img.save(image_path)
        return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def process_all_logos():
    """Process all logo files"""
    if not os.path.exists(LOGO_DIR):
        print(f"Logo directory not found: {LOGO_DIR}")
        return
    
    processed = 0
    for filename in os.listdir(LOGO_DIR):
        if filename.endswith('.png') and not filename.endswith('_32.png'):
            filepath = os.path.join(LOGO_DIR, filename)
            if make_background_transparent(filepath):
                processed += 1
                print(f"✓ Processed {filename}")
                
                # Also process the 32px version
                small_path = filepath.replace('.png', '_32.png')
                if os.path.exists(small_path):
                    make_background_transparent(small_path)
    
    print(f"\nProcessed {processed} logos")

if __name__ == "__main__":
    process_all_logos()
