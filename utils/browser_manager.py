"""Module for managing Selenium WebDriver instances based on configuration."""

import yaml
import tempfile
import os
import shutil
import psutil
import time
import uuid
from pathlib import Path
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
        self.user_data_dir = None
        self.use_user_data_dir = config.get("use_user_data_dir", True)

        # Always disable user data dir in CI environments or when running tests
        if (
            os.environ.get("CI") == "true"
            or os.environ.get("GITHUB_ACTIONS") == "true"
            or "pytest" in os.environ.get("_", "")
        ):
            self.use_user_data_dir = False
            logger.info("Detected CI environment or pytest - disabling user data dir")

        logger.info(f"use_user_data_dir = {self.use_user_data_dir}")

        if self.browser_name not in self.ALLOWED_BROWSERS:
            logger.warning(f"Unsupported browser: '{self.browser_name}'")
            logger.warning(
                f"Supported browsers are: {', '.join(self.ALLOWED_BROWSERS)}"
            )
            raise ValueError(
                f"Unsupported browser: '{self.browser_name}'. Allowed values: {', '.join(self.ALLOWED_BROWSERS)}"
            )

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _cleanup_chrome_processes(self):
        """Kill any existing Chrome/ChromeDriver processes."""
        processes_killed = 0
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] and any(
                    name in proc.info["name"].lower()
                    for name in ["chrome", "chromedriver"]
                ):
                    proc.kill()
                    processes_killed += 1
                    logger.info(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if processes_killed > 0:
            time.sleep(2)  # Give processes time to die
            logger.info(f"Killed {processes_killed} Chrome-related processes")

    def _cleanup_temp_directories(self):
        """Clean up any existing Chrome user data directories."""
        temp_patterns = [
            "/tmp/chrome_user_data_*",
            "/tmp/.org.chromium.*",
            "/tmp/scoped_dir*",
            os.path.expanduser("~/tmp/chrome_user_data_*"),
        ]

        cleaned = 0
        for pattern in temp_patterns:
            import glob

            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned += 1
                        logger.info(f"Cleaned temp directory: {path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {path}: {e}")

        if cleaned > 0:
            logger.info(f"Cleaned {cleaned} temporary directories")

    def _create_unique_user_data_dir(self):
        """Create a unique user data directory with proper permissions."""
        if not self.use_user_data_dir:
            return None

        # Use a more unique identifier
        unique_id = f"{uuid.uuid4().hex[:8]}_{os.getpid()}_{int(time.time())}"
        temp_base = os.environ.get("TMPDIR", "/tmp")
        user_data_dir = os.path.join(temp_base, f"chrome_user_data_{unique_id}")

        try:
            os.makedirs(user_data_dir, mode=0o755, exist_ok=False)
            logger.info(f"Created unique user data dir: {user_data_dir}")
            return user_data_dir
        except OSError as e:
            logger.warning(f"Failed to create user data dir {user_data_dir}: {e}")
            return None

    def _get_chrome_options(self):
        """Get Chrome options with proper configuration."""
        options = ChromeOptions()

        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "profile.default_content_settings.popups": 0,
            "directory_upgrade": True,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
        }
        options.add_experimental_option("prefs", prefs)

        # User data directory handling
        if self.use_user_data_dir:
            self.user_data_dir = self._create_unique_user_data_dir()
            if self.user_data_dir:
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
            else:
                logger.warning("Failed to create user data dir, proceeding without it")
                self.use_user_data_dir = False

        # Essential Chrome arguments to prevent conflicts
        essential_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-crash-reporter",
            "--disable-oopr-debug-crash-dump",
            "--no-crash-upload",
            "--disable-low-res-tiling",
            "--disable-popup-blocking",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-ipc-flooding-protection",
            "--single-process",  # This can help avoid some multi-process issues
            "--no-zygote",  # Disable zygote process
        ]

        for arg in essential_args:
            options.add_argument(arg)

        # Headless specific configuration
        if self.headless:
            headless_args = [
                "--headless=new",
                "--disable-setuid-sandbox",
                "--disable-software-rasterizer",
                "--disable-images",
                "--disable-javascript",
                "--window-size=1920,1080",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--enable-logging",
                "--log-level=0",
                "--enable-features=NetworkService,NetworkServiceInProcess",
            ]
            for arg in headless_args:
                options.add_argument(arg)

        # Experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def start_browser(self):
        """Initializes the WebDriver based on the specified browser with enhanced retry logic."""
        retries = config.get("retry_attempts", 3)

        # Pre-cleanup before starting
        self._cleanup_chrome_processes()
        self._cleanup_temp_directories()

        for attempt in range(retries):
            try:
                if self.browser_name == "chrome":
                    options = self._get_chrome_options()

                    # Additional cleanup between attempts
                    if attempt > 0:
                        time.sleep(2)
                        self._cleanup_chrome_processes()

                    self.driver = webdriver.Chrome(options=options)

                    # Configure timeouts
                    self.driver.implicitly_wait(config.get("implicit_wait", 10))
                    self.driver.set_page_load_timeout(
                        config.get("page_load_timeout", 60)
                    )
                    self.driver.set_script_timeout(30)

                    if not self.headless:
                        self.driver.maximize_window()

                elif self.browser_name == "firefox":
                    options = FirefoxOptions()
                    file_type = config.get("file_type", "application/octet-stream")

                    # Firefox preferences
                    firefox_prefs = {
                        "browser.download.folderList": 2,
                        "browser.download.dir": self.download_dir,
                        "browser.download.manager.showWhenStarting": False,
                        "browser.helperApps.neverAsk.saveToDisk": file_type,
                        "dom.webnotifications.enabled": False,
                        "dom.push.enabled": False,
                        "permissions.default.image": 2,
                        "javascript.enabled": False,
                    }

                    for pref, value in firefox_prefs.items():
                        options.set_preference(pref, value)

                    if self.headless:
                        options.add_argument("-headless")

                    self.driver = webdriver.Firefox(options=options)
                    self.driver.implicitly_wait(config.get("implicit_wait", 10))
                    self.driver.set_page_load_timeout(
                        config.get("page_load_timeout", 60)
                    )
                    self.driver.set_script_timeout(30)

                    if not self.headless:
                        self.driver.maximize_window()

                logger.info(
                    f"Browser {self.browser_name} started successfully on attempt {attempt + 1}"
                )
                return self.driver

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to start browser: {e}")

                # Cleanup after failed attempt
                if self.user_data_dir and os.path.exists(self.user_data_dir):
                    try:
                        shutil.rmtree(self.user_data_dir, ignore_errors=True)
                        logger.info(
                            f"Cleaned user data dir after failed attempt: {self.user_data_dir}"
                        )
                    except Exception as cleanup_error:
                        logger.warning(
                            f"Failed to clean user data dir: {cleanup_error}"
                        )
                    self.user_data_dir = None

                # Additional cleanup between attempts
                self._cleanup_chrome_processes()

                if attempt == retries - 1:
                    logger.error(f"Failed to start browser after {retries} attempts")
                    raise

                # Wait before retry
                time.sleep(2**attempt)  # Exponential backoff

        return None

    def quit_browser(self):
        """Closes the WebDriver instance and cleans up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser session ended successfully")
            except Exception as e:
                logger.warning(f"Error quitting browser: {e}")
            finally:
                self.driver = None

        # Give browser time to shut down properly
        time.sleep(1)

        # Clean up processes
        self._cleanup_chrome_processes()

        # Clean up user data directory
        if self.user_data_dir and os.path.exists(self.user_data_dir):
            try:
                shutil.rmtree(self.user_data_dir, ignore_errors=True)
                logger.info(f"Cleaned up user data directory: {self.user_data_dir}")
            except Exception as e:
                logger.warning(
                    f"Failed to clean up user data directory {self.user_data_dir}: {e}"
                )
            finally:
                self.user_data_dir = None
