class BasePage:
    """Base page class for common page functionalities."""

    def __init__(self, driver):
        self.driver = driver

    def find_element(self, *args, **kwargs):
        """Find an element on the page."""
        return self.driver.find_element(*args, **kwargs)

    def click(self, *args, **kwargs):
        """Click an element on the page."""
        element = self.find_element(*args, **kwargs)
        element.click()

    def enter_text(self, text, *args, **kwargs):
        """Enter text into an input field."""
        element = self.find_element(*args, **kwargs)
        element.clear()
        element.send_keys(text)
