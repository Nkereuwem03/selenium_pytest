from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.logger import logger
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def test_tabs_and_windows_1(setup_teardown):
    """Opens new tab but does not switch to it"""

    driver = setup_teardown

    try:
        driver.get("https://parabank.parasoft.com/parabank/index.htm")
        reg_link = Keys.CONTROL + Keys.RETURN
        register = driver.find_element(By.LINK_TEXT, "Register")
        register.send_keys(reg_link)

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_tabs_and_windows_2(setup_teardown):
    """Opens new tab and automatically switches to it"""

    driver = setup_teardown

    try:
        driver.get("https://www.opencart.com/")
        # driver.switch_to.new_window('tab')
        driver.switch_to.new_window("window")
        driver.get("https://www.orangehrm.com/")
        # reg_link = Keys.CONTROL+Keys.RETURN
        # register = driver.find_element(By.LINK_TEXT, "Register")
        # register.send_keys(reg_link)
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
