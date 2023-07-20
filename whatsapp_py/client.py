import os
import time
import threading
from typing import Callable

import qrcode

from .event_emitter import EventEmitter
from .const import *
from .helpers import *
from .css import CSS
from .chat import Chat
from .browser import Browser, WebDriver
from .browser import WebElement
from .check import Check
from .task import TaskManager
from .client_events import ClientEvents
from .message_notification import MessageNotification

class Client(EventEmitter):
    """The main class of the library. It handles the browser and the events.

    Args:
        WebDriver (WebDriver): The webdriver to use. Can be Client.Chrome, Client.Edge, Client.Firefox or Client.Safari (default: Client.Chrome)
        headless (bool): Whether to run the browser in headless mode or not (default: True)
        user_data_dir (str): The path to the user data directory (default: 'user_data')
        debug (bool): Whether to print debug messages or not (default: False)
        print_qr_code (bool): Whether to print the QR code to the console or not (default: True)

    Raises:
        Exception: If the webdriver is not supported
    """

    Chrome = WebDriver.Chrome
    """The Chrome webdriver"""
    Edge = WebDriver.Edge
    """The Edge webdriver"""
    Firefox = WebDriver.Firefox
    """The Firefox webdriver"""
    Safari = WebDriver.Safari
    """The Safari webdriver"""

    __update_loop_timer: threading.Timer = None
    """The timer for the update loop"""
    __is_looping: bool = False
    """Whether the update loop is running or not"""
    __last_loading_progress_percent: float = None
    """The last WhatsApp loading progress percent"""
    __qr_content: str = None
    """QR code content that was set by the `qr_content` property"""
    __last_qr_content: str = None
    """The last QR code content that was set by the `qr_content` property"""
    __error_count: int = 0
    """The number of errors that occurred (used for the debug)"""
    __debug_enabled: bool = False
    """Whether to print debug messages or not"""

    browser: Browser = None
    """The browser"""
    task_manager: TaskManager = None
    """The manager of the tasks"""

    def __init__(self, 
            WebDriver:Chrome = Chrome, 
            headless:bool = True, 
            user_data_dir:str = 'user_data', 
            debug=False,
            print_qr_code = True, 
        ) -> None:
        self.__WebDriver = WebDriver
        self.__headless = headless
        self.__user_data_dir = user_data_dir
        self.__debug_enabled = debug
        self.__should_qr_code_printed = print_qr_code

        self.__error_count = len([entry for entry in os.listdir('debug/') if os.path.isfile(os.path.join('debug/', entry))]) if os.path.exists('debug/') else 0

        self.task_manager = TaskManager()
        self.start()

    def debug_info(self, *args, **kwargs):
        """Prints an info to the console if the debug is enabled
        
        Parameters:
            *args (Any): The arguments to print
            **kwargs (Any): The keyword arguments to print
        """
        if self.__debug_enabled:
            print('\t[INFO]', *args, **kwargs)
    
    def debug_error(self, *args, **kwargs):
        """Emits the `ClientEvents.ERROR` event

        If the [`__debug_enabled`](./#client.Client.__debug_enabled) is `True`:
        
        * Prints an error message to the console
        * Takes a screenshot of the browser window and saves it to the debug folder
        
        Parameters:
            *args (Any): The arguments to print
            **kwargs (Any): The keyword arguments to print
        """
        self.emit(ClientEvents.ERROR, *args, **kwargs)

        if self.__debug_enabled:
            print(f'\t[ERROR-{self.__error_count}]', *args, **kwargs)
            self.browser.screenshot(f'debug/error{self.__error_count}.png')
            self.__error_count += 1
    
    def __create_browser(self):
        """Creates the browser and emits the `ClientEvents.BROWSER_CREATED` event"""
        self.browser = Browser(WebDriver=self.__WebDriver, headless=self.__headless, user_data_dir=self.__user_data_dir, debug=self.__debug_enabled, starting_url=WHATSAPP_URL)
        self.emit(ClientEvents.BROWSER_CREATED, self.browser)

    def __check_function_decorator(type: str) -> Callable:
        """A decorator for the check functions
        
        Args:
            type (str): The type of the check function
        
        Returns:
            decorator (Callable): The decorator
        """
        def decorator(func: Callable):
            def wrapper(self, first_time=False, *args, **kwargs):
                if first_time:
                    if type not in Check.true_once:
                        val = func(self, *args, **kwargs)
                        if val:
                            Check.true_once.append(type)
                        return val
                    else:
                        return False
                else:
                    return func(self, *args, **kwargs)
            Check.funcs[type] = wrapper
            return wrapper
        return decorator

    def is_true(self, type: str, first_time=False) -> bool:
        """Checks if a condition is true

        Args:
            type (str): The type of the check function
            first_time (bool, optional): Whether to check if the condition is true for the first time or not. Defaults to False.
        
        Returns:
            is_true (bool): Whether the condition is true or not
        """
        if type in Check.funcs:
            return Check.funcs[type](self, first_time=first_time)
        else:
            self.debug_error(f'Check type "{type}" not implemented')
            return False
    
    def is_true_first_time(self, type: str) -> bool:
        """Checks if a condition is true **for the first time**

        * It is the same as calling `is_true(type, first_time=True)`

        Args:
            type (str): The type of the check function

        Returns:
            is_true_first_time (bool): Whether the condition is true or not
        """
        return self.is_true(type, first_time=True)

    def __start(self) -> None:
        """
        * Creates the browser
        * Emits the `ClientEvents.START` event
        * Starts the update loop timer (calls `__update`)
        """
        self.debug_info('__start()')
        self.__create_browser()
        # self.load_main_page()
        self.emit(ClientEvents.START)
        self.__is_looping = True
        self.__update_loop_timer = threading.Timer(LOOP_INTERVAL, self.__update)
        self.__update_loop_timer.start()

    def __update(self) -> None:
        """
        * Stops if the browser window is closed
        * Stops if the client is not looping (`__is_looping` is `False`)
        * Emits the `ClientEvents.UPDATE` event
        * Starts the update loop timer (calls `__update`)
        """
        if self.browser.is_closed:
            self.debug_info('Browser window closed by user')
            self.stop()
            return

        if not self.__is_looping:
            return

        # Start the update loop timer for the endless loop
        # With threads, it can be run endless without the recursion limit (1000)
        self.__update_loop_timer = threading.Timer(LOOP_INTERVAL, self.__update)
        self.__update_loop_timer.start()

        self.emit(ClientEvents.UPDATE)

        # Check for the new notifications
        notifications = self.browser.notifications
        if len(notifications) > 0:
            # get_notification() reduces the notifications list by one
            # so the length of the notifications can be used to check if there are any new notifications
            raw_notification = self.browser.get_notification()
            # WhatsApp sends the notifications in the format of
            #   `<phone_number>@c.us` on `tag`
            #   `<message_body>` on `body`
            phone_number = raw_notification['tag'].split('@')[0]
            body = raw_notification['body']
            notification = MessageNotification(phone_number, body)

            self.debug_info('New notification:', notification)
            self.emit(ClientEvents.NOTIFICATION, notification)

        # Check for the loading screen
        if self.is_true(Check.LOADING_SCREEN):
            # If the loading screen is detected, do not continue
            if self.__last_loading_progress_percent != self.loading_percent:
                self.__last_loading_progress_percent = self.loading_percent
                self.debug_info(f'Loading {int(self.loading_percent)}%')
            return
        
        # Check if the login screen is detected for the first time
        if self.is_true_first_time(Check.LOGIN_SCREEN):
            self.debug_info('Login screen detected')
            # Start the login wait thread
            self.__login_wait_thread = threading.Thread(target=self.wait_for_login)
            self.__login_wait_thread.start()
            return
        
        if self.is_true_first_time(Check.QR_READY):
            self.emit(ClientEvents.QR_CODE, self.qr_content)
            if self.__should_qr_code_printed:
                self.print_qr_code()
        
        if self.is_true_first_time(Check.QR_REFRESH):
            self.refresh_qr_code()

        if self.is_true_first_time(Check.LOGGED_IN):
            self.debug_info('Logged in')
            self.emit(ClientEvents.LOGGED_IN)
            return

        if self.is_true(Check.LOGGED_IN):
            self.__check_tasks()
            return

    def __check_tasks(self):
        """Checks if there is a task to do and starts it if there is"""
        task = self.task_manager.get_task()
        if task is not None:
            # There is a task to do
            if not task.is_done:
                # Task is not done yet
                if not task.in_progress:
                    # Task is not in progress. Start it
                    self.debug_info(f'Starting task {task}')
                    task.start()
   
    def start(self) -> None:
        """Starts the client in a new thread (calls `__start`)"""
        threading.Thread(target=self.__start).start()
         
    def stop(self) -> None:
        """Stops the client"""
        self.__is_looping = False

        try:
            self.__update_loop_timer.cancel()
        except Exception as e:
            self.debug_info(f'Error while stopping timer: {e}')

        try:
            self.browser.stop()
        except Exception as e:
            self.debug_info(f'Error while closing browser: {e}')
        
        self.emit(ClientEvents.STOP)

    def load_main_page(self) -> None:
        """Loads the WhatsApp Web main page"""
        Check.remove_first_check(Check.MAIN_SCREEN)
        self.browser.load_url(WHATSAPP_URL)
    
    def load_chat_page(self, chat:Chat) -> None:
        """Loads the chat page of the given chat

        Args:
            chat (Chat): The chat to load
        """
        self.browser.load_url(f"{WHATSAPP_PHONE_URL}{chat.phone_number}")

    @property
    def qr_content(self) -> str:
        """Fetches the qr code from the browser and returns it

        * If the qr code is not ready, returns `None`
        * If the qr code is ready but not refreshed, refreshes and returns it

        Returns:
            qr_content (str): The content of the QR code
        """
        if not self.is_qr_ready:
            return None

        if self.need_qr_refresh:
            self.refresh_qr_code()

        el_qr_content = self.browser.find_element(CSS.QR_CODE)
        if el_qr_content is None:
            return None

        self.__qr_content = el_qr_content.get_attribute('data-ref')

        if self.__last_qr_content != self.__qr_content:
            self.debug_info('QR code updated.')
            self.__last_qr_content = self.__qr_content

        return self.__qr_content

    def refresh_qr_code(self) -> None:
        """Refreshes the QR code if it is needed

        * WhatsApp Web wants the QR code to be refreshed manually sometimes
        """
        if not self.need_qr_refresh:
            return None
        
        el_qr_refresh = self.browser.find_element(CSS.QR_REFRESH)
        if el_qr_refresh is None:
            return None

        self.debug_info('Refreshing QR code...')
        el_qr_refresh.click()
        time.sleep(LOOP_INTERVAL)
        Check.remove_first_check(Check.QR_REFRESH)
        Check.remove_first_check(Check.QR_READY)


    @property
    @__check_function_decorator(Check.WHATSAPP_URL)
    def is_whatsapp_url(self) -> bool:
        """Checks if the current url is the WhatsApp Web url
        
        Returns:
            is_whatsapp_url (bool): True if the current url is the WhatsApp Web url, False otherwise
        """
        return self.browser.current_url.startswith(WHATSAPP_URL)
    
    @property
    @__check_function_decorator(Check.WHATSAPP_READY)
    def is_whatsapp_ready(self) -> bool:
        """Checks if the WhatsApp Web is ready
        
        Returns:
            is_whatsapp_ready (bool): True if the WhatsApp Web is ready, False otherwise
        """
        return self.is_whatsapp_url and self.browser.has_element(CSS.APP)

    @property
    @__check_function_decorator(Check.CONFIRM_POPUP)
    def has_confirm_popup(self) -> bool:
        """Checks if the confirm popup is visible

        * Popups are shown while a chat is being loaded
        
        Returns:
            has_confirm_popup (bool): True if the confirm popup is visible, False otherwise
        """
        return self.is_whatsapp_ready and self.browser.has_element(CSS.CONFIRM_POPUP)
    
    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_OK)
    def has_confirm_popup_ok(self) -> bool:
        """Checks if the confirm popup has the OK button

        * If the chat has invalid phone number, the confirm popup has the OK button
        
        Returns:
            has_confirm_popup_ok (bool): True if the confirm popup has the OK button, False otherwise
        """
        return self.has_confirm_popup and self.browser.has_element(CSS.CONFIRM_POPUP_OK)
    
    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_CANCEL)
    def has_confirm_popup_cancel(self) -> bool:
        """Checks if the confirm popup has the Cancel button

        * While the chat is being loaded, the confirm popup has the Cancel button

        Returns:
            has_confirm_popup_cancel (bool): True if the confirm popup has the Cancel button, False otherwise
        """
        return self.has_confirm_popup and self.browser.has_element(CSS.CONFIRM_POPUP_CANCEL)

    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_BUTTON)
    def has_confirm_popup_button(self) -> bool:
        """Checks if the confirm popup has any button

        Returns:
            has_confirm_popup_button (bool): True if the confirm popup has any button, False otherwise
        """
        return self.has_confirm_popup_cancel or self.has_confirm_popup_ok
    
    @property
    @__check_function_decorator(Check.LOADING_SCREEN)
    def is_loading_screen(self) -> bool:
        """Checks if the loading screen is visible
        
        Returns:
            is_loading_screen (bool): True if the loading screen is visible, False otherwise
        """
        return self.is_whatsapp_ready and self.browser.has_element(CSS.LOADING_SCREEN)

    @property
    @__check_function_decorator(Check.LOGIN_SCREEN)
    def is_login_screen(self) -> bool:
        """Checks if the login screen is visible

        Returns:
            is_login_screen (bool): True if the login screen is visible, False otherwise
        """
        return self.is_whatsapp_ready and self.browser.has_element(CSS.LINK_WITH_PHONE)

    @property
    @__check_function_decorator(Check.QR_READY)
    def is_qr_ready(self) -> bool:
        """Checks if the QR code is ready

        * QR code is ready when the login screen is visible and the QR code is visible
        * It takes some time for the QR code to be ready after the login screen is visible
        
        Returns:
            is_qr_ready (bool): True if the QR code is ready, False otherwise
        """
        return self.is_login_screen and self.browser.has_element(CSS.QR_CODE)
    
    @property
    @__check_function_decorator(Check.QR_REFRESH)
    def need_qr_refresh(self) -> bool:
        """Checks if the QR code needs to be refreshed

        * WhatsApp Web wants the QR code to be refreshed manually sometimes
        * QR code needs to be refreshed when the QR refresh button is visible

        Returns:
            need_qr_refresh (bool): True if the QR code needs to be refreshed, False otherwise
        """
        return self.is_qr_ready and self.browser.has_element(CSS.QR_REFRESH)

    @property
    @__check_function_decorator(Check.LOGGED_IN)
    def is_logged_in(self) -> bool:
        """Checks if the user is logged in

        * User is logged in when the main screen or the chat screen is visible
        * Middle drawer is visible in both the main screen and the chat screen
        
        Returns:
            is_logged_in (bool): True if the user is logged in, False otherwise
        """
        return self.is_whatsapp_ready and self.browser.has_element(CSS.MIDDLE_DRAWER)
    
    @property
    @__check_function_decorator(Check.MAIN_SCREEN)
    def is_main_screen(self) -> bool:
        """Checks if the main screen is visible

        * Main screen is visible when the user is logged in and the intro title is visible

        Returns:
            is_main_screen (bool): True if the main screen is visible, False otherwise
        """
        return self.is_logged_in and self.browser.has_element(CSS.INTRO_TITLE)
    
    @property
    @__check_function_decorator(Check.CHAT_SCREEN)
    def is_chat_screen(self) -> bool:
        """Checks if the chat screen is visible

        * Chat screen is visible when the user is logged in and the conversation panel is visible
        
        Returns:
            is_chat_screen (bool): True if the chat screen is visible, False otherwise
        """
        return self.is_logged_in and self.browser.has_element(CSS.CONVERSATION_PANEL)
    


    @property
    def loading_percent(self) -> float:
        """Fetches the loading percent of the loading screen

        * Returns `0.0` when the loading screen is not shown

        Returns:
            loading_percent (float): Loading percent of the loading screen
        """
        if not self.is_loading_screen:
            return 0.0
        try:
            el = self.browser.find_element(CSS.LOADING_PROGRESS)
            value = el.get_attribute('value')
            max = el.get_attribute('max')
            if value is not None and max is not None:
                if max == '0':
                    return 0.0
                return (float(value) / float(max)) * 100
        except:
            pass
        return 0.0

    @property
    def confirm_popup_content(self) -> str:
        """Fetches the content of the confirm popup

        * Returns empty string when the confirm popup is not shown

        Returns:
            confirm_popup_content (str): Content of the confirm popup
        """
        if not self.has_confirm_popup:
            return ''
        el = self.browser.find_element(CSS.CONFIRM_POPUP_CONTENTS)
        if el is not None:
            return el.text
        return ''

    @property
    def chat_title(self) -> str:
        """Fetches the title of the chat

        * Returns empty string when the chat screen is not shown

        Returns:
            chat_title (str): Title of the chat
        """
        el = self.browser.find_element(CSS.CHAT_TITLE)
        if el is not None:
            return el.text
        return ''
    
    @property
    def is_chat_info_open(self) -> bool:
        """Checks if the chat info drawer is open

        * Returns `False` when the chat screen is not shown

        Returns:
            is_chat_info_open (bool): True if the chat info drawer is open, False otherwise
        """
        if not self.is_chat_screen:
            return False
        if not self.browser.has_element(CSS.CHAT_INFO_DRAWER):
            return False
        el = self.browser.find_element(CSS.CHAT_INFO_TITLE)
        if el is None:
            return False
        return el.text == self.chat_title
    
    @property
    def last_sent_message_data(self) -> str:
        """Fetches the `data-testid` attribute of the last sent message
        * Returns empty string if there is no last sent message

        Returns:
            last_sent_message_data (str): `data-testid` attribute of the last sent message
        """
        return self.browser.execute_script('return Array.from(document.querySelectorAll("[data-testid^=conv-msg-true_]")).reverse()[0]?.getAttribute("data-testid");') or ''

    def get_message_from_data(self, data: str) -> WebElement|None:
        """Fetches the message element from the `data-testid` attribute

        * Returns `None` if the message element is not found

        Args:
            data (str): `data-testid` attribute of the message

        Returns:
            web_element (WebElement | None): Message element if found, None otherwise
        """
        return self.browser.execute_script(f'return document.querySelector("[data-testid=\'{data}\']");') or None

    def confirm_popup(self) -> None:
        """Confirms the confirm popup

        * Does nothing if the confirm popup is not shown
        """
        if not self.has_confirm_popup:
            return None

        try:
            self.browser.wait_until(lambda: self.has_confirm_popup_ok)
        except:
            self.debug_error('Invalid popup.')
            return None
 
        self.debug_info('Confirming popup...')
        ok = self.browser.find_element(CSS.CONFIRM_POPUP_OK)
        ok.click()
        time.sleep(LOOP_INTERVAL)
        return None

    def wait_for_login(self) -> None:
        """Waits for the user to login

        * Does nothing if the user is already logged in
        * Removes the check for login screen when the user is logged in
        """
        self.debug_info('Waiting for login...')
        while not self.is_logged_in:
            time.sleep(LOOP_INTERVAL)
        self.debug_info('Logged in.')
        # remove check for login screen
        Check.remove_first_check(Check.LOGIN_SCREEN)


    def is_chat_open(self, phone_number: str) -> bool:
        """Checks if the chat is open for the given phone number

        Args:
            phone_number (str): Phone number of the chat

        Returns:
            is_chat_open (bool): True if the chat is open, False otherwise
        """
        if not self.is_chat_screen:
            self.debug_info('is_chat_open -> not self.is_chat_screen')
            return False

        try:
            phone_number = str(int(phone_number.replace(' ', '')))
        except:
            self.debug_info('is_chat_open -> invalid phone number')
            return False
        
        chat_title = self.chat_title
        try:
            chat_title = str(int(chat_title.replace(' ', '')))
        except:
            pass

        if chat_title == phone_number:
            self.debug_info('is_chat_open -> chat_title == phone_number')
            return True

        el_chat_title = self.browser.find_element(CSS.CHAT_TITLE)
        if el_chat_title is None:
            self.debug_info('is_chat_open -> el_chat_title is None')
            return False
        
        if not self.is_chat_info_open:
            self.debug_info('is_chat_open -> not self.is_chat_info_open')
            el_chat_title.click()

            # if retry_until_true(lambda: self.is_chat_info_open):
            #     self._print('is_chat_open -> not self.is_chat_info_open')
            #     return False
            try:
                self.browser.wait_until(lambda: self.is_chat_info_open)
            except:
                self.debug_info('is_chat_open -> not self.is_chat_info_open')
                return False

            # if retry_until_true(lambda: self.browser.find_element(CSS.CHAT_INFO_TITLE).text == chat_title):
            #     self._print('is_chat_open -> self.browser.find_element(CSS.CHAT_INFO_TITLE).text != chat_title')
            #     return False
            try:
                self.browser.wait_until(lambda: self.browser.find_element(CSS.CHAT_INFO_TITLE).text == chat_title)
            except:
                self.debug_info('is_chat_open -> self.browser.find_element(CSS.CHAT_INFO_TITLE).text != chat_title')
                return False

        el_chat_info_subtitle = self.browser.find_element(CSS.CHAT_INFO_SUBTITLE)
        if el_chat_info_subtitle is None:
            self.debug_info('is_chat_open -> el_chat_info_subtitle is None')
            return False

        chat_info_subtitle = el_chat_info_subtitle.text
        try:
            chat_info_subtitle = str(int(chat_info_subtitle.replace(' ', '')))
        except:
            pass

        # Close chat info
        # el_close = self.browser.find_element(CSS.CHAT_INFO_CLOSE)
        # el_close.click()
        # time.sleep(0.1)

        if chat_info_subtitle == phone_number:
            self.debug_info('is_chat_open -> chat_info_subtitle == phone_number')
            self.browser.execute_script('if (arguments[0]) arguments[0].innerText = arguments[1];', el_chat_title, chat_info_subtitle)
            return True

        self.debug_info('is_chat_open -> False')
        return False


    def print_qr_code(self, invert=False, tty=False):
        """Prints the QR Code in the terminal

        Args:
            invert (bool, optional): invert the ASCII characters (solid <-> transparent) Defaults to False.
            tty (bool, optional): use fixed TTY color codes (forces invert=True) Defaults to False.
        """
        self.debug_info(f'Printing QR Code...')
        qr = qrcode.QRCode()
        qr.add_data(self.qr_content)
        qr.print_ascii(invert=invert, tty=tty)
    
    def new_chat(self, phone_number: str) -> Chat:
        """Creates a new chat

        Args:
            phone_number (str): Phone number of the chat

        Returns:
            chat (Chat): Chat object
        """
        chat = Chat(client=self, phone_number=phone_number)

        try:
            int(phone_number.replace(' ', ''))
        except:
            # self._print_error('Invalid phone number.')
            chat.is_phone_number_invalid = True
            raise Exception(f"Invalid phone number.")

        return chat
