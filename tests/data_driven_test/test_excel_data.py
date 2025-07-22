from time import time
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
from utils.excel_reader import get_row_count, read_data, update_cell, load_sheet
from openpyxl.styles import PatternFill


EXCEL_PATH = get_absolute_path("data", "excel_data.xlsx")
GREEN_FILL = PatternFill(start_color="60b212", end_color="60b212", fill_type="solid")
RED_FILL = PatternFill(start_color="ff0000", end_color="ff0000", fill_type="solid")

@pytest.mark.smoke
def test_fixed_deposit_calculator(setup_teardown):
    driver = setup_teardown
    max_retries = 3
    for attempt in range(max_retries):
        try:
            driver.set_page_load_timeout(60)
            driver.get("https://www.moneycontrol.com/fixed-income/calculator/state-bank-of-india/fixed-deposit-calculator-SBI-BSB001.html")
            break  # Success, exit retry loop
        except TimeoutException:
            if attempt == max_retries - 1:
                pytest.fail("Failed to load page after multiple attempts")
            logger.warning(f"Page load timeout, attempt {attempt + 1}, retrying...")
            time.sleep(5)  
    file = EXCEL_PATH

    sheet = load_sheet(file, "Sheet3")

    # sheet = "Sheet3"
    rows = get_row_count(file, "Sheet3")

    try:
        # driver.get(
        #     "https://www.moneycontrol.com/fixed-income/calculator/state-bank-of-india/fixed-deposit-calculator-SBI-BSB001.html"
        # )

        # for row in range(1, rows + 1):
        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):

            if all(cell is None or str(cell).strip() == "" for cell in row):
                continue

            # principal = read_data(file, sheet, row, 1)
            # rate = read_data(file, sheet, row, 2)
            # period = read_data(file, sheet, row, 3)
            # period_unit = read_data(file, sheet, row, 4)
            # frequency = read_data(file, sheet, row, 5)
            # expected_value = read_data(file, sheet, row, 6)

            principal = row[0]
            rate = row[1]
            period = row[2]
            period_unit = row[3]
            frequency = row[4]
            expected_value = row[5]

            # if(any(value is None or str(value).strip() == "" for value in [principal, rate, period, period_unit, frequency, expected_value])):
            #     logger.warning(f"Row {row}: Skipping due to empty/None values")
            #     write_data(file, sheet, row, 8, "skipped")
            #     continue

            logger.info(f"Processing row {row}")

            driver.find_element(By.CSS_SELECTOR, "#principal").clear()
            driver.find_element(By.CSS_SELECTOR, "#principal").send_keys(str(principal))

            driver.find_element(By.CSS_SELECTOR, "#interest").clear()
            driver.find_element(By.CSS_SELECTOR, "#interest").send_keys(str(rate))

            driver.find_element(By.CSS_SELECTOR, "#tenure").clear()
            driver.find_element(By.CSS_SELECTOR, "#tenure").send_keys(str(period))

            try:
                Select(
                    driver.find_element(By.ID, "tenurePeriod")
                ).select_by_visible_text(str(period_unit).strip())
            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"Test failed due to: {type(e).__name__}: {e}")
                update_cell(file, "Sheet3", idx, 8, value="fail", fill=RED_FILL)
                continue

            try:
                Select(driver.find_element(By.ID, "frequency")).select_by_visible_text(
                    str(frequency)
                )
            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"Test failed due to: {type(e).__name__}: {e}")
                update_cell(file, "Sheet3", idx, 8, value="fail", fill=RED_FILL)
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
                    update_cell(file, "Sheet3", idx, 8, value="pass", fill=GREEN_FILL)
                else:
                    update_cell(file, "Sheet3", idx, 8, value="fail", fill=RED_FILL)

            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"[Row {row}] Error during calculation: {e}")
                pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
                update_cell(file, "Sheet3", idx, 8, value="fail", fill=RED_FILL)

    except (NoSuchElementException, TimeoutException, ValueError) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
