import time
from utils.logger import logger
import pytest
from utils.wait_helper import wait_for_element_presence
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def test_mouse_hover(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://magento.softwaretestingboard.com/#google_vignette")

        menu = driver.find_element(By.XPATH, "//span[normalize-space()='Women']")
        submenu_1 = driver.find_element(
            By.XPATH, "//a[@id='ui-id-9']//span[contains(text(),'Tops')]"
        )
        submenu_2 = driver.find_element(
            By.XPATH, "//a[@id='ui-id-11']//span[contains(text(),'Jackets')]"
        )

        actions = ActionChains(driver)
        actions.move_to_element(menu).perform()
        actions.move_to_element(submenu_1).perform()
        submenu_2.click()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_right_click(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://swisnl.github.io/jQuery-contextMenu/demo.html")

        wait = WebDriverWait(driver, 10)

        actions = ActionChains(driver)
        menu = driver.find_element(
            By.XPATH, "//span[@class='context-menu-one btn btn-neutral']"
        )
        actions.context_click(menu).perform()

        paste_option = wait_for_element_presence(
            driver,
            (
                By.XPATH,
                "//li[@class='context-menu-item context-menu-icon context-menu-icon-paste']",
            ),
        )
        paste_option.click()

        alert = wait.until(EC.alert_is_present())
        assert alert.text == "clicked: paste"
        alert.accept()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_double_click(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testautomationpractice.blogspot.com/#")

        wait = WebDriverWait(driver, 10)

        actions = ActionChains(driver)
        copy_btn = driver.find_element(
            By.XPATH, "//button[normalize-space()='Copy Text']"
        )
        actions.double_click(copy_btn).perform()

        input_field = wait_for_element_presence(
            driver, (By.CSS_SELECTOR, "#field2")
        ).get_attribute("value")
        assert input_field == "Hello World!"

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_drag_and_drop(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testautomationpractice.blogspot.com/#")

        wait = WebDriverWait(driver, 10)

        actions = ActionChains(driver)
        draggable = driver.find_element(By.XPATH, "//div[@id='draggable']")
        droppable = driver.find_element(By.CSS_SELECTOR, "#droppable")
        actions.drag_and_drop(draggable, droppable).perform()

        assert (
            wait_for_element_presence(
                driver, (By.CSS_SELECTOR, "div[id='droppable'] p")
            ).text
            == "Dropped!"
        )

        time.sleep(5)
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.skip(reason="stale element reference: stale element not found")
def test_slider(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://jqueryui.com/slider/#range")
        wait = WebDriverWait(driver, 10)
        action = ActionChains(driver)

        frame = wait_for_element_presence(driver, (By.CSS_SELECTOR, ".demo-frame"))

        driver.switch_to.frame(frame)

        left = wait_for_element_presence(
            driver,
            (
                By.XPATH,
                "//span[@class='ui-slider-handle ui-corner-all ui-state-default'][1]",
            ),
        )

        right = wait_for_element_presence(
            driver,
            (
                By.XPATH,
                "//span[@class='ui-slider-handle ui-corner-all ui-state-default'][2]",
            ),
        )

        logger.info(f"left: {left.location}")
        logger.info(f"right: {right.location}")

        action.drag_and_drop_by_offset(left, 100, 0).perform()
        action.drag_and_drop_by_offset(right, -20, 0).perform()

        logger.info(f"left after: {left.location}")
        logger.info(f"right after: {right.location}")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_scrolling_1(setup_teardown):
    """Scroll to a particular pixel on the screen"""
    driver = setup_teardown

    try:
        driver.get("https://www.countries-ofthe-world.com/flags-of-the-world.html")
        wait = WebDriverWait(driver, 10)

        driver.execute_script("window.scrollBy(0, 3000)", "")
        y_offset = driver.execute_script("return window.pageYOffset")
        print(f"No of pixels moved: {y_offset}")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.skip(reason="Timeout: Element not present within 10s: ('xpath', '//td[normalize-space()='Nigeria']')")
def test_scrolling_2(setup_teardown):
    """Scroll into view on a particular element"""
    driver = setup_teardown

    try:
        driver.get("https://www.countries-ofthe-world.com/flags-of-the-world.html")

        nigeria_flag = wait_for_element_presence(
            driver, (By.XPATH, "//td[normalize-space()='Nigeria']")
        )
        # driver.find_element(
        #     By.XPATH, "//td[normalize-space()='Nigeria']"
        # )
        # nigeria_flag = driver.find_element(By.XPATH, "//img[@alt='Flag of Nigeria']")

        driver.execute_script("arguments[0].scrollIntoView();", nigeria_flag)
        time.sleep(3)
        y_offset = driver.execute_script("return window.pageYOffset")
        print(f"No of pixels moved: {y_offset}")
        time.sleep(3)
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_scrolling_3(setup_teardown):
    """Scroll to the vertical end of window and back to top"""

    driver = setup_teardown

    try:
        driver.get("https://www.countries-ofthe-world.com/flags-of-the-world.html")
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)", "")
        time.sleep(3)
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight)", "")
        y_offset = driver.execute_script("return window.pageYOffset")
        print(f"No of pixels moved: {y_offset}")
        time.sleep(3)
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
