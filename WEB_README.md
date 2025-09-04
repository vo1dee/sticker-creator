# Sticker Processing Web Interface

A beautiful web interface for the sticker processing tool that allows you to upload multiple images and download processed stickers as a ZIP archive.

## Features

- 🌐 **Web Interface**: Clean, modern web UI with drag-and-drop upload
- 📦 **Batch Processing**: Upload multiple images at once (up to 20 files)
- 🎨 **AI Background Removal**: Automatic background removal using rembg
- 📐 **Auto Resize**: Images optimized to 512x512 pixels
- 🖼️ **Subtle Outline**: Adds a refined beige-brown-gray outline
- 📥 **ZIP Download**: Download all processed images in a single archive
- ⚡ **Fast Processing**: Efficient batch processing with progress feedback

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web App

```bash
python app.py
```

### 3. Open in Browser

Visit `http://localhost:5000` in your web browser.

## Usage

1. **Upload Images**: Drag and drop images or click to browse files
2. **Supported Formats**: PNG, JPG, JPEG, BMP, TIFF, TIF, WebP
3. **File Limits**:
   - Maximum 20 files per upload
   - Maximum 10MB per file
   - Total upload limit: 50MB
4. **Processing**: Images are automatically processed with:
   - Background removal
   - Resize to 512x512
   - Subtle outline addition
5. **Download**: Get all processed images as a ZIP archive

## File Structure

```
stickers/
├── app.py                 # Flask web application
├── main.py               # Original processing script
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── results.html
├── static/               # Static files (CSS, JS, images)
├── uploads/              # Temporary upload storage
├── web_processed/        # Processed images for web app
├── processed/            # Processed images from CLI
├── new/                  # Images for CLI processing
├── old/                  # Original images from CLI
└── requirements.txt      # Python dependencies
```

## Technical Details

- **Framework**: Flask web framework
- **Image Processing**: PIL (Pillow) with rembg for background removal
- **File Handling**: Secure file uploads with validation
- **Archive Creation**: ZIP files with processed images
- **UI**: Bootstrap 5 with custom styling and Font Awesome icons

## API Endpoints

- `GET /` - Main upload page
- `POST /upload` - Handle file uploads and processing
- `GET /download/<session_id>/<filename>` - Download ZIP archive

## Error Handling

The web app includes comprehensive error handling for:
- Invalid file types
- File size limits exceeded
- Processing errors
- Missing files
- Network issues

## Security Features

- Secure filename handling
- File type validation
- File size limits
- Session-based file management
- CSRF protection via Flask-WTF

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Troubleshooting

### Common Issues

1. **Flask not found**: Run `pip install flask`
2. **Port already in use**: Change port in `app.run(port=5001)`
3. **Large files failing**: Check `MAX_CONTENT_LENGTH` setting
4. **Processing errors**: Check console output for detailed error messages

### Performance Tips

- Process images in smaller batches for better performance
- Use high-quality images for best results
- Close browser tabs when done to free up server resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. See the main README for license details.