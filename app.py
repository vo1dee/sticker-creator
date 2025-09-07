#!/usr/bin/env python3
"""
Flask Web Interface for Sticker Processing Tool

This web app provides a user-friendly interface to:
1. Upload multiple images
2. Process them with background removal and outline
3. Download processed images as a ZIP archive

Usage:
    python app.py

Then visit http://localhost:5000 in your browser
"""

import os
import uuid
import zipfile
import tempfile
from pathlib import Path
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import sys

# Import our existing image processing functions
from main import process_image, create_square_image, add_white_outline

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'web_processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.secret_key = 'sticker-processing-secret-key'

# Create necessary directories
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(PROCESSED_FOLDER).mkdir(exist_ok=True)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'service': 'sticker-processor', 'version': '1.0.0'}

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and processing"""
    if 'files' not in request.files:
        flash('No files part in the request', 'error')
        return redirect(request.url)

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(request.url)

    # Validate file count
    if len(files) > 20:
        flash('Maximum 20 files allowed at once', 'error')
        return redirect(request.url)

    # Create unique session ID for this batch
    session_id = str(uuid.uuid4())
    session_upload_dir = Path(UPLOAD_FOLDER) / session_id
    session_processed_dir = Path(PROCESSED_FOLDER) / session_id

    session_upload_dir.mkdir(exist_ok=True)
    session_processed_dir.mkdir(exist_ok=True)

    processed_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Check file size (max 10MB per file)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning

            if file_size > 10 * 1024 * 1024:  # 10MB
                flash(f'File {filename} is too large (max 10MB)', 'error')
                continue

            upload_path = session_upload_dir / filename
            processed_path = session_processed_dir / f"{Path(filename).stem}_processed.png"

            try:
                # Save uploaded file
                file.save(upload_path)

                # Process the image
                process_image(upload_path, processed_path, None)
                processed_files.append(processed_path.name)
                print(f"✓ Processed: {filename}")
            except Exception as e:
                error_msg = f'Error processing {filename}: {str(e)}'
                print(f"✗ {error_msg}")
                flash(error_msg, 'error')
        else:
            flash(f'Invalid file type: {file.filename}', 'error')

    if processed_files:
        # Create ZIP archive
        zip_path = session_processed_dir / f"processed_stickers_{session_id[:8]}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for processed_file in processed_files:
                file_path = session_processed_dir / processed_file
                zipf.write(file_path, processed_file)

        return render_template('results.html',
                             session_id=session_id,
                             processed_count=len(processed_files),
                             zip_filename=zip_path.name)
    else:
        flash('No files were successfully processed')
        return redirect(url_for('index'))

@app.route('/download/<session_id>/<filename>')
def download_zip(session_id, filename):
    """Download the processed images ZIP file"""
    zip_path = Path(PROCESSED_FOLDER) / session_id / filename

    if zip_path.exists():
        return send_file(zip_path, as_attachment=True, download_name=filename)
    else:
        flash('File not found')
        return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 Starting Sticker Processing Web App...")
    print("📱 Visit http://localhost:5000 in your browser")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    print("📦 Processed folder:", PROCESSED_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=5000)