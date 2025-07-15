from selenium.webdriver.common.by import By


def test_full_xpath(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(
        By.XPATH, "/html/body/div[6]/div[1]/div[2]/div[2]/form/input"
    ).send_keys("Lenovo Thinkpad Carbon Laptop")
    driver.find_element(
        By.XPATH, "/html[1]/body[1]/div[6]/div[1]/div[2]/div[2]/form[1]/button[1]"
    ).click()


def test_relative_xpath(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(By.XPATH, "//*[@id='small-searchterms']").send_keys(
        "Lenovo Thinkpad Carbon Laptop"
    )
    driver.find_element(By.XPATH, "//button[normalize-space()='Search']").click()


def test_and_xpath_option(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(
        By.XPATH, "//input[@id='small-searchterms' and @placeholder='Search store']"
    ).send_keys("Lenovo Thinkpad Carbon Laptop")
    driver.find_element(By.XPATH, "//button[normalize-space()='Search']").click()


def test_or_xpath_option(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(
        By.XPATH, "//input[@id='small-searchterms' or @aria-label='Search store']"
    ).send_keys("Lenovo Thinkpad Carbon Laptop")
    driver.find_element(By.XPATH, "//button[normalize-space()='Search']").click()


def test_contains_xpath_option(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(By.XPATH, "//input[contains(@id,'search')]").send_keys(
        "Lenovo Thinkpad Carbon Laptop"
    )
    driver.find_element(By.XPATH, "//button[normalize-space()='Search']").click()


def test_starts_with_xpath_option(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(
        By.XPATH, "//input[starts-with(@placeholder,'Search')]"
    ).send_keys("Lenovo Thinkpad Carbon Laptop")
    driver.find_element(By.XPATH, "//button[normalize-space()='Search']").click()


def test_text(setup_teardown):
    driver = setup_teardown
    driver.get("https://demo.nopcommerce.com/")
    driver.find_element(
        By.XPATH, "//input[starts-with(@placeholder,'Search')]"
    ).send_keys("Lenovo Thinkpad Carbon Laptop")
    driver.find_element(By.XPATH, "//button[text()='Search']").click()
