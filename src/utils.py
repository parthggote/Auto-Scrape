import logging
import sys

def setup_logging():
    """
    Configures the root logger for the application.

    This setup provides a consistent logging format and level across all modules.
    Logs are directed to standard output.
    """
    # Get the root logger
    logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the logging level
    logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create a handler to write to standard output (console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Add the handler to the root logger
    logger.addHandler(stream_handler)

    logging.info("Logging configured successfully.")
