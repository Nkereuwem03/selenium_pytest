from selenium.webdriver.common.by import By
from utils.logger import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pytest
from utils.wait_helper import wait_for_elements_presence


def test_select_single_checkbox(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")

        check_elements = wait_for_elements_presence(
            driver, (By.XPATH, "//input[@type='checkbox' and contains(@value, 'cb')]")
        )
        for element in check_elements:
            if element.is_selected():
                element.click()
            if element.get_attribute("value") == "cb1":
                element.click()
                assert element.is_selected()

        logger.info("Test passed: test select single checkbox")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_select_multiple_checkboxes(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")

        check_elements = wait_for_elements_presence(
            driver, (By.XPATH, "//input[@type='checkbox' and contains(@value, 'cb')]")
        )

        boxes_to_be_checked = ["cb1", "cb2"]
        for element in check_elements:
            if element.is_selected():
                element.click()
            if element.get_attribute("value") in boxes_to_be_checked:
                element.click()
                assert element.is_selected()

        # for i in range(len(check_elements)):
        #     if i < 1:
        #         check_elements[i].click()

        # for i in range(len(check_elements)-2, len(check_elements)):
        #     check_elements[i].click()

        logger.info("Test passed: test select multiple checkboxes")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"test_select_multiple_checkboxes: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
