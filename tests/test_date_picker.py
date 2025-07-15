import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from utils.wait_helper import wait_for_element_presence
from utils.logger import logger
import pytest


def test_standard_date(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://testautomationpractice.blogspot.com/")

        wait_for_element_presence(driver, (By.CSS_SELECTOR, "#datepicker")).click()

        day = 10
        target_date = "march 2028"
        target_date_dt = datetime.strptime(target_date, "%B %Y").date()

        while True:
            current_month = wait_for_element_presence(
                driver, (By.CSS_SELECTOR, ".ui-datepicker-month")
            ).text
            current_year = wait_for_element_presence(
                driver, (By.CSS_SELECTOR, ".ui-datepicker-year")
            ).text
            current_date_str = f"{current_month} {current_year}".lower()
            current_date_dt = datetime.strptime(current_date_str, "%B %Y").date()

            if target_date_dt == current_date_dt:
                break

            if target_date_dt < current_date_dt:
                wait_for_element_presence(
                    driver,
                    (By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-w']"),
                ).click()
            else:
                wait_for_element_presence(
                    driver,
                    (By.XPATH, "//span[@class='ui-icon ui-icon-circle-triangle-e']"),
                ).click()

        driver.find_element(By.XPATH, f"//a[@data-date={day}]").click()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_standard_date_2(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://testautomationpractice.blogspot.com/")

        wait_for_element_presence(driver, (By.CSS_SELECTOR, "#txtDate")).click()

        day = 10
        month = "Mar"
        year = "2020"

        select_month_element = driver.find_element(
            By.CSS_SELECTOR, "select[aria-label='Select month']"
        )
        select_month = Select(select_month_element)
        select_month.select_by_visible_text(month)

        select_year_element = driver.find_element(
            By.CSS_SELECTOR, "select[aria-label='Select year']"
        )
        select_year = Select(select_year_element)
        select_year.select_by_visible_text(year)

        driver.find_element(
            By.XPATH, f"//a[@class='ui-state-default' and @data-date='{day}']"
        ).click()

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_bootstrap_date(setup_teardown):
    driver = setup_teardown

    try:
        driver.get("https://testautomationpractice.blogspot.com/")

        wait_for_element_presence(driver, (By.CSS_SELECTOR, "#start-date")).send_keys(
            "07/04/2024"
        )
        wait_for_element_presence(driver, (By.CSS_SELECTOR, "#end-date")).send_keys(
            "07/05/2024"
        )
        wait_for_element_presence(driver, (By.CSS_SELECTOR, ".submit-btn")).click()

        date_range = driver.find_element(By.CSS_SELECTOR, "#result").text
        assert date_range == "You selected a range of 1 days."

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
