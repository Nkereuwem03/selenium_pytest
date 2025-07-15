"""
This module contains pytest fixtures for setting up and tearing down the Selenium WebDriver.
"""

import pytest
import os
import allure
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from utils.browser_manager import BrowserManager
from utils.logger import attach_log_to_allure, logger
import json


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser to run tests on"
    )


def pytest_sessionstart(session):
    os.makedirs("allure-results", exist_ok=True)
    temp_browser_manager = BrowserManager()
    driver = temp_browser_manager.start_browser()
    browser_name = temp_browser_manager.browser_name
    browser_version = driver.capabilities.get("browserVersion", "unknown")
    logger.info("Driver capabilities:\n" + json.dumps(driver.capabilities, indent=2))

    temp_browser_manager.quit_browser()

    env_file = os.path.join("allure-results", "environment.properties")
    with open(env_file, "w") as f:
        f.write(f"Browser={browser_name}\n")
        f.write(f"Browser.Version={browser_version}\n")
        f.write(f"OS={os.name}\n")
        f.write("Environment=QA\n")
        f.write("Tester=Nkereuwem\n")
        f.write(f"Tested.On={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    logger.info(f"Environment file created at {env_file} with browser details.")
    logger.info("Starting test session with browser details.")
    logger.info("-" * 50)


@pytest.fixture(scope="function")
def setup_teardown(request):
    """
    Sets up and tears down the Selenium WebDriver for each test function.

    Yields:
        WebDriver: The Selenium WebDriver instance.
    """
    browser_name = request.config.getoption("--browser")
    browser_manager = BrowserManager(browser_name)
    driver = browser_manager.start_browser()
    logger.info(f"Starting browser: {browser_name}")

    yield driver

    logger.info(f"Quitting browser: {browser_manager.browser_name}")
    browser_manager.quit_browser()
    logger.info("Browser session ended.")
    logger.info("Test completed, browser closed.")
    logger.info("\n" + "-" * 50 + "\n" + "-" * 50 + "\n" + "-" * 50)


def _extract_driver_from_item(item):
    """Safely get WebDriver instance from test item if present."""
    for name, value in item.funcargs.items():
        if isinstance(value, WebDriver):
            return value
    return None


def _attach_screenshot(driver: WebDriver, phase: str):
    """Take and attach screenshot to Allure if driver is available."""
    try:
        # Attach screenshot
        screenshot = driver.get_screenshot_as_png()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        allure.attach(
            screenshot,
            name=f"{phase}_failure_screenshot_{timestamp}",
            attachment_type=allure.attachment_type.PNG,
        )
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.error(
            f"Screenshot or page source capture failed: {type(e).__name__}: {e}"
        )


def _attach_page_source(driver: WebDriver, phase: str):
    """Take and attach page source (HTML) to Allure if driver is available."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        # Attach HTML page source
        allure.attach(
            driver.page_source,
            name=f"{phase}_page_source_{timestamp}",
            attachment_type=allure.attachment_type.HTML,
        )

    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.error(f"Page source capture failed: {type(e).__name__}: {e}")


# Automatically capture screenshots and attach logs
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    # Get driver if it exists in the test
    driver = _extract_driver_from_item(item)

    # Screenshot & log on setup or call failure
    if result.failed and result.when in ("setup", "call", "teardown"):
        if driver:
            _attach_screenshot(driver, result.when)
            _attach_page_source(driver, result.when)
    attach_log_to_allure()
