import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = "logs/app.log", max_bytes: int = 5 * 1024 * 1024, backup_count: int = 3) -> logging.Logger:
    """
    Logging settings with console output and size-based rotating file output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
   # Preventing duplicate handlers upon multiple invocations
    if logger.handlers:
        return logger

    # Standard Log Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    #1. Console handler (for display in the terminal or Docker)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    #2. Rotating FileHandler
    #Create logs directory if it does not exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count, 
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
        
    return logger

# Local Test Sample
if __name__ == "__main__":
    log = setup_logger("test_logger", log_file="logs/currency_etl.log")
    log.info("The logging system with volume-limiting capability has been successfully set up.")