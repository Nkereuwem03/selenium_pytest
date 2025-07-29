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
from selenium.webdriver.remote.webdriver import WebDriver
from openpyxl.styles import PatternFill

dotenv.load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "127.0.0.1"),  # Make it configurable
    "port": int(os.getenv("DATABASE_PORT", "3306")),
    "user": "root",
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": "test_data",
}

for key, value in DB_CONFIG.items():
    if value is None or str(value).strip() == "":
        logger.error(f"{key} is missing or blank in the .env file.")
        raise ValueError(f"Missing environment variable: {key}")

DB_OPERATIONS = {
    "CREATE_TABLE": """
        CREATE TABLE IF NOT EXISTS fixed_deposits (
            id INT PRIMARY KEY AUTO_INCREMENT,
            fd_amount_rs INT NOT NULL,
            fd_period_value INT NOT NULL,
            fd_period_unit VARCHAR(10), 
            interest_rate DECIMAL(5, 2) NOT NULL, 
            compounding_frequency VARCHAR(20) NOT NULL, 
            maturity_amount_lakh DECIMAL(10, 1) NOT NULL, 
            expected_result VARCHAR(10) NOT NULL, 
            actual_result VARCHAR(10) 
        );
    """,
    "INSERT": """
        INSERT INTO fixed_deposits (
            fd_amount_rs,
            fd_period_value,
            fd_period_unit,
            interest_rate,
            compounding_frequency,
            maturity_amount_lakh,
            expected_result,
            actual_result) 
            VALUES
            (20000, 2, 'years', 10.00, 'Monthly', 0.2, 'pass', NULL),
            (40000, 5, 'years', 15.00, 'Quarterly', 0.8, 'pass', NULL),
            (50000, 3, 'months', 10.00, 'Half Yearly', 0.6, 'pass', NULL),
            (75000, 2, 'months', 12.00, 'Yearly', 0.9, 'pass', NULL),
            (85000, 2, 'days', 12.00, 'Yearly', 2.1, 'fail', NULL);
    """,
    "UPDATE_PASS": "UPDATE fixed_deposits SET actual_result='pass' WHERE id = %s",
    "UPDATE_FAIL": "UPDATE fixed_deposits SET actual_result='fail' WHERE id = %s",
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


def find_element(driver: WebDriver, locator: tuple, data):
    element = wait_for_element_presence(driver, locator)
    element.clear()
    element.send_keys(data)


@pytest.mark.skipif(
    not os.getenv("DATABASE_PASSWORD"), reason="Database credentials not available"
)
def test_fixed_deposit_calculator(setup_teardown):
    """Orchestrates the data-driven test for the fixed deposit calculator."""
    all_test_data = get_test_data()
    if len(all_test_data) == 0:
        logger.warning("No test data found in the database.")
        pytest.fail("No test data available.")

    driver = setup_teardown
    results = []

    try:
        driver.get("https://fd-calculator.in/result")
        for test_case in all_test_data:
            if any(
                value is None or (isinstance(value, str) and value.strip() == "")
                for key, value in test_case.items()
                if key not in ["id", "actual_result"]
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
                find_element(
                    driver,
                    (By.CSS_SELECTOR, "#amountInputField"),
                    str(test_case["fd_amount_rs"]),
                )
                find_element(
                    driver,
                    (By.CSS_SELECTOR, "#periodInputField"),
                    str(test_case["fd_period_value"]),
                )
                Select(
                    driver.find_element(By.ID, "amountSelectField")
                ).select_by_visible_text(str(test_case["fd_period_unit"]).strip())

                find_element(
                    driver,
                    (By.CSS_SELECTOR, "#interestInputField"),
                    str(test_case["interest_rate"]),
                )

                Select(
                    driver.find_element(By.ID, "frequencySelectField")
                ).select_by_visible_text(test_case["compounding_frequency"])

                calc_btn = driver.find_element(By.ID, "calculateButton")
                driver.execute_script("arguments[0].click();", calc_btn)

                result_elem = wait_for_element_presence(
                    driver, (By.CSS_SELECTOR, "#futureValue")
                )

                actual_value = float(result_elem.text.replace("Lakh", ""))
                expected_value = float(test_case["maturity_amount_lakh"])

                if round(actual_value, 1) == round(expected_value, 1):
                    results.append({"id": row_id, "status": "pass"})
                else:
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
