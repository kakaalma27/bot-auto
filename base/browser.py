from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Browser:
    def __init__(self, browser_instance=None, proxy=None,  extension=None):
        if browser_instance:
            self.browser = browser_instance  # Use the provided browser instance
        else:
            self.browser = self._initialize_driver(proxy, extension)

    def _initialize_driver(self, proxy=None,  extension=None):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=old')
        options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--no-zygote")
        options.add_argument("--noerrdialogs")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy settings if provided
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Add extension if provided
        if extension:
            options.add_extension(extension)
        
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()  # Explicitly set the window size
        return driver
    
    def open_url(self, url):
        self.browser.get(url)

    def close(self):
        self.browser.quit()
