from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from utils.wait_helper import wait_for_element_presence
from utils.custom_assertions import assert_element_text
from utils.logger import logger
import pytest


def test_select_single_option(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")

        select_element = wait_for_element_presence(
            driver, (By.CSS_SELECTOR, "select[name='dropdown']")
        )
        select = Select(select_element)

        select.select_by_index(0)
        dropdown_1 = driver.find_element(By.CSS_SELECTOR, "option[value='dd1']")
        assert dropdown_1.is_selected()

        select.select_by_visible_text("Drop Down Item 2")
        dropdown_2 = driver.find_element(By.CSS_SELECTOR, "option[value='dd2']")
        assert dropdown_2.is_selected()

        select.select_by_value("dd4")
        dropdown_4 = driver.find_element(By.CSS_SELECTOR, "option[value='dd4']")
        assert dropdown_4.is_selected()

        selected_option = select.first_selected_option
        assert selected_option.get_attribute("value") == "dd4"
        assert_element_text(selected_option, "Drop Down Item 4")

        driver.find_element(By.CSS_SELECTOR, "input[value='submit']").click()
        logger.info("Test passed: test select single option")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_select_multiple_options(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")

        select_element = wait_for_element_presence(
            driver, (By.CSS_SELECTOR, "select[name='multipleselect[]']")
        )
        select = Select(select_element)
        select.deselect_all()

        # select.select_by_index(0)
        # select.select_by_value("ms2")
        # select.select_by_visible_text("Selection Item 3")

        options_to_select = ["Selection Item 1", "Selection Item 2", "Selection Item 3"]
        for option in options_to_select:
            select.select_by_visible_text(option)

        option_1 = driver.find_element(By.CSS_SELECTOR, "option[value='ms1']")
        option_2 = driver.find_element(By.CSS_SELECTOR, "option[value='ms2']")
        option_3 = driver.find_element(By.CSS_SELECTOR, "option[value='ms3']")

        assert option_1.is_selected()
        assert option_2.is_selected()
        assert option_3.is_selected()

        select.deselect_by_index(0)
        assert not option_1.is_selected()

        all_options = select.options
        selected_options = select.all_selected_options
        first_selected_options = select.first_selected_option

        driver.find_element(By.CSS_SELECTOR, "input[value='submit']").click()
        logger.info("Test passed: test select multiple options")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_select_multiple_options_using_action_chains(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")

        select_element = wait_for_element_presence(
            driver, (By.CSS_SELECTOR, "select[name='multipleselect[]']")
        )
        select = Select(select_element)
        select.deselect_all()

        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL)

        # options_to_select = ["Selection Item 1", "Selection Item 2", "Selection Item 3"]
        options_to_select = ["ms1", "ms2", "ms3"]
        for option_text in options_to_select:
            option = driver.find_element(By.XPATH, f"//option[@value='{option_text}']")
            actions.click(option)

        actions.key_up(Keys.CONTROL)
        actions.perform()

        option_1 = driver.find_element(By.CSS_SELECTOR, "option[value='ms1']")
        option_2 = driver.find_element(By.CSS_SELECTOR, "option[value='ms2']")
        option_3 = driver.find_element(By.CSS_SELECTOR, "option[value='ms3']")

        assert option_1.is_selected()
        assert option_2.is_selected()
        assert option_3.is_selected()

        driver.find_element(By.CSS_SELECTOR, "input[value='submit']").click()
        logger.info("Test passed: test select multiple using action chains")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
