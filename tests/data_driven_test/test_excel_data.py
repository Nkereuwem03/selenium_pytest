from utils.logger import logger
import pytest
import time
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.wait_helper import wait_for_element_presence
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from utils.paths import get_absolute_path
from utils.excel_reader import (
    get_row_count,
    read_data,
    write_data,
    fill_red_colour,
    fill_green_colour,
)

EXCEL_PATH = get_absolute_path("data", "excel_data.xlsx")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def safe_navigate_to_url(driver, url, max_retries=MAX_RETRIES):
    """Safely navigate to URL with retry logic for network issues."""
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Attempting to navigate to {url} (attempt {attempt + 1}/{max_retries})"
            )
            driver.get(url)

            # Wait for page to be ready
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Verify we can find key elements on the page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#principal"))
            )

            logger.info("Successfully navigated to the page")
            return True

        except (TimeoutException, WebDriverException) as e:
            logger.warning(f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(
                    f"Failed to navigate to {url} after {max_retries} attempts"
                )
                return False

    return False


def safe_fill_field(driver, selector, value, field_name):
    """Safely fill a form field with retry logic."""
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.clear()
        element.send_keys(str(value))
        logger.debug(f"Successfully filled {field_name} with value: {value}")
        return True
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Failed to fill {field_name}: {type(e).__name__}: {e}")
        return False


def safe_select_dropdown(driver, selector, value, field_name):
    """Safely select dropdown option with retry logic."""
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, selector))
        )
        select = Select(select_element)
        select.select_by_visible_text(str(value))
        logger.debug(f"Successfully selected {field_name} with value: {value}")
        return True
    except (TimeoutException, NoSuchElementException, ValueError) as e:
        logger.error(f"Failed to select {field_name}: {type(e).__name__}: {e}")
        return False


def safe_click_calculate(driver):
    """Safely click the calculate button."""
    try:
        # Try multiple possible selectors for the calculate button
        selectors = [
            "//div[@class='cal_div']//a[1]/img",
            "//div[@class='cal_div']//a[1]",
            "//img[contains(@src, 'calculate')]",
            "//a[contains(@onclick, 'calculate')]",
        ]

        for selector in selectors:
            try:
                calc_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].click();", calc_btn)
                logger.debug("Successfully clicked calculate button")
                return True
            except (TimeoutException, NoSuchElementException):
                continue

        logger.error("Could not find or click calculate button")
        return False

    except Exception as e:
        logger.error(f"Error clicking calculate button: {type(e).__name__}: {e}")
        return False


def safe_get_result(driver):
    """Safely get the calculation result."""
    try:
        # Wait for result to appear
        result_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#resp_matval strong"))
        )

        # Additional wait to ensure result is fully loaded
        time.sleep(1)

        result_text = result_elem.text.strip()
        if not result_text:
            raise ValueError("Result element found but text is empty")

        actual_value = float(result_text.replace(",", ""))
        logger.debug(f"Successfully retrieved result: {actual_value}")
        return actual_value

    except (TimeoutException, NoSuchElementException, ValueError) as e:
        logger.error(f"Failed to get result: {type(e).__name__}: {e}")
        return None


def test_fixed_deposit_calculator(setup_teardown):
    driver = setup_teardown
    file = EXCEL_PATH
    sheet = "Sheet3"

    try:
        rows = get_row_count(file, sheet)
        logger.info(f"Found {rows} rows in Excel sheet")
    except Exception as e:
        pytest.fail(f"Failed to read Excel file: {type(e).__name__}: {e}")

    # Navigate to the website with retry logic
    url = "https://www.moneycontrol.com/fixed-income/calculator/state-bank-of-india/fixed-deposit-calculator-SBI-BSB001.html"
    if not safe_navigate_to_url(driver, url):
        pytest.fail("Failed to navigate to the calculator website")

    test_passed = 0
    test_failed = 0
    test_skipped = 0

    try:
        for row in range(2, rows + 1):
            logger.info(f"Processing row {row}")

            try:
                principal = read_data(file, sheet, row, 1)
                rate = read_data(file, sheet, row, 2)
                period = read_data(file, sheet, row, 3)
                period_unit = read_data(file, sheet, row, 4)
                frequency = read_data(file, sheet, row, 5)
                expected_value = read_data(file, sheet, row, 6)

                # Check if any required field is None or empty
                if any(
                    value is None or str(value).strip() == ""
                    for value in [
                        principal,
                        rate,
                        period,
                        period_unit,
                        frequency,
                        expected_value,
                    ]
                ):
                    logger.warning(f"Row {row}: Skipping due to empty/None values")
                    write_data(file, sheet, row, 8, "skipped")
                    test_skipped += 1
                    continue

                # Fill form fields
                if not safe_fill_field(driver, "#principal", principal, "Principal"):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                if not safe_fill_field(driver, "#interest", rate, "Interest Rate"):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                if not safe_fill_field(driver, "#tenure", period, "Period"):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                if not safe_select_dropdown(
                    driver, "tenurePeriod", period_unit, "Period Unit"
                ):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                if not safe_select_dropdown(
                    driver, "frequency", frequency, "Frequency"
                ):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                # Click calculate button
                if not safe_click_calculate(driver):
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                # Get result
                actual_value = safe_get_result(driver)
                if actual_value is None:
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1
                    continue

                # Compare results
                expected_value = float(expected_value)
                if round(actual_value, 2) == round(expected_value, 2):
                    logger.info(
                        f"Row {row}: PASSED - Expected: {expected_value}, Actual: {actual_value}"
                    )
                    write_data(file, sheet, row, 8, "pass")
                    fill_green_colour(file, sheet, row, 8)
                    test_passed += 1
                else:
                    logger.warning(
                        f"Row {row}: FAILED - Expected: {expected_value}, Actual: {actual_value}"
                    )
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)
                    test_failed += 1

            except Exception as e:
                logger.error(f"[Row {row}] Unexpected error: {type(e).__name__}: {e}")
                write_data(file, sheet, row, 8, "fail")
                fill_red_colour(file, sheet, row, 8)
                test_failed += 1

    except Exception as e:
        logger.error(f"Critical test failure: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")

    finally:
        # Log test summary
        total_tests = test_passed + test_failed + test_skipped
        logger.info("=" * 50)
        logger.info("TEST SUMMARY")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {test_passed}")
        logger.info(f"Failed: {test_failed}")
        logger.info(f"Skipped: {test_skipped}")
        logger.info("=" * 50)

        # Fail the test if there were any failures
        if test_failed > 0:
            pytest.fail(
                f"Test completed with {test_failed} failures out of {total_tests} tests"
            )
