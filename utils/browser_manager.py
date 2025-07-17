"""Module for managing Selenium WebDriver instances based on configuration."""
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os
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
            logger.warning(f"Supported browsers are: {', '.join(self.ALLOWED_BROWSERS)}")
            raise ValueError(
                f"Unsupported browser: '{self.browser_name}'. "
                f"Allowed values: {', '.join(self.ALLOWED_BROWSERS)}"
            )
            
        self.headless = config.get("headless", False)
        self.download_dir = os.path.abspath(
            config.get("download_directory", "./downloads")
        )
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        # os.makedirs(self.download_dir, exist_ok=True)

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
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)           
            options.add_argument("--disable-blink-features=AutomationControlled")
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()

        elif self.browser_name == "firefox":
            options = FirefoxOptions()
            file_type = config.get("file_type", "application/octet-stream")
            options.set_preference("browser.download.folderList", 2)
            # 0 = desktop, 1 = default location, 2 = desired location
            # https://www.sitepoint.com/mime-types-complete-list/
            options.set_preference("browser.download.dir", self.download_dir)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", file_type)
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)
            if self.headless:
                options.add_argument("-headless")
            self.driver = webdriver.Firefox(options=options)
            self.driver.maximize_window()

        # else:
        #     raise ValueError(f"Unsupported browser: {self.browser_name}")

        return self.driver

    def quit_browser(self):
        """Closes the WebDriver instance if it exists."""
        if self.driver:
            self.driver.quit()
            self.driver = None
