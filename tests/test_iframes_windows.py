from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from utils.wait_helper import wait_for_alert_visibility, wait_for_element_visibility
from utils.logger import logger


@pytest.mark.alert
def test_alerts(setup_teardown):
    driver = setup_teardown
    driver.get("https://the-internet.herokuapp.com/javascript_alerts")

    try:
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsAlert()']").click()
        alert = wait_for_alert_visibility(driver)
        alert.accept()
        logger.info("Test passed: test_alerts")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.alert
def test_js_confirm(setup_teardown):
    driver = setup_teardown
    driver.get("https://the-internet.herokuapp.com/javascript_alerts")
    try:
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsConfirm()']").click()
        alert = wait_for_alert_visibility(driver)
        alert.dismiss()
        logger.info("Test passed: test_js_confirm")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.alert
def test_js_prompt(setup_teardown):
    driver = setup_teardown
    try:
        logger.info("Starting test_js_prompt")
        logger.debug(f"Driver Capabilities: {driver.capabilities}")
        logger.info(f"Browser: {driver.capabilities.get('browserName', 'Unknown')}")
        logger.info(f"Platform: {driver.capabilities.get('platform', 'N/A')}")
        logger.info(f"Version: {driver.capabilities.get('version', 'N/A')}")

        driver.get("https://the-internet.herokuapp.com/javascript_alerts")
        driver.find_element(By.CSS_SELECTOR, "button[onclick='jsPrompt()']").click()
        alert = wait_for_alert_visibility(driver)
        alert.send_keys("Selenium Test")
        alert.accept()

        logger.info("Test passed: test_js_prompt")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.alert
def test_authentication_window(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://admin:admin@the-internet.herokuapp.com/basic_auth")
        logger.info("Test passed: test_authentication_window")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.alert
def test_simple_iframe(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://demo.xqa.io/iframe-testing/iframe-testing.html")
        driver.switch_to.frame(driver.find_element(By.ID, "simple-iframe"))

        username_input = driver.find_element(By.CSS_SELECTOR, "#username")
        username_input.send_keys("johndoe")

        password_input = driver.find_element(By.CSS_SELECTOR, "#password")
        password_input.send_keys("thisisademopassword")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        alert = wait_for_alert_visibility(driver)
        logger.info("Alert is present, proceeding to accept it.")
        alert_text = alert.text
        assert alert_text == "Simple iframe form submitted!"
        alert.accept()

        logger.info("Test passed: test_simple_iframe")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


@pytest.mark.alert
def test_nested_iframe(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://demo.xqa.io/iframe-testing/iframe-testing.html")
        outer_frame = driver.find_element(By.CSS_SELECTOR, "#outer-iframe")
        driver.switch_to.frame(outer_frame)

        inner_frame = driver.find_element(By.CSS_SELECTOR, "#inner-iframe")
        driver.switch_to.frame(inner_frame)

        product_name = driver.find_element(By.CSS_SELECTOR, "#product")
        product_name.send_keys("selenium")

        quantity_input = driver.find_element(By.CSS_SELECTOR, "#quantity")
        quantity_input.send_keys("10")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        alert = wait_for_alert_visibility(driver)
        logger.info("Alert is present, proceeding to accept it.")
        alert_text = alert.text
        assert alert_text == "Nested iframe form submitted!"
        alert.accept()
        logger.info("Test passed: test_nested_iframe")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")

@pytest.mark.smoke
def test_handle_browser_windows(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

        original_windows = driver.window_handles
        original_window = driver.current_window_handle

        link = wait_for_element_visibility(
            driver, (By.CSS_SELECTOR, "a[href='http://www.orangehrm.com']")
        )
        if not link:
            raise NoSuchElementException("Link to OrangeHRM not found.")
        link.click()

        # Wait until a new window opens
        WebDriverWait(driver, 10).until(
            lambda d: len(d.window_handles) > len(original_windows)
        )

        new_tab = [
            handle for handle in driver.window_handles if handle not in original_windows
        ][0]
        driver.switch_to.window(new_tab)

        assert "OrangeHRM" in driver.title
        driver.find_element(By.XPATH, "//a[normalize-space()='Pricing']").click()

        # assert (
        #     driver.title
        #     == "Human Resources Management Software | OrangeHRM HR Software"
        # )

        driver.close()
        driver.switch_to.window(original_window)

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Username']").send_keys(
            "Admin"
        )
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']").send_keys(
            "admin123"
        )
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.title_is("OrangeHRM"))
        assert driver.title == "OrangeHRM"

        logger.info("Test passed: test_handle_browser_windows")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed: {type(e).__name__}: {e}")
