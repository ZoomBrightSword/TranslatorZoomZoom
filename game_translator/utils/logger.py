import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# Use the same AppData directory as the config
APP_NAME = "GameTranslator"
APP_DATA_DIR = Path(os.getenv("APPDATA", "")) / APP_NAME
LOG_FILE = APP_DATA_DIR / "app.log"

def setup_logger():
    """
    Configures and returns a logger that writes to a rotating file.
    """
    # Ensure the log directory exists
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger("GameTranslator")
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if this function is called more than once
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a rotating file handler
    # This will create up to 5 log files, each 1MB in size.
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,  # 1 MB
        backupCount=5,
        encoding='utf-8'
    )

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

# Create a single logger instance to be used across the application
log = setup_logger()

# Example usage:
# from utils.logger import log
# log.info("This is an info message.")
# log.warning("This is a warning.")
# log.error("This is an error.")