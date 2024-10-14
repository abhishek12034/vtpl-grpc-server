import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    logger = logging.getLogger("grpc_ips")

    # Avoid adding duplicate handlers
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # File handler with timed rotation
        log_path = os.path.join("logs", "grpc_server.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_path,
            when="D",
            interval=2,
            backupCount=5,  # Rotate every minute, keep 1 backup
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatters
        console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Attach formatters to handlers
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
