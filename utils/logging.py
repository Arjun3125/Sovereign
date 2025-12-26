"""
Logging Utilities
Centralized logging for the Sovereign system.
"""

import logging
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_file=None):
    """Set up logging for the system.
    
    Args:
        log_level: Logging level (default INFO)
        log_file: Optional log file path
    """
    logger = logging.getLogger("cold_strategist")
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"cold_strategist.{name}")
