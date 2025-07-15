from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.paths import get_absolute_path
from utils.logger import logger
import pytest


@pytest.mark.screenshot
def test_capture_screenshot(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://parabank.parasoft.com/parabank/index.htm")

        path = get_absolute_path("screenshots")
        driver.save_screenshot(f"{path}/parabank_homepage.png")
        # driver.get_screenshot_as_file(f"{path}/parabank_homepage.png")
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
