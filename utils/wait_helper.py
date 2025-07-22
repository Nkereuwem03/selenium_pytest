"""
Helper functions for explicit waits in Selenium WebDriver.
"""

import yaml
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from utils.logger import logger


with open("config/config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


timeout = config.get("explicit_wait", 10)


def wait_for_element_presence(driver: WebDriver, locator: tuple) -> WebElement:
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        logger.debug(f"Element located by {locator} is present.")
        return element
    except TimeoutException:
        logger.error(f"Timeout: Element not present within {timeout}s: {locator}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while waiting for element presence: {e}")
        raise


def wait_for_elements_presence(driver: WebDriver, locator: tuple) -> list[WebElement]:
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
        logger.debug(f"Element located by {locator} is present.")
        return elements
    except TimeoutException:
        logger.error(f"Timeout: Element not present within {timeout}s: {locator}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while waiting for element presence: {e}")
        raise


def wait_for_element_visibility(driver: WebDriver, locator: tuple) -> WebElement:
    """
    Waits for an element to be visible on the page.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        logger.debug(f"Element located by {locator} is visible.")
        return element
    except TimeoutException:
        logger.error(f"Timeout: Element not visible within {timeout}s: {locator}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while waiting for element visibility: {e}")
        raise


def wait_for_alert_visibility(driver: WebDriver) -> str:
    """
    Waits for a JavaScript alert to be present and returns its text.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        logger.debug("Alert is present.")
        alert = driver.switch_to.alert
        return alert
    except TimeoutException:
        logger.error(f"Timeout: Alert not visible within {timeout}s.")
        raise
    except Exception as e:
        logger.error(f"An error occurred while waiting for alert visibility: {e}")
        raise


def wait_for_element_clickable(driver: WebDriver, locator: tuple) -> WebElement:
    """Waits for an element to be clickable on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        logger.debug(f"Element located by {locator} is clickable.")
        return element
    except TimeoutException:
        logger.error(f"Timeout: Element not clickable within {timeout}s: {locator}")
        raise
