import logging
import os
from datetime import datetime

class ExactLevelFilter(logging.Filter):
    """
    A logging filter that allows only log records matching a specific log level.

    This filter is useful when you want a handler to capture only one
    particular level (e.g., DEBUG), rather than all logs above a threshold.

    Attributes
    ----------
    level : int
        The numeric logging level (e.g., logging.DEBUG) that should be allowed.
    """

    def __init__(self, level):
        """
        Initialize the filter with the exact logging level to match.

        Parameters
        ----------
        level : int
            The logging level that this filter should permit.
        """
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Determine whether the specified record should be logged.

        Parameters
        ----------
        record : logging.LogRecord
            The log record being evaluated.

        Returns
        -------
        bool
            True if the record's log level matches the configured level,
            otherwise False.
        """
        return record.levelno == self.level


# Keep a single timestamp directory per process
_LOG_DIR = None

def _get_run_log_dir(base="logs"):
    """
    Return the log directory for the current run, creating it on first use.

    A timestamped directory is created only once per process invocation.
    Subsequent calls return the same path, ensuring all log files for the run
    go into the same folder.

    Parameters
    ----------
    base : str, optional
        The base directory in which the timestamped folder will be created.
        Defaults to "logs".

    Returns
    -------
    str
        The full path to the run-specific log directory.
    """
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
    Set up and return a configured logger with multiple handlers.

    This logger includes:
      - `framework.log`: captures all logs (DEBUG and above).
      - `debug.log`: captures DEBUG logs *only*, using an exact-level filter.
      - (optional) console handler: captures INFO-level and above.

    The function is idempotent: repeated calls for the same logger name
    will not attach duplicate handlers.

    Parameters
    ----------
    logger_name : str
        The name of the logger to create or retrieve.
    console_level : int, optional
        The minimum log level for console output. Defaults to logging.INFO.
    attach_console : bool, optional
        Whether to attach a console handler. Defaults to True.

    Returns
    -------
    logging.Logger
        The configured logger instance.
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
    framework_handler.setLevel(logging.DEBUG)
    framework_handler.setFormatter(formatter)
    logger.addHandler(framework_handler)

    # Handler 2: debug.log (DEBUG ONLY)
    debug_handler = logging.FileHandler(debug_log_path, mode="a", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(ExactLevelFilter(logging.DEBUG))
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Optional: console handler (INFO+)
    if attach_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger