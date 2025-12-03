from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    # Settings
    size = (512, 512)
    color = "#667FEA"
    text = "◈"
    output_path = "src/assets/favicon.png"

    # Create transparent image
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load font - try to find a system font or use default
    # Increasing font size to fill more of the canvas
    try:
        # Try to use a font that supports the symbol. 
        # DejaVuSans is common in Linux containers.
        # Increased size from 400 to 550 to minimize padding
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 550)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 550)
        except IOError:
            # Fallback to default
            print("Warning: Could not load specific font, using default.")
            font = ImageFont.load_default()

    # Calculate text position to center it
    # getbbox returns (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center exactly
    x = (size[0] - text_width) / 2 - bbox[0]
    y = (size[1] - text_height) / 2 - bbox[1]

    # Draw text
    draw.text((x, y), text, font=font, fill=color)

    # Save
    img.save(output_path)
    print(f"Favicon saved to {output_path}")

if __name__ == "__main__":
    create_favicon()
