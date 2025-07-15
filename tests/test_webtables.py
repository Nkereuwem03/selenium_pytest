from selenium.webdriver.common.by import By
from utils.wait_helper import (
    wait_for_element_presence,
    wait_for_elements_presence,
    wait_for_element_visibility,
)
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest
from utils.logger import logger


def test_static_table(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testautomationpractice.blogspot.com/")

        # no of rows and columns
        rows = wait_for_elements_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr")
        )
        columns = wait_for_elements_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[1]/th")
        )

        # read specific row and column data
        heading = wait_for_element_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[1]/th[1] ")
        ).text
        data = wait_for_element_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[2]/td[1] ")
        ).text

        # read all rows and columns data
        for r in range(2, len(rows) + 1):
            for c in range(1, len(columns) + 1):
                data = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[{c}]"
                ).text
                logger.info(data, end="   ")
            logger.info("")

        # read data based on conditions
        for r in range(2, len(rows) + 1):
            author_name = driver.find_element(
                By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[2]"
            ).text
            if author_name == "Mukesh":
                book_name = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[1]"
                ).text
                price = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[4]"
                ).text
                logger.info(book_name, "  ", author_name, "  ", price)
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")


def test_dynamic_table(setup_teardown):
    driver = setup_teardown
    try:
        driver.get("https://testautomationpractice.blogspot.com/")

        # no of rows and columns
        rows = wait_for_elements_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr")
        )
        columns = wait_for_elements_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[1]/th")
        )

        # read specific row and column data
        heading = wait_for_element_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[1]/th[1] ")
        ).text
        data = wait_for_element_presence(
            driver, (By.XPATH, "//table[@name='BookTable']/tbody/tr[2]/td[1] ")
        ).text

        # read all rows and columns data
        for r in range(2, len(rows) + 1):
            for c in range(1, len(columns) + 1):
                data = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[{c}]"
                ).text
                print(data, end="   ")
            print()

        # read data based on conditions
        for r in range(2, len(rows) + 1):
            author_name = driver.find_element(
                By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[2]"
            ).text
            if author_name == "Mukesh":
                book_name = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[1]"
                ).text
                price = driver.find_element(
                    By.XPATH, f"//table[@name='BookTable']/tbody/tr[{r}]/td[4]"
                ).text
                print(book_name, "  ", author_name, "  ", price)
    except (TimeoutException, NoSuchElementException) as e:
        logger.info(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
