# AGENTS.md - Development Guidelines

## Build/Lint/Test Commands
- **Run script**: `python main.py` (monitors 'new' folder continuously)
- **Install dependencies**: `pip install -r requirements.txt`
- **Lint**: `python -m flake8 main.py` (if flake8 installed)
- **Type check**: `python -m mypy main.py` (if mypy installed)
- **Test single function**: `python -c "from main import create_square_image; print('Function works')"`

## Logging Commands
- **View application logs**: `tail -f logs/app.log`
- **View error logs**: `tail -f logs/error.log`
- **View processing logs**: `tail -f logs/processing.log`
- **View access logs**: `tail -f logs/access.log`
- **Check log files**: `ls -la logs/`
- **Docker container logs**: `docker-compose logs -f sticker-processor`

## Project Files
- `requirements.txt` - All Python dependencies
- `README.md` - Project documentation and usage instructions
- `.gitignore` - Git ignore rules for Python projects
- `AGENTS.md` - This file with development guidelines

## Code Style Guidelines
- **Imports**: Standard library first, then third-party. Use `from pathlib import Path`
- **Naming**: snake_case for functions/variables, PascalCase for classes (if any)
- **Types**: Use type hints for function parameters and return values
- **Error handling**: Use try/except blocks with specific exception types
- **Docstrings**: Include docstrings for all functions explaining purpose and parameters
- **File operations**: Use `pathlib.Path` instead of string paths
- **String formatting**: Use f-strings for dynamic strings
- **Function length**: Keep functions focused on single responsibilities
- **Constants**: Use UPPER_CASE for magic numbers and configuration values