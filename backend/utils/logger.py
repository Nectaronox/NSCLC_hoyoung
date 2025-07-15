import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
   이 부분은 logger을 설정하는 부분으로 이런 부분도 AI에게 맞기고 가면 쉽게 할 수 있음.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging_level = getattr(logging, log_level, logging.INFO)
    
    # Use basicConfig for root logger configuration
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]  # Ensure logs go to console
    )

    # Get the root logger
    logger = logging.getLogger('nsclc_staging')
    
    # Clear existing handlers to avoid duplicates if re-run
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    log_file = os.path.join(log_dir, 'nsclc_staging.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = os.path.join(log_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Set third-party loggers to WARNING level
    logging.getLogger('uvicorn').setLevel(logging.INFO) # Uvicorn logs are useful
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    logger.info("Logging configured successfully")
    return logger

def get_logger(name: str = None):
    """
    Get a logger instance.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        logger: Logger instance
    """
    if name:
        return logging.getLogger(f'nsclc_staging.{name}')
    return logging.getLogger('nsclc_staging')

class LoggerMixin:
    """
    Mixin class to add logging functionality to any class.
    """
    
    @property
    def logger(self):
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)

# Context manager for logging performance
class LogExecutionTime:
    """
    Context manager to log execution time of code blocks.
    
    Usage:
        with LogExecutionTime("Processing image"):
            # Your code here
            pass
    """
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(f"{self.operation_name} failed after {duration:.2f}s: {exc_val}")
        else:
            self.logger.info(f"{self.operation_name} completed in {duration:.2f}s")
        
        return False  # Don't suppress exceptions 