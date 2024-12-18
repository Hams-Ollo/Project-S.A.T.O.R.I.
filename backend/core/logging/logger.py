"""
Comprehensive logging configuration for S.A.T.O.R.I. AI
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class CustomFormatter(logging.Formatter):
    """
    Custom formatter with colors and emojis for different log levels
    """
    
    # ANSI escape sequences for colors
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
    }
    
    # Emojis for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    # Reset ANSI escape sequence
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        # Get the emoji and color for the log level
        emoji = self.EMOJIS.get(record.levelname, '')
        color = self.COLORS.get(record.levelname, '')
        
        # Add the module and function name to the record
        record.module_func = f"{record.module}.{record.funcName}"
        
        # Format timestamp
        record.timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Create the log format with color
        format_str = (
            f"{color}[{record.timestamp}] "
            f"{emoji} {record.levelname:<8} "
            f"[{record.module_func}] "
            f"{record.getMessage()}{self.RESET}"
        )
        
        # Add exception info if present
        if record.exc_info:
            format_str = f"{format_str}\n{self.formatException(record.exc_info)}"
        
        return format_str

class SatoriLogger:
    """
    Centralized logging configuration for S.A.T.O.R.I. AI
    """
    
    def __init__(
        self,
        name: str,
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_dir: Optional[str] = None
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create log directory if it doesn't exist
        if log_to_file:
            self.log_dir = Path(log_dir or "logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Add file handlers
            self._add_file_handlers()
        
        # Add console handler
        self._add_console_handler()
        
        # Prevent logging from propagating to the root logger
        self.logger.propagate = False
    
    def _add_console_handler(self):
        """Add a console handler with color formatting"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter())
        self.logger.addHandler(console_handler)
    
    def _add_file_handlers(self):
        """Add file handlers with rotation policies"""
        # General logs
        general_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / "satori.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        general_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(module)s.%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(general_handler)
        
        # Error logs
        error_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "error.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(module)s.%(funcName)s] %(message)s\n'
            'Exception: %(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(error_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger

def create_logger(
    name: str,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Create and configure a logger instance
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    return SatoriLogger(name, log_level, log_to_file, log_dir).get_logger() 