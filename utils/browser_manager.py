"""Module for managing Selenium WebDriver instances based on configuration."""

import yaml
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from utils.logger import logger

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class BrowserManager:
    """Manages Selenium WebDriver instances for different browsers."""

    ALLOWED_BROWSERS = ["chrome", "firefox"]

    def __init__(self, browser_name=None):
        self.driver = None
        self.browser_name = browser_name or config.get("browser", "chrome").lower()

        if self.browser_name not in self.ALLOWED_BROWSERS:
            logger.warning(f"Unsupported browser: '{self.browser_name}'")
            logger.warning(
                f"Supported browsers are: {', '.join(self.ALLOWED_BROWSERS)}"
            )
            raise ValueError(
                f"Unsupported browser: '{self.browser_name}'. "
                f"Allowed values: {', '.join(self.ALLOWED_BROWSERS)}"
            )

        self.headless = config.get("headless", False)
        self.download_dir = os.path.abspath(
            config.get("download_directory", "./downloads")
        )
        os.makedirs(self.download_dir, exist_ok=True)

    def start_browser(self):
        """Initializes the WebDriver based on the specified browser."""
        if self.browser_name == "chrome":
            options = ChromeOptions()
            prefs = {
                "download.default_directory": self.download_dir,
                "profile.default_content_settings.popups": 0,
                "directory_upgrade": True,
            }
            options.add_experimental_option("prefs", prefs)

            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--enable-logging")
                options.add_argument("--log-level=0")
                options.add_argument(
                    "--enable-features=NetworkService,NetworkServiceInProcess"
                )
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--remote-debugging-port=9222")

                # ✅ Prevent Chrome profile conflict in CI
                temp_user_data = tempfile.mkdtemp()
                options.add_argument(f"--user-data-dir={temp_user_data}")

            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), options=options
            )
            self.driver.maximize_window()

        elif self.browser_name == "firefox":
            options = FirefoxOptions()
            file_type = config.get("file_type", "application/octet-stream")
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", self.download_dir)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", file_type)
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)

            if self.headless:
                options.add_argument("-headless")

            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()), options=options
            )
            self.driver.maximize_window()

        return self.driver

    def quit_browser(self):
        """Closes the WebDriver instance if it exists."""
        if self.driver:
            self.driver.quit()
            self.driver = None
