from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from utils.wait_helper import wait_for_element_visibility, wait_for_element_clickable
from utils.logger import logger
import pytest


def test_bootstrap_dropdown(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://www.dummyticket.com/dummy-ticket-for-visa-application/")
        wait_for_element_clickable(
            driver, (By.XPATH, "//span[@id='select2-billing_country-container']")
        ).click()
        search_box = wait_for_element_visibility(
            driver, (By.XPATH, "//input[@class='select2-search__field']")
        )
        search_box.clear()
        search_box.send_keys("Ghana")
        ghana_option = wait_for_element_clickable(
            driver, (By.XPATH, "//li[@role='option'][contains(text(), 'Ghana')]")
        )
        ghana_option.click()
        wait_for_element_visibility(
            driver, (By.XPATH, "//span[@id='select2-billing_country-container']")
        )
        logger.info("Test passed: Bootstrap dropdown selection successful.")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
