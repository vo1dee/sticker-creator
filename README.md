# Image Background Removal and Sticker Generator

This Python script monitors the `new/` folder for new image files, automatically processes them by removing backgrounds using AI, resizing to 512x512 pixels, and organizing the results.

## Features

- **Real-time Monitoring**: Continuously watches the `new/` folder for new image files
- **Background Removal**: Uses AI-powered background removal with rembg (with fallback)
- **Automatic Resizing**: Converts images to 512x512 pixel squares with proper centering
- **File Organization**: Moves processed images to `processed/` and originals to `old/`
- **Robust Processing**: Falls back to original image if background removal fails
- **Supported Formats**: JPG, JPEG, PNG, BMP, TIFF, TIF, WEBP

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure the following folders exist (they will be created automatically if missing):
   - `new/` - Place new images here
   - `processed/` - Processed stickers will be saved here
   - `old/` - Original images will be moved here after processing

2. Run the script:
   ```bash
   python main.py
   ```

3. The script will run continuously. Add image files to the `new/` folder and they will be automatically processed.

4. To stop the script, press `Ctrl+C`.

## Dependencies

- `rembg` - AI-powered background removal
- `pillow` - Image processing
- `watchdog` - File system monitoring
- `onnxruntime` - Required by rembg for AI inference

## Troubleshooting

If you encounter a `ModuleNotFoundError` for `onnxruntime`, try installing it separately:
```bash
pip install onnxruntime
```

## Project Structure

```
stikers/
├── main.py              # Main script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── AGENTS.md           # Development guidelines
├── .gitignore          # Git ignore rules
├── new/                # Input folder (monitor this)
├── processed/          # Output folder (processed stickers)
└── old/                # Archive folder (original images)
```

## License

This project is open source. Feel free to use and modify as needed.