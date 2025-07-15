"""Logger configuration for Selenium tests using Loguru."""

import os
import sys
from datetime import datetime
from loguru import logger
import allure

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

ENV = os.getenv("ENV", "development").lower()

log_filename = f"selenium_log_{datetime.now().strftime('%Y-%m-%d')}.log"
log_file_path = os.path.join(LOG_DIR, log_filename)

logger.remove()

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.add(
    sys.stdout,
    level="ERROR" if ENV == "development" else "ERROR",
    colorize=True,
    format=LOG_FORMAT,
)

logger.add(
    log_file_path,
    level="ERROR" if ENV == "development" else "ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="1 MB",
    retention="7 days",
    encoding="utf-8",
    enqueue=True,
    # backtrace=True,
    # diagnose=True,
)


def catch_exceptions(type_, value, traceback):
    """Catches unhandled exceptions and logs them."""
    logger.exception("Uncaught exception:", exc_info=(type_, value, traceback))


sys.excepthook = catch_exceptions


LOG_PATH = log_file_path


def attach_log_to_allure():
    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8") as log_file:
                allure.attach(
                    log_file.read(),
                    name="test_log",
                    attachment_type=allure.attachment_type.TEXT,
                )
    except ImportError:
        logger.warning("Allure not installed, skipping log attachment.")
