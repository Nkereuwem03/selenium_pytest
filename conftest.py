"""
This module contains pytest fixtures for setting up and tearing down the Selenium WebDriver.
"""

import pytest
import os
import allure
import json
import atexit
import shutil
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from utils.browser_manager import BrowserManager
from utils.logger import attach_log_to_allure, logger

# Global variable to track temporary directories for cleanup
_temp_dirs = []


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser to run tests on"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode",
    )
    parser.addoption(
        "--env", action="store", default="QA", help="Environment to run tests against"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_sessionstart(session):
    """Initialize test session and create environment file."""
    os.makedirs("allure-results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Get browser configuration
    browser_name = session.config.getoption("--browser")
    headless = session.config.getoption("--headless")
    environment = session.config.getoption("--env")

    # Create temporary browser instance to get capabilities
    temp_browser_manager = None
    driver = None
    browser_version = "unknown"

    try:
        temp_browser_manager = BrowserManager(browser_name=browser_name)
        driver = temp_browser_manager.start_browser()
        browser_version = driver.capabilities.get("browserVersion", "unknown")
        logger.info(
            "Driver capabilities:\n" + json.dumps(driver.capabilities, indent=2)
        )
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        logger.error(f"Failed to get browser capabilities: {e}")
    finally:
        if temp_browser_manager:
            temp_browser_manager.quit_browser()

    # Create environment file for Allure
    env_file = os.path.join("allure-results", "environment.properties")
    with open(env_file, "w") as f:
        f.write(f"Browser={browser_name}\n")
        f.write(f"Browser.Version={browser_version}\n")
        f.write(f"Headless={headless}\n")
        f.write(f"OS={os.name}\n")
        f.write(f"Environment={environment}\n")
        f.write(
            f"Python.Version={session.config.hook.pytest_report_header(config=session.config, start_path=session.startpath)[0] if hasattr(session.config.hook, 'pytest_report_header') else 'unknown'}\n"
        )
        f.write(f"Test.Start.Time={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    logger.info(f"Environment file created at {env_file}")
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTED")
    logger.info(f"Browser: {browser_name} (headless: {headless})")
    logger.info(f"Environment: {environment}")
    logger.info("=" * 80)


def pytest_sessionfinish(session, exitstatus):
    """Clean up after test session."""
    logger.info("=" * 80)
    logger.info("TEST SESSION FINISHED")
    logger.info(f"Exit status: {exitstatus}")
    logger.info("=" * 80)

    # Clean up temporary directories
    cleanup_temp_directories()


def cleanup_temp_directories():
    """Clean up temporary directories created during test execution."""
    global _temp_dirs
    for temp_dir in _temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    _temp_dirs.clear()


# Register cleanup function to run on exit
atexit.register(cleanup_temp_directories)


@pytest.fixture(scope="function")
def setup_teardown(request):
    """
    Sets up and tears down the Selenium WebDriver for each test function.

    Args:
        request: pytest request object

    Yields:
        WebDriver: The Selenium WebDriver instance.
    """
    test_name = request.node.name
    browser_name = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    logger.info(f"Setting up test: {test_name}")
    logger.info(f"Browser: {browser_name} (headless: {headless})")

    browser_manager = None
    driver = None

    try:
        browser_manager = BrowserManager(browser_name=browser_name)
        driver = browser_manager.start_browser()
        logger.info(f"Browser {browser_name} started successfully")

        # Add test info to Allure
        allure.dynamic.feature(f"Browser: {browser_name}")
        allure.dynamic.parameter("browser", browser_name)
        allure.dynamic.parameter("headless", headless)

        yield driver

    except Exception as e:
        logger.error(f"Failed to start browser: {e}")
        raise
    finally:
        if browser_manager:
            logger.info(f"Quitting browser: {browser_name}")
            browser_manager.quit_browser()
            logger.info("Browser session ended")

        logger.info(f"Test completed: {test_name}")
        logger.info("-" * 80)


@pytest.fixture(scope="function")
def driver(setup_teardown):
    """
    Alias fixture for setup_teardown for backward compatibility.
    """
    return setup_teardown


def _extract_driver_from_item(item):
    """
    Safely extract WebDriver instance from test item if present.

    Args:
        item: pytest test item

    Returns:
        WebDriver or None: The WebDriver instance if found
    """
    try:
        for name, value in item.funcargs.items():
            if isinstance(value, WebDriver):
                return value
    except (AttributeError, KeyError):
        pass
    return None


def _attach_screenshot(driver: WebDriver, phase: str, test_name: str = ""):
    """
    Take and attach screenshot to Allure if driver is available.

    Args:
        driver: WebDriver instance
        phase: Test phase (setup, call, teardown)
        test_name: Name of the test
    """
    try:
        screenshot = driver.get_screenshot_as_png()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = f"{phase}_screenshot_{timestamp}"
        if test_name:
            name = f"{test_name}_{name}"

        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
        logger.info(f"Screenshot attached: {name}")
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {type(e).__name__}: {e}")


def _attach_page_source(driver: WebDriver, phase: str, test_name: str = ""):
    """
    Take and attach page source (HTML) to Allure if driver is available.

    Args:
        driver: WebDriver instance
        phase: Test phase (setup, call, teardown)
        test_name: Name of the test
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = f"{phase}_page_source_{timestamp}"
        if test_name:
            name = f"{test_name}_{name}"

        allure.attach(
            driver.page_source,
            name=name,
            attachment_type=allure.attachment_type.HTML,
        )
        logger.info(f"Page source attached: {name}")
    except Exception as e:
        logger.error(f"Failed to capture page source: {type(e).__name__}: {e}")


def _attach_browser_logs(driver: WebDriver, phase: str, test_name: str = ""):
    """
    Attach browser logs to Allure if available.

    Args:
        driver: WebDriver instance
        phase: Test phase (setup, call, teardown)
        test_name: Name of the test
    """
    try:
        if hasattr(driver, "get_log"):
            logs = driver.get_log("browser")
            if logs:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                name = f"{phase}_browser_logs_{timestamp}"
                if test_name:
                    name = f"{test_name}_{name}"

                log_text = "\n".join(
                    [f"[{log['level']}] {log['message']}" for log in logs]
                )
                allure.attach(
                    log_text,
                    name=name,
                    attachment_type=allure.attachment_type.TEXT,
                )
                logger.info(f"Browser logs attached: {name}")
    except Exception as e:
        logger.debug(f"Could not capture browser logs: {type(e).__name__}: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Automatically capture screenshots and attach logs on test failure.

    Args:
        item: pytest test item
        call: pytest call info
    """
    outcome = yield
    result = outcome.get_result()

    # Get driver if it exists in the test
    driver = _extract_driver_from_item(item)
    test_name = item.name

    # Capture artifacts on failure
    if result.failed and result.when in ("setup", "call", "teardown"):
        logger.error(f"Test {test_name} failed in {result.when} phase")

        if driver:
            _attach_screenshot(driver, result.when, test_name)
            _attach_page_source(driver, result.when, test_name)
            _attach_browser_logs(driver, result.when, test_name)

        # Always attach test logs
        attach_log_to_allure()

    # Also capture on success for debugging if needed
    elif result.passed and result.when == "call":
        logger.info(f"Test {test_name} passed")
        attach_log_to_allure()


@pytest.fixture(scope="session")
def browser_config(request):
    """
    Session-scoped fixture that provides browser configuration.

    Returns:
        dict: Browser configuration dictionary
    """
    return {
        "browser": request.config.getoption("--browser"),
        "headless": request.config.getoption("--headless"),
        "environment": request.config.getoption("--env"),
    }
