"""Module for logging"""
import logging
import sys

def setup_custom_logger(name: str):
    """Creates custom logger to be attached at module level"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # every logger needs a handler, either inherited from parent or their own
    if not logger.handlers:  # avoid duplicate handlers if called multiple times
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger
