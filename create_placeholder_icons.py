#!/usr/bin/env python3
"""
Create placeholder icons for the Floor Plan Drawing Application.
This script generates simple colored square PNG icons for all referenced icons.
"""

import os
from PIL import Image, ImageDraw
import sys

def create_placeholder_icon(name, color, size=32):
    """Create a simple colored square icon."""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a colored square with rounded corners effect
    margin = 2
    draw.rectangle([margin, margin, size-margin, size-margin], fill=color, outline=(0, 0, 0, 100))
    
    # Add a simple symbol based on the icon name
    center = size // 2
    if name == "open":
        # Simple folder symbol
        draw.rectangle([center-8, center-6, center+8, center+8], fill=(255, 255, 255, 200))
    elif name == "save":
        # Simple disk symbol
        draw.ellipse([center-8, center-8, center+8, center+8], fill=(255, 255, 255, 200))
    elif name == "load":
        # Simple arrow symbol
        draw.polygon([(center, center-8), (center-6, center+4), (center+6, center+4)], fill=(255, 255, 255, 200))
    elif name == "new_floor":
        # Simple plus symbol
        draw.rectangle([center-1, center-8, center+1, center+8], fill=(255, 255, 255, 200))
        draw.rectangle([center-8, center-1, center+8, center+1], fill=(255, 255, 255, 200))
    elif name in ["zoom_in", "zoom_out"]:
        # Magnifying glass symbol
        draw.ellipse([center-6, center-6, center+6, center+6], outline=(255, 255, 255, 200), width=2)
        if name == "zoom_in":
            draw.rectangle([center-1, center-4, center+1, center+4], fill=(255, 255, 255, 200))
            draw.rectangle([center-4, center-1, center+4, center+1], fill=(255, 255, 255, 200))
        else:
            draw.rectangle([center-4, center-1, center+4, center+1], fill=(255, 255, 255, 200))
    elif name == "fit_window":
        # Simple expand symbol
        draw.rectangle([center-6, center-6, center+6, center+6], outline=(255, 255, 255, 200), width=2)
    elif name == "select":
        # Simple cursor symbol
        draw.polygon([(center-6, center+6), (center+6, center+6), (center, center-6)], fill=(255, 255, 255, 200))
    elif name == "draw_room":
        # Simple square symbol
        draw.rectangle([center-6, center-6, center+6, center+6], outline=(255, 255, 255, 200), width=2)
    elif name == "draw_pathway":
        # Simple line symbol
        draw.line([center-8, center, center+8, center], fill=(255, 255, 255, 200), width=3)
    
    return img

def main():
    """Create all placeholder icons."""
    # Define colors for different icon types
    icon_colors = {
        "open": (70, 130, 180),  # Steel blue
        "save": (60, 179, 113),   # Medium sea green
        "load": (255, 140, 0),    # Dark orange
        "new_floor": (106, 90, 205),  # Slate blue
        "zoom_in": (119, 136, 153),   # Light slate gray
        "zoom_out": (119, 136, 153),  # Light slate gray
        "fit_window": (105, 105, 105), # Dim gray
        "select": (178, 34, 34),   # Fire brick
        "draw_room": (0, 128, 128), # Teal
        "draw_pathway": (128, 0, 128), # Purple
    }
    
    # Create icons directory if it doesn't exist
    icons_dir = "assets/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    created_count = 0
    for icon_name, color in icon_colors.items():
        icon_path = os.path.join(icons_dir, f"{icon_name}.png")
        
        if not os.path.exists(icon_path):
            try:
                icon_img = create_placeholder_icon(icon_name, color)
                icon_img.save(icon_path, "PNG")
                print(f"Created placeholder icon: {icon_path}")
                created_count += 1
            except Exception as e:
                print(f"Error creating icon {icon_name}: {e}")
        else:
            print(f"Icon already exists: {icon_path}")
    
    print(f"\nPlaceholder icons created: {created_count}")
    print("The UI should now load without icon-related errors.")

if __name__ == "__main__":
    main()
