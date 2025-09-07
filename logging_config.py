#!/usr/bin/env python3
"""
Logging Configuration for Sticker Processing Tool

This module provides centralized logging configuration for the application,
including file handlers, formatters, and structured logging support.
"""

import os
import logging
import logging.handlers
from pathlib import Path
# Try to import JSON logger, fallback to standard if not available
try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    try:
        import jsonlogger
        HAS_JSON_LOGGER = True
    except ImportError:
        HAS_JSON_LOGGER = False
        jsonlogger = None
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create logs directory
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def get_log_level():
    """Get log level from environment variable"""
    level = os.getenv('LOG_LEVEL', 'INFO').upper()
    return LOG_LEVELS.get(level, logging.INFO)

def get_log_format():
    """Get log format from environment variable"""
    return os.getenv('LOG_FORMAT', 'json').lower()

def create_json_formatter():
    """Create JSON formatter for structured logging"""
    if HAS_JSON_LOGGER and jsonlogger:
        return jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Fallback to human-readable formatter if JSON logger not available
        return create_human_formatter()

def create_human_formatter():
    """Create human-readable formatter"""
    return logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def setup_logging():
    """Setup comprehensive logging configuration"""

    # Get configuration from environment
    log_level = get_log_level()
    log_format = get_log_format()

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set root logger level
    root_logger.setLevel(log_level)

    # Choose formatter
    if log_format == 'json':
        formatter = create_json_formatter()
    else:
        formatter = create_human_formatter()

    # Console handler for immediate output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handlers with rotation
    file_handlers = [
        ('app.log', logging.INFO),
        ('error.log', logging.ERROR),
        ('debug.log', logging.DEBUG),
        ('processing.log', logging.INFO),
        ('access.log', logging.INFO)
    ]

    for filename, level in file_handlers:
        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # Add filter for specific loggers
        if filename == 'processing.log':
            file_handler.addFilter(lambda record: record.name in ['main', 'processing'])
        elif filename == 'access.log':
            file_handler.addFilter(lambda record: record.name == 'access')
        elif filename == 'error.log':
            file_handler.addFilter(lambda record: record.levelno >= logging.ERROR)

        root_logger.addHandler(file_handler)

    # Create specific loggers
    loggers = {
        'app': logging.getLogger('app'),
        'main': logging.getLogger('main'),
        'processing': logging.getLogger('processing'),
        'access': logging.getLogger('access'),
        'flask': logging.getLogger('werkzeug')  # Flask's internal logger
    }

    # Set levels for specific loggers
    for name, logger in loggers.items():
        logger.setLevel(log_level)

    # Suppress noisy loggers in production
    if os.getenv('FLASK_ENV') == 'production':
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)

    return loggers

def get_logger(name):
    """Get a configured logger instance"""
    return logging.getLogger(name)

# Performance logging decorator
def log_performance(logger=None):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()

            log = logger or logging.getLogger(func.__module__)
            log.info(f"Starting {func.__name__}", extra={
                'function': func.__name__,
                'action': 'start'
            })

            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time

                log.info(f"Completed {func.__name__}", extra={
                    'function': func.__name__,
                    'action': 'complete',
                    'duration_ms': round(duration * 1000, 2)
                })

                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                log.error(f"Failed {func.__name__}: {str(e)}", extra={
                    'function': func.__name__,
                    'action': 'error',
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e)
                })
                raise

        return wrapper
    return decorator

# Request logging for Flask
def log_request(logger=None):
    """Log Flask request details"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request

            log = logger or logging.getLogger('access')

            # Log incoming request
            log.info("Request received", extra={
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'action': 'request_start'
            })

            try:
                result = func(*args, **kwargs)

                # Log successful response
                log.info("Request completed", extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200,
                    'action': 'request_complete'
                })

                return result
            except Exception as e:
                # Log error response
                log.error("Request failed", extra={
                    'method': request.method,
                    'path': request.path,
                    'error': str(e),
                    'action': 'request_error'
                })
                raise

        return wrapper
    return decorator

# Initialize logging when module is imported
loggers = setup_logging()

# Export commonly used loggers
app_logger = loggers['app']
main_logger = loggers['main']
processing_logger = loggers['processing']
access_logger = loggers['access']