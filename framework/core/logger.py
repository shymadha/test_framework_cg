# import logging
# import os
# from logging.handlers import RotatingFileHandler

# def setup_logger(name: str = "TestFramework",
#                  log_level=logging.INFO,
#                  log_dir: str = "logs") -> logging.Logger:

#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)

#     logger = logging.getLogger(name)
#     logger.setLevel(log_level)

#     if logger.handlers:
#         return logger  # Prevent duplicate handlers

#     log_file = os.path.join(log_dir, "framework.log")

#     # File handler with rotation
#     file_handler = RotatingFileHandler(
#         log_file,
#         maxBytes=5 * 1024 * 1024,  # 5MB
#         backupCount=3
#     )

#     # Console handler
#     console_handler = logging.StreamHandler()

#     formatter = logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     )

#     file_handler.setFormatter(formatter)
#     console_handler.setFormatter(formatter)

#     logger.addHandler(file_handler)
#     logger.addHandler(console_handler)

#     return logger

import logging
import os
from datetime import datetime

class ExactLevelFilter(logging.Filter):
    """Pass only log records that match an exact level (e.g., DEBUG only)."""
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


# Keep a single timestamp directory per process
_LOG_DIR = None

def _get_run_log_dir(base="logs"):
    global _LOG_DIR
    if _LOG_DIR is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        _LOG_DIR = os.path.join(base, ts)
        os.makedirs(_LOG_DIR, exist_ok=True)
    return _LOG_DIR


def setup_logger(logger_name: str,
                 console_level=logging.INFO,
                 attach_console=True) -> logging.Logger:
    """
    Creates/returns a logger with:
      - framework.log (all levels)
      - debug.log (DEBUG only)
      - optional console (INFO+)
    Ensures no duplicate handlers on repeated calls for the same logger_name.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers will filter
    logger.propagate = False        # prevent passing up to root, avoiding duplicates

    # If handlers already attached, return as-is (idempotent)
    if logger.handlers:
        return logger

    log_dir = _get_run_log_dir()
    framework_log_path = os.path.join(log_dir, "framework.log")
    debug_log_path = os.path.join(log_dir, "debug.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler 1: framework.log (ALL LEVELS)
    framework_handler = logging.FileHandler(framework_log_path, mode="a", encoding="utf-8")
    framework_handler.setLevel(logging.DEBUG)  # accept all >= DEBUG
    framework_handler.setFormatter(formatter)
    logger.addHandler(framework_handler)

    # Handler 2: debug.log (DEBUG ONLY)
    debug_handler = logging.FileHandler(debug_log_path, mode="a", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)      # necessary, but not sufficient
    debug_handler.addFilter(ExactLevelFilter(logging.DEBUG))  # ensures ONLY DEBUG
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Optional: console handler (INFO+)
    if attach_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger