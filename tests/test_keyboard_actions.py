from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pytest
from utils.logger import logger


def test_keyboard_actions(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://www.comparetext.net/compare")
        action = ActionChains(driver)

        left_box = driver.find_element(By.XPATH, "//textarea[@id='left']")
        right_box = driver.find_element(By.XPATH, "//textarea[@id='right']")
        submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit'] span")

        left_box.send_keys(
            "Here are the main keyboard actions you can perform in Selenium"
        )

        action.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
        action.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL)
        action.perform()

        # action.send_keys(Keys.TAB)
        action.click(right_box)

        action.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        action.click(submit)
        logger.info("Test passed: test keyboard actions")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
