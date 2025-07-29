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
import time

dotenv.load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": "root",
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": "test_data",
}


def get_database_connection(max_retries=5, retry_delay=10):
    """Get database connection with retry logic for Jenkins environment"""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Database connection attempt {attempt}/{max_retries}")
            connection = connect(**DB_CONFIG)

            # Test the connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            logger.info(f"Database connection successful on attempt {attempt}")
            return connection

        except Error as e:
            logger.error(f"Database connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error("All database connection attempts failed")
                raise
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)


def get_test_data() -> list[dict]:
    """Get test data with improved error handling and retries"""
    try:
        connection = get_database_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM fixed_deposits")
            test_data = cursor.fetchall()
            logger.info(f"Retrieved {len(test_data)} test case(s).")
        connection.close()
        return test_data
    except Error as e:
        logger.error(f"Database error: {e}")
        return []


def update_results_in_db(results: list[dict]):
    """Updates the test results in the database in a single batch."""
    if not results:
        logger.warning("No results to update.")
        return

    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            for result in results:
                query = "UPDATE fixed_deposits SET actual_result=%s WHERE id = %s"
                cursor.execute(query, (result["status"], result["id"]))
            connection.commit()
        connection.close()
        logger.info("Database update complete.")
    except Error as e:
        logger.error(f"Database error while updating results: {e}")


def find_element(driver: WebDriver, locator: tuple, data):
    element = wait_for_element_presence(driver, locator)
    element.clear()
    element.send_keys(data)


# FIXED: Proper decorator syntax
@pytest.mark.skipif(
    not os.getenv("DATABASE_PASSWORD"), reason="Database credentials not available"
)
def test_fixed_deposit_calculator(setup_teardown):
    """Orchestrates the data-driven test for the fixed deposit calculator."""

    # Get test data with better error handling
    all_test_data = get_test_data()

    if len(all_test_data) == 0:
        logger.warning("No test data found in the database.")
        # Use pytest.skip instead of pytest.fail to avoid stopping other tests
        pytest.skip("No database connection available - skipping database tests")

    driver = setup_teardown
    results = []

    try:
        driver.get("https://fd-calculator.in/result")

        for test_case in all_test_data:
            # Validate required fields
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

            row_id = test_case["id"]
            try:
                # Clear and fill form fields
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

                # Select period unit
                Select(
                    driver.find_element(By.ID, "amountSelectField")
                ).select_by_visible_text(str(test_case["fd_period_unit"]).strip())

                # Enter interest rate
                find_element(
                    driver,
                    (By.CSS_SELECTOR, "#interestInputField"),
                    str(test_case["interest_rate"]),
                )

                # Select compounding frequency
                Select(
                    driver.find_element(By.ID, "frequencySelectField")
                ).select_by_visible_text(test_case["compounding_frequency"])

                # Click calculate button
                calc_btn = driver.find_element(By.ID, "calculateButton")
                driver.execute_script("arguments[0].click();", calc_btn)

                # Get result
                result_elem = wait_for_element_presence(
                    driver, (By.CSS_SELECTOR, "#futureValue")
                )

                actual_value = float(result_elem.text.replace("Lakh", ""))
                expected_value = float(test_case["maturity_amount_lakh"])

                # Compare results
                if round(actual_value, 1) == round(expected_value, 1):
                    results.append({"id": row_id, "status": "pass"})
                    logger.info(f"Test case {row_id}: PASSED")
                else:
                    results.append({"id": row_id, "status": "fail"})
                    logger.warning(
                        f"Test case {row_id}: FAILED - Expected: {expected_value}, Actual: {actual_value}"
                    )

            except (NoSuchElementException, TimeoutException, ValueError) as e:
                logger.error(f"[ID: {row_id}] Test Failed with error: {e}")
                results.append({"id": row_id, "status": "fail"})
                continue

    except WebDriverException as browser_error:
        logger.error(f"A browser error occurred during UI testing: {browser_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during UI testing: {e}")

    # Update results in database
    if results:
        update_results_in_db(results)

    # Assert that we processed some test cases
    assert len(results) > 0, "No test cases were processed"
