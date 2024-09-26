import logging

def setup_logging():
    logger = logging.getLogger('grpc_ips')
    
    # Avoid adding duplicate handlers
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # File handler (single file for all logs)
        file_handler = logging.FileHandler('grpc_server.log')  # Change here
        file_handler.setLevel(logging.DEBUG)

        # Formatters
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Attach formatters to handlers
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
