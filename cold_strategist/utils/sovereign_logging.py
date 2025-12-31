"""
Centralized logging helpers for cold_strategist subpackage.

This file mirrors `utils/sovereign_logging.py` and avoids the risky
module name `logging` which can shadow the stdlib logging module.
"""

import logging


def setup_logging(log_level=logging.INFO, log_file=None):
    logger = logging.getLogger("cold_strategist")
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"cold_strategist.{name}")
