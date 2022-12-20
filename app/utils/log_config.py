import uvicorn
import logging

FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"

app_dict_config = {
    "formatters": {
        "basic": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": FORMAT,
        }
    }
}

# code variant:
def init_loggers(logger_name: str = "pds_gateway_log", log_level: str = "DEBUG"):
    # create logger
    logger = logging.getLogger(logger_name)

    logger.setLevel(log_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter
    formatter = uvicorn.logging.DefaultFormatter(FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
