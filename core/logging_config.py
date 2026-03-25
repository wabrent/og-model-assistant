"""
Logging configuration using Loguru.
"""
import sys
from loguru import logger

from core.config import settings


def setup_logging():
    """Configure logging with Loguru."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with formatting
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    return logger


# Create logs directory
import os
os.makedirs("logs", exist_ok=True)
