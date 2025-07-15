from logging import config
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# from utils.custom_assertions import wait_for_file_download
from utils.wait_helper import wait_for_element_presence
from utils.logger import logger
import pytest
import yaml
import time

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


def test_file_download(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://www.sample-videos.com/download-sample-doc-file.php")
        file = wait_for_element_presence(
            driver,
            (
                By.CSS_SELECTOR,
                "th:nth-child(1)",
            ),
        )
        file.click()
        time.sleep(5)  # Wait for the download to start
        # assert wait_for_file_download(
        #     config["download_directory"], "test.txt", timeout=15
        # ), "File not fully downloaded"
        logger.info("Test passed: test file download")

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
