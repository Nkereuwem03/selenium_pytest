"""This code is part of a Selenium-based test automation framework for web applications.
It includes classes for handling dashboard, profile, and settings pages,
as well as tests for JavaScript alerts, iframes, and browser windows.
"""

from selenium.webdriver.common.by import By
from utils.logger import logger
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Dashboard page class for dashboard-specific functionalities."""

    def get_welcome_message(self):
        """Get the welcome message text from the dashboard."""
        return self.find_element(By.CSS_SELECTOR, "h1").text

    def click_logout(self):
        """Click the logout button on the dashboard."""
        self.click(By.CSS_SELECTOR, "a.logout")

    def navigate_to_profile(self):
        """Navigate to the user profile page."""
        self.click(By.CSS_SELECTOR, "a.profile")
        return ProfilePage(self.driver)

    def navigate_to_settings(self):
        """Navigate to the settings page."""
        self.click(By.CSS_SELECTOR, "a.settings")
        return SettingsPage(self.driver)


class ProfilePage(BasePage):
    """Profile page class for profile-specific functionalities."""

    def get_profile_info(self):
        """Get the profile information text."""
        return self.find_element(By.CSS_SELECTOR, "div.profile-info").text


class SettingsPage(BasePage):
    """Settings page class for settings-specific functionalities."""

    def change_password(self, old_password, new_password):
        """Change the user's password."""
        self.enter_text(old_password, By.CSS_SELECTOR, "input[name='old_password']")
        self.enter_text(new_password, By.CSS_SELECTOR, "input[name='new_password']")
        self.click(By.CSS_SELECTOR, "button[type='submit']")
        logger.info("Password changed successfully.")
        return self

    def get_settings_info(self):
        """Get the settings information text."""
        return self.find_element(By.CSS_SELECTOR, "div.settings-info").text
