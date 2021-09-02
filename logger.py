import logging


def init_logger() -> logging.Logger:
    logger = logging.getLogger('chat')
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    return logger

logger = init_logger()
