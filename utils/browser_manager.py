"""Module for managing Selenium WebDriver instances based on configuration."""

import yaml
import os
import tempfile
import time
import atexit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from utils.logger import logger
import shutil

# Global list to track temporary directories for cleanup
_temp_directories = []


def load_config():
    """
    Load configuration from YAML file with fallback to defaults.

    Returns:
        dict: Configuration dictionary
    """
    config_path = "config/config.yaml"
    default_config = {
        "browser": "chrome",
        "headless": False,
        "download_directory": "./downloads",
        "file_type": "application/octet-stream",
        "timeout": 30,
        "retry_attempts": 3,
        "window_size": "1920,1080",
    }

    if not os.path.exists(config_path):
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            # Merge with defaults to ensure all keys exist
            return {**default_config, **config}
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        logger.warning("Using default configuration")
        return default_config


def cleanup_temp_directories():
    """Clean up all temporary directories created during execution."""
    global _temp_directories
    for temp_dir in _temp_directories:
        try:
            if os.path.exists(temp_dir):

                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    _temp_directories.clear()


# Register cleanup function
atexit.register(cleanup_temp_directories)


class BrowserManager:
    """Manages Selenium WebDriver instances for different browsers."""

    ALLOWED_BROWSERS = ["chrome", "firefox"]

    def __init__(self, browser_name=None, headless=None):
        """
        Initialize BrowserManager.

        Args:
            browser_name (str): Name of the browser ('chrome' or 'firefox')
            headless (bool): Whether to run browser in headless mode
        """
        self.config = load_config()
        self.driver = None
        self.browser_name = (
            browser_name or self.config.get("browser", "chrome")
        ).lower()
        self.headless = (
            headless if headless is not None else self.config.get("headless", False)
        )
        self.temp_user_data_dir = None

        # Validate browser name
        if self.browser_name not in self.ALLOWED_BROWSERS:
            logger.error(f"Unsupported browser: '{self.browser_name}'")
            logger.error(f"Supported browsers: {', '.join(self.ALLOWED_BROWSERS)}")
            raise ValueError(
                f"Unsupported browser: '{self.browser_name}'. "
                f"Allowed values: {', '.join(self.ALLOWED_BROWSERS)}"
            )

        # Set up download directory
        self.download_dir = os.path.abspath(
            self.config.get("download_directory", "./downloads")
        )
        os.makedirs(self.download_dir, exist_ok=True)

        # Configuration
        self.timeout = self.config.get("timeout", 30)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.window_size = self.config.get("window_size", "1920,1080")

    def _setup_chrome_options(self):
        """
        Set up Chrome options.

        Returns:
            ChromeOptions: Configured Chrome options
        """
        options = ChromeOptions()

        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,  # Block images for faster loading
        }
        options.add_experimental_option("prefs", prefs)

        # Common arguments
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")

        # Exclude automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Headless mode configuration
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--window-size={self.window_size}")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--enable-logging")
            options.add_argument("--log-level=0")
            options.add_argument(
                "--enable-features=NetworkService,NetworkServiceInProcess"
            )

            # Create temporary user data directory for headless mode
            # self.temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
            # _temp_directories.append(self.temp_user_data_dir)
            # options.add_argument(f"--user-data-dir={self.temp_user_data_dir}")
            # options.add_argument("--no-first-run")
            # options.add_argument("--no-default-browser-check")

        return options

    def _setup_firefox_options(self):
        """
        Set up Firefox options.

        Returns:
            FirefoxOptions: Configured Firefox options
        """
        options = FirefoxOptions()

        # Download preferences
        file_type = self.config.get("file_type", "application/octet-stream")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", self.download_dir)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", file_type)
        options.set_preference("browser.download.useDownloadDir", True)

        # Disable notifications and popups
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("dom.popup_maximum", 0)

        # Performance optimizations
        options.set_preference("permissions.default.image", 2)  # Block images
        options.set_preference("javascript.enabled", False)  # Disable JavaScript
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)

        if self.headless:
            options.add_argument("--headless")
            options.add_argument(f"--width={self.window_size.split(',')[0]}")
            options.add_argument(f"--height={self.window_size.split(',')[1]}")

        return options

    def start_browser(self):
        """
        Initialize the WebDriver based on the specified browser with retry logic.

        Returns:
            WebDriver: Initialized WebDriver instance

        Raises:
            Exception: If browser fails to start after all retry attempts
        """
        for attempt in range(self.retry_attempts):
            try:
                logger.info(
                    f"Starting {self.browser_name} browser (attempt {attempt + 1}/{self.retry_attempts})"
                )

                if self.browser_name == "chrome":
                    options = self._setup_chrome_options()
                    service = ChromeService(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)

                elif self.browser_name == "firefox":
                    options = self._setup_firefox_options()
                    service = FirefoxService(GeckoDriverManager().install())
                    self.driver = webdriver.Firefox(service=service, options=options)

                # Configure timeouts
                self.driver.implicitly_wait(self.timeout)
                self.driver.set_page_load_timeout(self.timeout)
                self.driver.set_script_timeout(self.timeout)

                # Maximize window if not headless
                if not self.headless:
                    self.driver.maximize_window()
                else:
                    # Set window size for headless mode
                    width, height = self.window_size.split(",")
                    self.driver.set_window_size(int(width), int(height))

                logger.info(f"Browser {self.browser_name} started successfully")
                return self.driver

            except Exception as e:
                logger.error(f"Failed to start browser (attempt {attempt + 1}): {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception as e:
                        pass
                    self.driver = None

                if attempt < self.retry_attempts - 1:
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error(
                        f"Failed to start browser after {self.retry_attempts} attempts"
                    )
                    raise Exception(f"Could not start {self.browser_name} browser: {e}")

    def quit_browser(self):
        """
        Close the WebDriver instance if it exists and clean up resources.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info(f"Browser {self.browser_name} closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None

        # Clean up temporary user data directory
        if self.temp_user_data_dir and os.path.exists(self.temp_user_data_dir):
            try:
                shutil.rmtree(self.temp_user_data_dir)
                logger.info(
                    f"Cleaned up temporary directory: {self.temp_user_data_dir}"
                )
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")
            finally:
                self.temp_user_data_dir = None

    def is_browser_running(self):
        """
        Check if browser is currently running.

        Returns:
            bool: True if browser is running, False otherwise
        """
        if not self.driver:
            return False

        try:
            # Try to get current URL to check if browser is responsive
            self.driver.current_url
            return True
        except Exception as e:
            return False

    def restart_browser(self):
        """
        Restart the browser instance.

        Returns:
            WebDriver: New WebDriver instance
        """
        logger.info("Restarting browser")
        self.quit_browser()
        return self.start_browser()

    def get_browser_info(self):
        """
        Get information about the current browser instance.

        Returns:
            dict: Browser information dictionary
        """
        if not self.driver:
            return {"status": "not_running"}

        try:
            return {
                "browser_name": self.browser_name,
                "version": self.driver.capabilities.get("browserVersion", "unknown"),
                "driver_version": self.driver.capabilities.get("chrome", {}).get(
                    "chromedriverVersion", "unknown"
                ),
                "platform": self.driver.capabilities.get("platformName", "unknown"),
                "headless": self.headless,
                "current_url": self.driver.current_url,
                "window_size": self.driver.get_window_size(),
                "status": "running",
            }
        except Exception as e:
            logger.error(f"Error getting browser info: {e}")
            return {"status": "error", "error": str(e)}

    def __del__(self):
        """Destructor to ensure browser is closed."""
        self.quit_browser()
