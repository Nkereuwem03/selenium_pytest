from utils.logger import logger
import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
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


def test_fixed_deposit_calculator(setup_teardown):
    driver = setup_teardown
    file = EXCEL_PATH
    sheet = "Sheet3"
    rows = get_row_count(file, sheet)

    try:
        driver.get(
            "https://www.moneycontrol.com/fixed-income/calculator/state-bank-of-india/fixed-deposit-calculator-SBI-BSB001.html"
        )

        for row in range(2, rows + 1):
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
                continue

            # Convert to string to ensure send_keys compatibility
            principal = str(principal)
            rate = str(rate)
            period = str(period)

            driver.find_element(By.CSS_SELECTOR, "#principal").clear()
            driver.find_element(By.CSS_SELECTOR, "#principal").send_keys(principal)

            driver.find_element(By.CSS_SELECTOR, "#interest").clear()
            driver.find_element(By.CSS_SELECTOR, "#interest").send_keys(rate)

            driver.find_element(By.CSS_SELECTOR, "#tenure").clear()
            driver.find_element(By.CSS_SELECTOR, "#tenure").send_keys(period)

            try:
                Select(
                    driver.find_element(By.ID, "tenurePeriod")
                ).select_by_visible_text(str(period_unit))
            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"Test failed due to: {type(e).__name__}: {e}")
                write_data(file, sheet, row, 8, "fail")
                fill_red_colour(file, sheet, row, 8)
                continue

            try:
                Select(driver.find_element(By.ID, "frequency")).select_by_visible_text(
                    str(frequency)
                )
            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"Test failed due to: {type(e).__name__}: {e}")
                write_data(file, sheet, row, 8, "fail")
                fill_red_colour(file, sheet, row, 8)
                continue

            try:
                calc_btn = driver.find_element(
                    By.XPATH, "//div[@class='cal_div']//a[1]/img"
                )
                driver.execute_script("arguments[0].click();", calc_btn)
            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"Test failed due to: {type(e).__name__}: {e}")
                continue

            try:
                result_elem = wait_for_element_presence(
                    driver, (By.CSS_SELECTOR, "#resp_matval strong")
                )
                actual_value = float(result_elem.text.replace(",", ""))
                expected_value = float(expected_value)

                if round(actual_value, 2) == round(expected_value, 2):
                    write_data(file, sheet, row, 8, "pass")
                    fill_green_colour(file, sheet, row, 8)
                else:
                    write_data(file, sheet, row, 8, "fail")
                    fill_red_colour(file, sheet, row, 8)

            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"[Row {row}] Error during calculation: {e}")
                write_data(file, sheet, row, 8, "fail")
                fill_red_colour(file, sheet, row, 8)

    except (NoSuchElementException, TimeoutException, ValueError) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
