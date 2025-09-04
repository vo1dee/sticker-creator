#!/usr/bin/env python3
"""
Image Background Removal and Resizing Tool

This script monitors the 'new' folder for new image files, processes them by:
1. Removing backgrounds using rembg
2. Resizing to 512x512 pixels
3. Saving processed images to 'processed' folder
4. Moving original files to 'old' folder

Requirements:
- pip install rembg pillow watchdog

Usage:
    python main.py

The script runs continuously, monitoring the 'new' folder.
"""

import os
import sys
import time
import io
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageMath
import rembg
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    pass  # Will be checked later

def create_square_image(img, size=512):
    """
    Resize image to square while maintaining aspect ratio and centering.
    Fills background with transparency for PNG or white for other formats.
    """
    # Calculate scaling to fit within the square
    original_width, original_height = img.size
    scale = min(size / original_width, size / original_height)
    
    # Calculate new size maintaining aspect ratio
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    # Resize the image
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new square image with transparent background
    if img_resized.mode == 'RGBA':
        square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    else:
        square_img = Image.new('RGB', (size, size), (255, 255, 255))
    
    # Calculate position to center the image
    x = (size - new_width) // 2
    y = (size - new_height) // 2
    
    # Paste the resized image onto the square background
    if img_resized.mode == 'RGBA':
        square_img.paste(img_resized, (x, y), img_resized)
    else:
        square_img.paste(img_resized, (x, y))
    
    return square_img

def add_white_outline(img, outline_width=6):
    """
    Add a subtle beige-brown-gray outline around non-transparent pixels.
    outline_width in pixels (0.5mm ≈ 6px at 300 DPI)
    """
    if img.mode != 'RGBA':
        return img

    # Get the alpha channel
    alpha = img.split()[-1]

    # Expand the alpha channel to create the outline area
    expanded_alpha = alpha.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))

    # Create outline mask: expanded area minus original area
    outline_mask = ImageMath.unsafe_eval("max(a - b, 0)", a=expanded_alpha, b=alpha).convert('L')

    # Create subtle beige-brown-gray outline image
    outline_color = (235, 225, 215, 255)  # Subtle beige-brown-gray pastel
    outline_img = Image.new('RGBA', img.size, outline_color)

    # Composite: outline where mask is set, original image elsewhere
    result = Image.composite(outline_img, img, outline_mask)

    return result

def process_image(input_path, output_path, old_path):
    """
    Process a single image: remove background and resize to 512x512
    """
    try:
        print(f"Processing: {input_path.name}")

        # First, validate the input image
        try:
            with Image.open(input_path) as test_img:
                test_img.verify()  # Verify the image is not corrupted
        except Exception as e:
            print(f"✗ Invalid input image {input_path.name}: {str(e)}")
            return

        # Read the input image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        # Try background removal, fallback to original if it fails
        try:
            output_data = rembg.remove(input_data)
            if isinstance(output_data, bytes) and len(output_data) > 100:  # Basic validation
                print(f"✓ Background removal completed for {input_path.name}")
                img = Image.open(io.BytesIO(output_data))
            else:
                raise ValueError("Invalid rembg output")
        except Exception as e:
            print(f"⚠ Background removal failed for {input_path.name}: {str(e)}")
            print("   Falling back to original image processing...")
            # Fallback: use original image
            img = Image.open(input_path)

        # Convert to RGBA if not already (for transparency support)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Resize to 512x512 square
        square_img = create_square_image(img, 512)

        # Add subtle beige-brown-gray outline
        square_img = add_white_outline(square_img, 6)  # 6px ≈ 0.5mm at 300 DPI

        # Save the processed image
        square_img.save(output_path, 'PNG', optimize=True)
        print(f"✓ Saved processed: {output_path.name}")

        # Move original to old folder
        if isinstance(old_path, Path):
            input_path.rename(old_path)
            print(f"✓ Moved original to: {old_path.name}")
        else:
            print(f"✗ Failed to move {input_path.name}: invalid path")

    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {str(e)}")

class ImageHandler(FileSystemEventHandler):
    def __init__(self, new_folder, processed_folder, old_folder):
        self.new_folder = Path(new_folder)
        self.processed_folder = Path(processed_folder)
        self.old_folder = Path(old_folder)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}

    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_formats:
                print(f"New image detected: {file_path.name}")
                self.process_file(file_path)

    def process_file(self, input_path):
        # Ensure input_path is a Path object
        if not isinstance(input_path, Path):
            input_path = Path(input_path)

        # Ensure name is string
        name = str(input_path.name)
        stem = str(input_path.stem)

        # Create output filename (always save as PNG for transparency)
        output_filename = stem + "_processed.png"
        output_path = self.processed_folder / output_filename
        old_path = self.old_folder / name

        process_image(input_path, output_path, old_path)

def main():
    # Define folders
    base_dir = Path.cwd()
    new_folder = base_dir / "new"
    processed_folder = base_dir / "processed"
    old_folder = base_dir / "old"

    # Create folders if they don't exist
    new_folder.mkdir(exist_ok=True)
    processed_folder.mkdir(exist_ok=True)
    old_folder.mkdir(exist_ok=True)

    print("Monitoring 'new' folder for new images...")
    print(f"Processed images will be saved to: {processed_folder}")
    print(f"Original images will be moved to: {old_folder}")
    print("Press Ctrl+C to stop.")

    # Process any existing files in the new folder first
    event_handler = ImageHandler(new_folder, processed_folder, old_folder)
    print("Processing existing files in 'new' folder...")
    for file_path in new_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in event_handler.supported_formats:
            print(f"Found existing image: {file_path.name}")
            event_handler.process_file(file_path)
    print("Finished processing existing files.")

    # Set up the observer
    observer = Observer()
    observer.schedule(event_handler, str(new_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped.")
    observer.join()

if __name__ == "__main__":
    # Import io here to avoid import error if not needed
    import io

    # Check if required packages are installed
    try:
        import rembg
        from PIL import Image
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError as e:
        print("Error: Required packages not installed.")
        print("Please run: pip install rembg pillow watchdog")
        sys.exit(1)

    main()
