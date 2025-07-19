"""Module for managing Selenium WebDriver instances based on configuration."""

import yaml
import tempfile
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils.logger import logger

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class BrowserManager:
    """Manages Selenium WebDriver instances for different browsers."""

    ALLOWED_BROWSERS = ["chrome", "firefox"]

    def __init__(self, browser_name=None):
        self.driver = None
        self.browser_name = browser_name or config.get("browser", "chrome").lower()
        self.headless = config.get("headless", False)
        self.download_dir = os.path.abspath(
            config.get("download_directory", "./downloads")
        )
        self.user_data_dir = None  # Store unique user data directory for Chrome

        if self.browser_name not in self.ALLOWED_BROWSERS:
            logger.warning(f"Unsupported browser: '{self.browser_name}'")
            logger.warning(
                f"Supported browsers are: {', '.join(self.ALLOWED_BROWSERS)}"
            )
            raise ValueError(
                f"Unsupported browser: '{self.browser_name}'. "
                f"Allowed values: {', '.join(self.ALLOWED_BROWSERS)}"
            )

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def start_browser(self):
        """Initializes the WebDriver based on the specified browser with retry logic."""
        retries = config.get("retry_attempts", 3)
        for attempt in range(retries):
            try:
                if self.browser_name == "chrome":
                    options = ChromeOptions()
                    prefs = {
                        "download.default_directory": self.download_dir,
                        "profile.default_content_settings.popups": 0,
                        "directory_upgrade": True,
                        "profile.default_content_setting_values.notifications": 2,
                        "profile.managed_default_content_settings.images": 2,  # Block images for faster loading
                    }
                    options.add_experimental_option("prefs", prefs)

                    # Use a unique temporary user data directory
                    self.user_data_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
                    options.add_argument(f"--user-data-dir={self.user_data_dir}")

                    # Enhanced headless configuration for CI environments
                    if self.headless:
                        options.add_argument("--headless=new")
                        options.add_argument("--no-sandbox")
                        options.add_argument("--disable-dev-shm-usage")
                        options.add_argument("--disable-gpu")
                        options.add_argument("--disable-setuid-sandbox")
                        options.add_argument("--disable-software-rasterizer")
                        options.add_argument("--disable-background-networking")
                        options.add_argument("--disable-background-timer-throttling")
                        options.add_argument("--disable-renderer-backgrounding")
                        options.add_argument("--disable-backgrounding-occluded-windows")
                        options.add_argument("--disable-client-side-phishing-detection")
                        options.add_argument("--disable-crash-reporter")
                        options.add_argument("--disable-oopr-debug-crash-dump")
                        options.add_argument("--no-crash-upload")
                        options.add_argument("--disable-low-res-tiling")
                        options.add_argument("--window-size=1920,1080")
                        options.add_argument(
                            "--disable-images"
                        )  # Disable image loading
                        options.add_argument(
                            "--disable-javascript"
                        )  # Disable JS for faster loading
                        options.add_argument(
                            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        )
                        options.add_argument("--disable-extensions")
                        options.add_argument("--disable-plugins")
                        options.add_argument("--enable-logging")
                        options.add_argument("--log-level=0")
                        options.add_argument(
                            "--enable-features=NetworkService,NetworkServiceInProcess"
                        )

                    # Additional stability options
                    options.add_argument("--disable-popup-blocking")
                    options.add_argument("--disable-infobars")
                    options.add_argument("--disable-notifications")
                    options.add_argument("--disable-web-security")
                    options.add_argument("--allow-running-insecure-content")
                    options.add_argument("--ignore-certificate-errors")
                    options.add_argument("--ignore-ssl-errors")
                    options.add_argument("--ignore-certificate-errors-spki-list")
                    options.add_argument("--ignore-certificate-errors")
                    options.add_experimental_option(
                        "excludeSwitches", ["enable-automation"]
                    )
                    options.add_experimental_option("useAutomationExtension", False)
                    options.add_argument(
                        "--disable-blink-features=AutomationControlled"
                    )

                    self.driver = webdriver.Chrome(options=options)

                    # Set timeouts for CI environment
                    self.driver.implicitly_wait(config.get("implicit_wait", 10))
                    self.driver.set_page_load_timeout(
                        config.get("page_load_timeout", 60)
                    )  # Increased timeout
                    self.driver.set_script_timeout(30)

                    self.driver.maximize_window()

                elif self.browser_name == "firefox":
                    options = FirefoxOptions()
                    file_type = config.get("file_type", "application/octet-stream")
                    options.set_preference("browser.download.folderList", 2)
                    options.set_preference("browser.download.dir", self.download_dir)
                    options.set_preference(
                        "browser.download.manager whether to show when starting", False
                    )
                    options.set_preference(
                        "browser.helperApps.neverAsk.saveToDisk", file_type
                    )
                    options.set_preference("dom.webnotifications.enabled", False)
                    options.set_preference("dom.push.enabled", False)
                    options.set_preference(
                        "permissions.default.image", 2
                    )  # Block images
                    options.set_preference("javascript.enabled", False)  # Disable JS

                    if self.headless:
                        options.add_argument("-headless")

                    self.driver = webdriver.Firefox(options=options)

                    # Set timeouts
                    self.driver.implicitly_wait(config.get("implicit_wait", 10))
                    self.driver.set_page_load_timeout(
                        config.get("page_load_timeout", 60)
                    )
                    self.driver.set_script_timeout(30)

                    self.driver.maximize_window()

                logger.info(
                    f"Browser {self.browser_name} started successfully on attempt {attempt + 1}"
                )
                return self.driver

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to start browser: {e}")
                if self.user_data_dir and os.path.exists(self.user_data_dir):
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                    self.user_data_dir = None
                if attempt == retries - 1:
                    logger.error(f"Failed to start browser after {retries} attempts")
                    raise
        return None

    def quit_browser(self):
        """Closes the WebDriver instance and cleans up user data directory."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser session ended successfully")
            except Exception as e:
                logger.warning(f"Error quitting browser: {e}")
            self.driver = None

        if self.user_data_dir and os.path.exists(self.user_data_dir):
            try:
                shutil.rmtree(self.user_data_dir, ignore_errors=True)
                logger.info(f"Cleaned up user data directory: {self.user_data_dir}")
            except Exception as e:
                logger.warning(
                    f"Failed to clean up user data directory {self.user_data_dir}: {e}"
                )
            self.user_data_dir = None
