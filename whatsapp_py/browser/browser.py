import os
import threading
from typing import Any, Callable

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
    Chrome = Chrome
    Edge = Edge
    Firefox = Firefox
    Safari = Safari

class Browser:
    __screenshot_path: str = 'screenshot.png'

    _driver: Chrome = None
    
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
        self._driver = EventFiringWebDriver(self.__WebDriver(options=self.__webdriver_options), EventListener())
        if self.__starting_url:
            self._driver.get(self.__starting_url)

        
    def set_network_conditions(self, offline:bool = False, latency:int = 5, throughput:int = 500 * 1024, download_throughput:int = None, upload_throughput:int = None):
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

    def __screenshot_loop(self):
        self.screenshot()
        if self.__screenshot_interval > 0.0:
            self.__screenshot_timer = threading.Timer(self.__screenshot_interval, self.__screenshot_loop)
            self.__screenshot_timer.start()

    def start_screenshot_loop(self, interval:float = 0.5):
        self.__screenshot_interval = interval
        self.__screenshot_timer = threading.Timer(self.__screenshot_interval, self.__screenshot_loop)
        self.__screenshot_timer.start()
    
    def stop_screenshot_loop(self):
        self.__screenshot_interval = 0.0
        self.__screenshot_timer.cancel()
    
    def screenshot(self, path:str = None) -> bool:
        if path is None:
            path = self.__screenshot_path
        if os.path.dirname(path) != '' and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            return self._driver.get_screenshot_as_file(path)
        except:
            return False

    def load_url(self, url:str) -> bool:
        try:
            self._driver.get(url)
            return True
        except:
            return False

    def stop(self) -> bool:
        try:
            self._driver.quit()
            return True
        except:
            return False

    def wait(self, timeout: int) -> Callable[[], None]:
        return WebDriverWait(self._driver, timeout)

    def wait_until(self, method: Callable[[Chrome], Any], timeout:int = 10) -> Callable[[], None]: 
        return WebDriverWait(self._driver, timeout).until(lambda _: method())

    def find_element(self, css: str, parent:WebElement|Chrome=None) -> WebElement | None:
        if parent is None:
            parent = self._driver
        try:
            return parent.find_element(By.CSS_SELECTOR, css) # type: ignore
        except:
            return None
    
    def find_elements(self, css: str) -> list[WebElement]:
        try:
            return self._driver.find_elements(By.CSS_SELECTOR, css)
        except:
            return []
    
    def has_element(self, css: str) -> bool:
        return self.find_element(css) is not None

    def execute_script(self, script: str, *args:Any) -> Any:
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
        if len(self._driver.get_log('driver')) > 0:
            if WINDOW_CLOSED_MESSAGE_PREFIX in self._driver.get_log('driver')[-1]['message']:
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