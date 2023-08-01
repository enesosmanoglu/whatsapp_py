import os
import threading
from typing import Any, Callable, Self

#region Selenium
from selenium.webdriver import Chrome, Edge, Firefox, Safari
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver
#endregion

from .event_listener import EventListener

WINDOW_CLOSED_MESSAGE_PREFIX = 'Unable to evaluate script: no such window: target window already closed'

class WebDriver:
    """WebDriver types."""
    # TODO: Convert to Enum
    Chrome = Chrome
    Edge = Edge
    Firefox = Firefox
    Safari = Safari

class Browser:
    """Contains the information about a browser.

    Args:
        WebDriver (WebDriver): The WebDriver to be used.
        headless (bool): Whether to run the browser in headless mode.
        user_data_dir (str): The path to the user data directory.
        starting_url (str): The URL to be opened when the browser is started.
        debug (bool): Whether to run the browser in debug mode.
    """
    __screenshot_path: str = 'screenshot.png'
    """The path to the screenshot file."""

    _driver: Chrome = None
    """The WebDriver instance."""
    
    def __init__(self, 
            WebDriver:type[Chrome] = Chrome, 
            headless:bool = True, 
            user_data_dir:str = None,
            starting_url:str = None,
            debug:bool = False,
        ) -> None:
        self.__WebDriver = WebDriver
        self.__headless = headless
        self.__user_data_dir = user_data_dir
        self.__starting_url = starting_url
        self.__debug = debug

        self.__webdriver_options:ChromeOptions = None
        self.__webdriver_options_init()
        self.__create_driver()

    def __webdriver_options_init(self):
        """Initializes the WebDriver options."""
        if self.__WebDriver is Chrome:
            self.__webdriver_options = ChromeOptions()
        elif self.__WebDriver is Edge:
            self.__webdriver_options = EdgeOptions()
        elif self.__WebDriver is Firefox:
            self.__webdriver_options = FirefoxOptions()
        elif self.__WebDriver is Safari:
            self.__webdriver_options = SafariOptions()
        else:
            raise Exception('Invalid WebDriver')
        
        if self.__user_data_dir is not None:
            if not os.path.isabs(self.__user_data_dir):
                self.__user_data_dir = os.path.join(os.getcwd(), self.__user_data_dir)
            
            self.__webdriver_options.add_argument(f'--user-data-dir={self.__user_data_dir}')
        
        if self.__headless:
            self.__webdriver_options.add_argument('--headless=new')
            self.__webdriver_options.add_argument('window-size=1920,1080')
        else:
            self.__webdriver_options.add_argument('window-size=1500,900')
                
        self.__webdriver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.__webdriver_options.add_experimental_option('prefs', {'profile.exit_type': 'Normal', 'profile.default_content_setting_values.notifications': 1})
        self.__webdriver_options.add_argument("--enable-features=WebNotifications")
        self.__webdriver_options.add_argument("--disable-popup-blocking")
        self.__webdriver_options.add_argument("--disable-infobars")
        self.__webdriver_options.add_argument("--disable-extensions")


    def __create_driver(self):
        """Creates the WebDriver instance."""
        self._driver = EventFiringWebDriver(self.__WebDriver(options=self.__webdriver_options), EventListener())
        if self.__starting_url:
            self._driver.get(self.__starting_url)

        
    def set_network_conditions(self, offline:bool = False, latency:int = 5, throughput:int = 500 * 1024, download_throughput:int = None, upload_throughput:int = None) -> Self:
        """Sets the network conditions.

        Args:
            offline (bool, optional): Whether the browser should be offline. Defaults to False.
            latency (int, optional): The latency in milliseconds. Defaults to 5.
            throughput (int, optional): The throughput in bytes per second. Defaults to 500 * 1024.
            download_throughput (int, optional): The download throughput in bytes per second. Defaults to None.
            upload_throughput (int, optional): The upload throughput in bytes per second. Defaults to None.
        
        Info:
            The `throughput` parameter is a shorthand for setting both the download and upload throughput values.
            
        Returns:
            browser (Browser): The current browser instance.
        """
        if throughput is not None:
            if download_throughput is None:
                download_throughput = throughput
            if upload_throughput is None:
                upload_throughput = throughput
        
        self._driver.set_network_conditions(
            offline=offline,  # True|False
            latency=latency,  # additional latency (ms)
            download_throughput=download_throughput,  # maximal throughput
            upload_throughput=upload_throughput,  # maximal throughput
        )
        return self

    def __screenshot_loop(self):
        """The screenshot loop."""
        self.screenshot()
        if self.__screenshot_interval > 0.0:
            self.__screenshot_timer = threading.Timer(self.__screenshot_interval, self.__screenshot_loop)
            self.__screenshot_timer.start()

    def start_screenshot_loop(self, interval:float = 0.5) -> Self:
        """Starts the screenshot loop.

        Args:
            interval (float, optional): The interval in seconds. Defaults to 0.5.
        
        Returns:
            browser (Browser): The current browser instance.
        """
        self.__screenshot_interval = interval
        self.__screenshot_timer = threading.Timer(self.__screenshot_interval, self.__screenshot_loop)
        self.__screenshot_timer.start()
        return self
    
    def stop_screenshot_loop(self) -> Self:
        """Stops the screenshot loop.
        
        Returns:
            browser (Browser): The current browser instance.
        """
        self.__screenshot_interval = 0.0
        self.__screenshot_timer.cancel()
        return self
    
    def screenshot(self, path:str = None) -> bool:
        """Takes a screenshot.

        Args:
            path (str, optional): The path to the screenshot file. Defaults to [`__screenshot_path`](./#__screenshot_path).

        Returns:
            bool: True if the screenshot was taken successfully, False otherwise.
        """
        if path is None:
            path = self.__screenshot_path
        if os.path.dirname(path) != '' and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            return self._driver.get_screenshot_as_file(path)
        except:
            return False

    def load_url(self, url:str) -> bool:
        """Loads the specified URL.

        Args:
            url (str): The URL to load.

        Returns:
            bool: True if the URL was loaded successfully, False otherwise.
        """
        try:
            self._driver.get(url)
            return True
        except:
            return False

    def stop(self) -> bool:
        """Stops the browser.

        Returns:
            bool: True if the browser was stopped successfully, False otherwise.
        """
        try:
            self._driver.quit()
            return True
        except:
            return False

    def wait_until(self, method: Callable, timeout:int = 10) -> Any: 
        """Waits until the specified method returns a truthy value.

        Args:
            method (Callable: The method to wait for.
            timeout (int, optional): The timeout in seconds. Defaults to 10.

        Returns:
            result (Any): The result of the method.
        
        Raises:
            TimeoutException: If the method did not return a truthy value within the specified timeout.
        """
        return WebDriverWait(self._driver, timeout).until(lambda _: method())
    
    def wait_until_not(self, method: Callable, timeout:int = 10) -> Any:
        """Waits until the specified method returns a falsy value.

        Args:
            method (Callable: The method to wait for.
            timeout (int, optional): The timeout in seconds. Defaults to 10.

        Returns:
            result (Any): The result of the method.
        
        Raises:
            TimeoutException: If the method did not return a falsy value within the specified timeout.
        """
        return WebDriverWait(self._driver, timeout).until_not(lambda _: method())

    def find_element(self, css: str, parent:WebElement|Chrome=None) -> WebElement | None:
        """Finds the first element matching the specified CSS selector.

        Args:
            css (str): The CSS selector.
            parent (WebElement|Chrome, optional): The parent element. Defaults to `_driver`.

        Returns:
            element (WebElement|None): The element if found, None otherwise.
        """
        if parent is None:
            parent = self._driver
        try:
            return parent.find_element(By.CSS_SELECTOR, css) # type: ignore
        except:
            return None
    
    def find_elements(self, css: str, parent:WebElement|Chrome=None) -> list[WebElement]:
        """Finds all elements matching the specified CSS selector.

        Args:
            css (str): The CSS selector.
            parent (WebElement|Chrome, optional): The parent element. Defaults to `_driver`.

        Returns:
            elements (list[WebElement]): The elements if found, an empty list otherwise.
        """
        if parent is None:
            parent = self._driver
        try:
            return parent.find_elements(By.CSS_SELECTOR, css)
        except:
            return []
    
    def has_element(self, css: str) -> bool:
        """Checks if an element matching the specified CSS selector exists.

        Args:
            css (str): The CSS selector.

        Returns:
            has_element (bool): True if an element matching the specified CSS selector exists, False otherwise.
        """
        return self.find_element(css) is not None

    def execute_script(self, script: str, *args:Any) -> Any:
        """Executes the specified JavaScript code.

        Args:
            script (str): The JavaScript code.
            args (Any): The arguments to pass to the JavaScript code.

        Returns:
            result (Any): The result of the JavaScript code.
        """
        return self._driver.execute_script(script, *args)


    @property
    def is_running(self) -> bool:
        try:
            self._driver.title
            return True
        except:
            return False

    @property
    def is_closed(self) -> bool:
        logs = self._driver.get_log('driver')
        log_count = len(logs)
        if log_count > 0:
            if WINDOW_CLOSED_MESSAGE_PREFIX in logs[-1]['message']:
                return True
        return False

    @property
    def current_url(self) -> str:
        try:
            return self._driver.current_url
        except:
            return ''

    @property
    def notifications(self):
        return self._driver.execute_script('return window.notifications;') or []
    
    def get_notification(self):
        return self._driver.execute_script(f'return window.notifications?.shift();')