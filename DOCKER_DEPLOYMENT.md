# Docker Deployment Guide for Sticker Processing Tool

This guide will help you deploy the Sticker Processing Tool on your Proxmox server using Docker.

## Prerequisites

- Proxmox server with Docker installed
- At least 2GB RAM available
- At least 5GB free disk space

## Quick Start

1. **Clone or copy the project files to your Proxmox server**

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Open your browser and go to `http://your-proxmox-ip:5000`
   - Upload images through the web interface
   - Download processed stickers as ZIP files

## Manual Docker Commands

If you prefer to use Docker directly instead of Docker Compose:

```bash
# Build the image
docker build -t sticker-processor .

# Run the container
docker run -d \
  --name sticker-processor \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/web_processed:/app/web_processed \
  sticker-processor
```

## Configuration

### Environment Variables

You can customize the application behavior with these environment variables:

- `FLASK_ENV`: Set to `production` for production deployment
- `MAX_CONTENT_LENGTH`: Maximum upload size (default: 50MB)

### Volumes

The application uses these volumes for persistent storage:

- `./uploads`: Temporary storage for uploaded files
- `./web_processed`: Storage for processed images and ZIP files

## Production Deployment

For production use on Proxmox:

1. **Use a reverse proxy (recommended):**
   - Install nginx or traefik
   - Configure SSL certificates
   - Set up proper domain routing

2. **Resource limits:**
   ```yaml
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
       reservations:
         memory: 512M
   ```

3. **Backup strategy:**
   - Regularly backup the `uploads` and `web_processed` directories
   - Consider using Proxmox backup features for the entire container

## Troubleshooting

### Common Issues

1. **Port 5000 already in use:**
   - Change the port mapping in docker-compose.yml: `- "8080:5000"`

2. **Permission issues with volumes:**
   - Ensure the host directories have proper permissions
   - Run: `chmod 755 uploads web_processed`

3. **Memory issues:**
   - The rembg library requires significant memory for image processing
   - Ensure at least 2GB RAM is available

4. **Slow processing:**
   - Image processing is CPU and memory intensive
   - Consider using a machine with more cores for better performance

### Logs

Check container logs:
```bash
docker-compose logs -f sticker-processor
```

## Security Considerations

- The application runs with default Flask settings
- For production, consider:
  - Setting a strong `SECRET_KEY`
  - Using HTTPS
  - Implementing authentication if needed
  - Limiting upload file types and sizes

## Updating

To update the application:

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```