from PIL import Image, ImageDraw

def make_circle(img_path, output_path):
    # Open the image and convert to RGBA
    img = Image.open(img_path).convert("RGBA")
    
    # Make it a square
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    
    # Crop to a square
    img = img.crop((left, top, right, bottom))
    
    # Create the circular mask
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, min_dim, min_dim), fill=255)
    
    # Apply the mask
    result = Image.new("RGBA", img.size)
    result.paste(img, (0, 0), mask)
    
    # Optional: resize to standard favicon size (e.g. 128x128)
    result = result.resize((128, 128), Image.Resampling.LANCZOS)
    
    # Save as PNG to preserve transparency
    result.save(output_path, "PNG")

if __name__ == "__main__":
    make_circle("logo.jpeg", "logo.png")
