import yaml
from utils.custom_assertions import (
    assert_element_is_displayed,
    assert_element_text,
)
from utils.logger import logger
import pytest
from selenium.webdriver.common.by import By
from utils.paths import get_absolute_path
import os
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

with open("config/config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


def test_app_commands(setup_teardown):
    driver = setup_teardown
    driver.get("https://testpages.eviltester.com/styled/basic-html-form-test.html")
    driver.implicitly_wait(config["implicit_wait"])
    # driver.implicitly_wait(config.get("timeouts", {}).get("implicit", 10))

    try:
        title = driver.title
        current_url = driver.current_url
        page_source = driver.page_source

        heading_text = driver.find_element(By.CSS_SELECTOR, "div[class='page-body'] h1")
        assert_element_is_displayed(heading_text, "Heading")
        assert_element_text(heading_text, "Basic HTML Form Example", "Heading Text")

        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        comments_input = driver.find_element(By.NAME, "comments")
        file_input = driver.find_element(By.NAME, "filename")
        file_path = get_absolute_path(
            "data", "upload_files", "file-example_PDF_1MB.pdf"
        )
        checkboxes = driver.find_elements(By.NAME, "checkboxes[]")
        radio_btns = driver.find_elements(By.NAME, "radioval")
        multi_select = Select(
            driver.find_element(By.CSS_SELECTOR, "select[name='multipleselect[]']")
        )
        dropdowns = driver.find_elements(
            By.CSS_SELECTOR, "select[name='dropdown'] option"
        )
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[value='submit']")

        assert_element_is_displayed(username_input, "Username Input")
        assert username_input.is_enabled()
        username_input.clear()
        username_input.send_keys("John")
        assert username_input.get_attribute("value") == "John"

        password_input.send_keys("Password123.")

        comments_input.clear()
        comments_input.send_keys("This is a multi-line text-area")

        file_input.send_keys(file_path)
        #         assert (
        #             os.path.basename(file_input.get_attribute("value"))
        #             == "file-example_PDF_1MB.pdf"
        #         )
        #           - file-example_PDF_1MB.pdf
        #   + C:\fakepath\file-example_PDF_1MB.pdf
        assert file_input.get_attribute("value").endswith("file-example_PDF_1MB.pdf")

        for checkbox in checkboxes:
            if checkbox.is_selected():
                checkbox.click()
            assert not checkbox.is_selected()
            val = checkbox.get_attribute("value")
            if val in ["cb1", "cb2"]:
                checkbox.click()
            if checkbox.get_attribute("value") == "cb3":
                assert not checkbox.is_selected()

        for radio_btn in radio_btns:
            if radio_btn.get_attribute("value") == "rd1":
                radio_btn.click()
            if not radio_btn.get_attribute("value") == "rd1":
                assert not radio_btn.is_selected()

        multi_select.deselect_all()
        select_options = ["Selection Item 2", "Selection Item 4"]
        # selected = [option.text for option in multi_select.all_selected_options]
        # assert set(selected) == set(select_options)
        for select_option in select_options:
            multi_select.select_by_visible_text(select_option)

        for dropdown in dropdowns:
            if dropdown.text == "Drop Down Item 5":
                dropdown.click()

        submit_btn.click()
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Test failed due to: {type(e).__name__}: {e}")
        pytest.fail(f"Test failed due to: {type(e).__name__}: {e}")
        # screenshot_path = f"screenshots/{type(e).__name__}.png"
        # os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        # driver.save_screenshot(screenshot_path)
        # raise e
