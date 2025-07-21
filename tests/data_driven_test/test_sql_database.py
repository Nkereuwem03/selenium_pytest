"""
Data-driven tests for a fixed deposit calculator.

This script reads test cases from a MySQL database, runs them against a web-based
calculator using Selenium, and updates the database with the test results.
"""

from mysql.connector import connect
from mysql.connector import Error
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from utils.logger import logger
import os
import dotenv
from utils.wait_helper import wait_for_element_presence
import pytest

dotenv.load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT"),
    "user": os.getenv("DATABASE_USER"),
    "passwd": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
}

for key, value in DB_CONFIG.items():
    if value is None or str(value).strip() == "":
        logger.error(f"{key} is missing or blank in the .env file.")
        raise ValueError(f"Missing environment variable: {key}")

DB_OPERATIONS = {
    "CREATE_TABLE": """
        CREATE TABLE IF NOT EXISTS fixed_deposits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Principal INT(100) NOT NULL,
            RateOfInterest DECIMAL(5, 2) NOT NULL,
            Period INT NOT NULL,
            PeriodUnit VARCHAR(20) NOT NULL,
            Frequency VARCHAR(50) NOT NULL,
            MaturityValue DECIMAL(12, 2) NOT NULL,
            Expected VARCHAR(10) NOT NULL,
            Result VARCHAR(10) NOT NULL
        );
    """,
    "INSERT": """
        INSERT INTO fixed_deposits (Principal, RateOfInterest, Period, PeriodUnit, Frequency, MaturityValue, Expected, Result)
        VALUES
        (20000, 10.00, 2, 'year(s)', 'Simple Interest', 24000.00, 'pass', ''),
        (40000, 15.00, 5, 'year(s)', 'Simple Interest', 70000.00, 'pass', ''),
        (50000, 10.00, 3, 'month(s)', 'Simple Interest', 51250.00, 'pass', ''),
        (75000, 12.00, 2, 'month(s)', 'Simple Interest', 76500.00, 'pass', ''),
        (75000, 12.00, 2, 'day(s)', 'Simple Interest', 75045.32, 'fail', '');
    """,
    "UPDATE_PASS": "UPDATE fixed_deposits SET Result='pass' WHERE id = %s",
    "UPDATE_FAIL": "UPDATE fixed_deposits SET Result='fail' WHERE id = %s",
    "SELECT": "SELECT * FROM fixed_deposits",
}


def init_db():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(DB_OPERATIONS["CREATE_TABLE"])
                connection.commit()
                logger.info("Table created successfully.")
                cursor.execute(DB_OPERATIONS["SELECT"])
                if not cursor.fetchall():
                    cursor.execute(DB_OPERATIONS["INSERT"])
                    connection.commit()
                    logger.info("Inserted sample test data.")
                return True
    except Error as e:
        logger.error(f"Database initialization error: {e}")
        return False


def get_test_data() -> list[dict]:
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(DB_OPERATIONS["SELECT"])
                test_data = cursor.fetchall()
                logger.info(f"Retrieved {len(test_data)} test case(s).")
                return test_data
    except Error as e:
        logger.error(f"Database error: {e}")
        return []


def update_results_in_db(results: list[dict]):
    """Updates the test results in the database in a single batch."""
    if not results:
        logger.warning("No results to update.")
        return

    passed_count = sum(1 for r in results if r["status"] == "pass")
    failed_count = len(results) - passed_count

    print(f"\nUpdating database: {passed_count} passed, {failed_count} failed.")
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                for result in results:
                    query = (
                        DB_OPERATIONS.get("UPDATE_PASS")
                        if result["status"] == "pass"
                        else DB_OPERATIONS.get("UPDATE_FAIL")
                    )
                    cursor.execute(query, (result["id"],))
                connection.commit()
            logger.info("Database update complete.")
    except Error as e:
        logger.error(f"Database error while updating results: {e}")


def fill_form(driver, tag, tag_name, data):
    driver.find_element(tag, tag_name).clear()
    driver.find_element(tag, tag_name).send_keys(data)


# @pytest.mark.skipif(not init_db(), reason="Database init failed")
@pytest.mark.skip(reason="site not ready")
def test_fixed_deposit_calculator(setup_teardown):
    """Orchestrates the data-driven test for the fixed deposit calculator."""
    all_test_data = get_test_data()
    if len(all_test_data) == 0:
        logger.warning("No test data found in the database.")
        pytest.fail("No test data available.")

    driver = setup_teardown
    results = []
    try:
        driver.get(
            "https://www.moneycontrol.com/fixed-income/calculator/state-bank-of-india/fixed-deposit-calculator-SBI-BSB001.html"
        )
        for test_case in all_test_data:
            if any(
                value is None or (isinstance(value, str) and value.strip() == "")
                for key, value in test_case.items()
                if key != "id"
            ):
                logger.warning(
                    f"Skipping case {test_case['id']} due to blank/None fields."
                )
                results.append({"id": test_case["id"], "status": "fail"})
                continue

            # if not isinstance(test_case["Principal"], (int, float)) or not isinstance(test_case["RateOfInterest"], (int, float)) or not isinstance(test_case["Period"], int):
            #     logger.warning(f"Skipping case {test_case['id']} due to invalid data types.")
            #     results.append({"id": test_case["id"], "status": "fail"})
            #     continue

            row_id = test_case["id"]
            try:
                fill_form(driver, By.CSS_SELECTOR, "#principal", test_case["Principal"])
                fill_form(
                    driver,
                    By.CSS_SELECTOR,
                    "#interest",
                    str(test_case["RateOfInterest"]),
                )
                fill_form(driver, By.CSS_SELECTOR, "#tenure", test_case["Period"])
                Select(
                    driver.find_element(By.ID, "tenurePeriod")
                ).select_by_visible_text(str(test_case["PeriodUnit"]))
                Select(driver.find_element(By.ID, "frequency")).select_by_visible_text(
                    str(test_case["Frequency"])
                )
                calc_btn = driver.find_element(
                    By.XPATH, "//div[@class='cal_div']//a[1]/img"
                )
                driver.execute_script("arguments[0].click();", calc_btn)

                result_elem = wait_for_element_presence(
                    driver, (By.CSS_SELECTOR, "#resp_matval strong")
                )
                actual_value = float(result_elem.text.replace(",", ""))
                expected_value = float(test_case["MaturityValue"])

                if round(actual_value, 2) == round(expected_value, 2):
                    logger.info(f"[ID: {row_id}] Test Passed")
                    results.append({"id": row_id, "status": "pass"})
                else:
                    logger.warning(
                        f"[ID: {row_id}] Test Failed. Expected: {expected_value}, Actual: {actual_value}"
                    )
                    results.append({"id": row_id, "status": "fail"})

            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"[ID: {row_id}] Test Failed with error: {e}")
                results.append({"id": row_id, "status": "fail"})
                continue

    except WebDriverException as browser_error:
        logger.error(f"A browser error occurred during UI testing: {browser_error}")
    except Error as db_error:
        logger.error(f"A database error occurred during UI testing: {db_error}")
    except ValueError as value_error:
        logger.error(f"A value error occurred during UI testing: {value_error}")

    update_results_in_db(results)
