"""Custom assertion methods for Selenium WebDriver tests."""

from utils.logger import logger
import os
import time


def assert_title(driver, expected_title):
    """
    Asserts that the current page title matches the expected title.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): The WebDriver instance.
        expected_title (str): The expected title of the page.

    Raises:
        AssertionError: If the actual title does not match the expected title.
    """
    actual_title = driver.title
    if actual_title != expected_title:
        logger.error(
            f"Title mismatch. Expected: '{expected_title}', Actual: '{actual_title}'"
        )
    assert actual_title == expected_title


def assert_url(driver, expected_url):
    """
    Asserts that the current page URL matches the expected URL.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): The WebDriver instance.
        expected_url (str): The expected URL of the page.

    Raises:
        AssertionError: If the actual URL does not match the expected URL.
    """
    actual_url = driver.current_url
    assert (
        actual_url == expected_url
    ), f"URL mismatch. Expected: '{expected_url}', Actual: '{actual_url}'"


def assert_element_is_displayed(element, element_name="Element"):
    """
    Asserts that a given web element is displayed on the page.

    Args:
        element (selenium.webdriver.remote.webelement.WebElement): The web element to check.
        element_name (str): A descriptive name for the element (for error messages).

    Raises:
        AssertionError: If the element is not displayed.
    """
    assert element.is_displayed(), f"{element_name} is not displayed."


def assert_element_text(element, expected_text, element_name="Element"):
    """
    Asserts that a given web element's text matches the expected text.

    Args:
        element (selenium.webdriver.remote.webelement.WebElement): The web element to check.
        expected_text (str): The expected text of the element.
        element_name (str): A descriptive name for the element (for error messages).

    Raises:
        AssertionError: If the actual text does not match the expected text.
    """
    actual_text = element.text.strip()
    assert (
        actual_text == expected_text
    ), f"{element_name} text mismatch. Expected: '{expected_text}', Actual: '{actual_text}'"


def assert_text_contains(element, expected_substring, element_name="Element"):
    """
    Asserts that a given web element's text contains the expected substring.

    Args:
        element (WebElement): The web element to check.
        expected_substring (str): Substring expected to be present.
        element_name (str): A name for better error output.

    Raises:
        AssertionError: If the substring is not found.
    """
    actual_text = element.text.strip()
    assert (
        expected_substring in actual_text
    ), f"{element_name} text does not contain '{expected_substring}'. Actual: '{actual_text}'"


def assert_element_exists(element, element_name="Element"):
    """
    Asserts that a given web element is not None.

    Useful after find_element when you want to ensure the element was found.

    Args:
        element (WebElement or None): The element to check.
        element_name (str): Label for the element.

    Raises:
        AssertionError: If element is None.
    """
    assert element is not None, f"{element_name} does not exist on the page."


# def wait_for_file_download(path, filename, timeout=10):
#     file_path = os.path.join(path, filename)
#     for _ in range(timeout):
#         if os.path.exists(file_path):
#             return True
#         time.sleep(1)
#     return False
