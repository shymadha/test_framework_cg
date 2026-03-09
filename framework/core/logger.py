import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "TestFramework",
                 log_level=logging.INFO,
                 log_dir: str = "logs") -> logging.Logger:

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if logger.handlers:
        return logger  # Prevent duplicate handlers

    log_file = os.path.join(log_dir, "framework.log")

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )

    # Console handler
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger