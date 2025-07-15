from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pytest
from utils.logger import logger


def test_cookies(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://demo.nopcommerce.com/")
        driver.add_cookie({"name": "my_cookie", "value": "12345"})

        cookies = driver.get_cookies()

        for c in cookies:
            logger.info(f"{c.get('name')} : {c.get('value')}")
        logger.info("")

        driver.delete_cookie("my_cookie")

        cookies = driver.get_cookies()

        for c in cookies:
            logger.info(f"{c.get('name')} : {c.get('value')}")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
