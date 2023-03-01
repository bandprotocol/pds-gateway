import logging

from uvicorn.logging import DefaultFormatter

FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"


def init_loggers(logger_name: str = "pds_gateway_log", log_level: str = "DEBUG"):
    """Initializes the logger

    Args:
        logger_name: Logger name
        log_level: The log level as a string
    """
    # Creates logger
    logger = logging.getLogger(logger_name)

    logger.setLevel(log_level)

    # Create a console handler and sets the handler log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Creates a formatter and adds to the console handler
    formatter = DefaultFormatter(FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)

    # Adds the console handler to the logger
    logger.addHandler(ch)
