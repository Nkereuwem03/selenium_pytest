"""This code is part of a Selenium-based test automation framework for web applications.
It includes classes for handling login, dashboard, profile, and settings pages,
as well as utilities for waiting for elements, handling alerts, and managing browser sessions.
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import yaml
from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from utils.logger import logger

with open("config/config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)
timeout = config.get("timeouts", {}).get("explicit", 10)


class LoginPage(BasePage):
    """Login page class for login-specific functionalities."""

    def enter_username(self, username):
        """Enter the username in the login form."""
        self.enter_text(username, By.CSS_SELECTOR, "input[name='username']")

    def enter_password(self, password):
        """Enter the password in the login form."""
        self.enter_text(password, By.CSS_SELECTOR, "input[name='password']")

    def click_login(self):
        """Click the login button."""
        self.click(By.CSS_SELECTOR, "button[type='submit']")

    def get_error_message(self):
        """Get the error message text if login fails."""
        return self.find_element(By.CSS_SELECTOR, ".error-message").text

    def login(self, username, password):
        """Perform the login action with the provided username and password."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        logger.info("Login action performed.")
        return self

    def is_login_successful(self):
        """Check if the login was successful by verifying the presence of a welcome message."""
        try:
            welcome_message = self.find_element(By.CSS_SELECTOR, "h1.welcome")
            return welcome_message.is_displayed()
        except NoSuchElementException:
            logger.error("Login failed: Welcome message not found.")
            return False

    def navigate_to_dashboard(self):
        """Navigate to the dashboard page after successful login."""
        if self.is_login_successful():
            self.click(By.CSS_SELECTOR, "a.dashboard")
            logger.info("Navigated to the dashboard page.")
            return DashboardPage(self.driver)
        else:
            logger.error("Login was not successful, cannot navigate to dashboard.")
            raise RuntimeError("Login failed, cannot navigate to dashboard.")
