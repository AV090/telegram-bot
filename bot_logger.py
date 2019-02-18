import logging
import logging.handlers


def create_logger(name: str) -> logging:
    logger = logging.getLogger(name if name and len(name) > 5 else __name__ + " - from - " + name)
    fmt = logging.Formatter('%(asctime)s - %(name)18s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(

        "logs.log", maxBytes=2048 ** 2, backupCount=5)

    handler.setFormatter(fmt=fmt)
    logger.addHandler(handler)
    return logger
