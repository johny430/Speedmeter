import logging

from constants import LOG_DATE_FORMAT, LOG_FORMAT


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    # httpx пишет каждый запрос в INFO, дублируя наши строки по запросам.
    logging.getLogger("httpx").setLevel(logging.WARNING)
