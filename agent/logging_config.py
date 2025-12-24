"""
Structured Logging Configuration
Provides consistent logging across the application
"""
import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_obj["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj["request_id"] = record.request_id
        if hasattr(record, 'duration'):
            log_obj["duration_ms"] = record.duration
        
        return json.dumps(log_obj)


def setup_logging(app_name="travel-agent", log_level=None, log_file=None):
    """
    Setup application logging
    
    Args:
        app_name: Application name for logger
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
    
    Returns:
        Configured logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    level = getattr(logging, log_level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(level)
    logger.handlers = []  # Clear existing handlers
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Use JSON format in production, human-readable in development
    if os.environ.get('FLASK_ENV') == 'production':
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified and not in serverless environment)
    # Vercel and similar platforms have read-only filesystems
    is_serverless = os.getenv('VERCEL') == '1' or os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    if log_file and not is_serverless:
        try:
            os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs', exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If we can't create log file (e.g., read-only filesystem), just use console
            logger.warning(f"Failed to create log file {log_file}: {e}. Using console logging only.")
    elif is_serverless:
        logger.info("Running in serverless environment - file logging disabled")
    
    return logger


def log_request(logger, request, response=None, duration=None):
    """Log HTTP request details"""
    log_data = {
        "method": request.method,
        "path": request.path,
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Unknown')
    }
    
    if response:
        log_data["status_code"] = response.status_code
    
    if duration:
        log_data["duration_ms"] = round(duration * 1000, 2)
    
    logger.info(f"HTTP {request.method} {request.path}", extra=log_data)


def log_error(logger, error, context=None):
    """Log error with context"""
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if context:
        log_data.update(context)
    
    logger.error(f"Error: {str(error)}", exc_info=True, extra=log_data)


# Performance monitoring decorator
def log_performance(logger, threshold_ms=1000):
    """
    Decorator to log function performance
    
    Args:
        logger: Logger instance
        threshold_ms: Log warning if execution exceeds this (milliseconds)
    
    Usage:
        @log_performance(logger, threshold_ms=500)
        def slow_function():
            time.sleep(1)
    """
    from functools import wraps
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                
                if duration > threshold_ms:
                    logger.warning(
                        f"Slow function: {func.__name__} took {duration:.2f}ms",
                        extra={"function": func.__name__, "duration_ms": duration}
                    )
                else:
                    logger.debug(
                        f"Function {func.__name__} completed in {duration:.2f}ms",
                        extra={"function": func.__name__, "duration_ms": duration}
                    )
                
                return result
            
            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.error(
                    f"Function {func.__name__} failed after {duration:.2f}ms",
                    exc_info=True,
                    extra={"function": func.__name__, "duration_ms": duration}
                )
                raise
        
        return wrapper
    return decorator


# Usage example
if __name__ == "__main__":
    # Setup logger
    logger = setup_logging("test", log_level="DEBUG", log_file="logs/app.log")
    
    # Test logging
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test performance logging
    @log_performance(logger, threshold_ms=100)
    def test_function():
        import time
        time.sleep(0.2)
        return "done"
    
    test_function()
