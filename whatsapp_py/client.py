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
from .browser import Browser
from .browser import Chrome, Edge, Firefox, Safari
from .browser import WebElement
from .check import Check
from .task import TaskManager
from .client_events import ClientEvents
from .message_notification import MessageNotification

class Client(EventEmitter):
    Chrome = Chrome
    Edge = Edge
    Firefox = Firefox
    Safari = Safari

    __update_timer: threading.Timer = None
    __is_looping = False
    __is_qr_printed = False
    __qr_content: str = None
    __last_loading_progress: float = None
    __last_qr_content: str = None
    __error_count = len([entry for entry in os.listdir('debug/') if os.path.isfile(os.path.join('debug/', entry))]) if os.path.exists('debug/') else 0
    __debug = False

    def __init__(self, 
            WebDriver = Edge, 
            headless = True, 
            user_data_dir = None, 
            debug=False,
            print_qr = True, 
        ) -> None:
        self.__WebDriver = WebDriver
        self.__headless = headless
        self.__user_data_dir = user_data_dir
        self.__debug = debug
        self.__print_qr = print_qr
        self.task_manager = TaskManager()
        self.start()

    def _print(self, *args, **kwargs):
        if self.__debug:
            print('[DEBUG]', *args, **kwargs)
    
    def _print_error(self, *args, **kwargs):
        self.emit(ClientEvents.ERROR, *args, **kwargs)
        if not self.__debug:
            return
        self._print(f'[ERROR-{self.__error_count}]', *args, **kwargs)
        self.browser.screenshot(f'debug/error{self.__error_count}.png')
        self.__error_count += 1
    
    def __create_browser(self):
        self.browser = Browser(WebDriver=self.__WebDriver, headless=self.__headless, user_data_dir=self.__user_data_dir, debug=self.__debug, starting_url=WHATSAPP_URL)
        self.emit(ClientEvents.BROWSER_CREATED, self.browser)

    def __check_function_decorator(type: str) -> None:
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

    def is_true(self, type: str, first_time=False):
        if type in Check.funcs:
            return Check.funcs[type](self, first_time=first_time)
        else:
            self._print_error(f'Check type "{type}" not implemented')
            return False
    
    def is_true_first_time(self, type: str):
        return self.is_true(type, first_time=True)

    def __start(self) -> None:
        self._print('__start()')
        self.__create_browser()
        # self.load_main_page()
        self.emit(ClientEvents.START)
        self.__is_looping = True
        self.__update_timer = threading.Timer(LOOP_INTERVAL, self.__update)
        self.__update_timer.start()

    def __update(self) -> None:
        if self.browser.is_closed:
            self._print('Browser window closed by user')
            self.stop()
            return

        if not self.__is_looping:
            return

   
        self.__update_timer = threading.Timer(LOOP_INTERVAL, self.__update)
        self.__update_timer.start()
        self.emit(ClientEvents.UPDATE)

        notifications = self.browser.notifications
        if len(notifications) > 0:
            raw_notification = self.browser.get_notification()
            notification = MessageNotification(phone_number=raw_notification['tag'].split('@')[0], body=raw_notification['body'])
            self._print('New notification:', notification)
            self.emit(ClientEvents.NOTIFICATION, notification)

        if self.is_true(Check.LOADING_SCREEN):
            if self.__last_loading_progress != self.loading_percent:
                self.__last_loading_progress = self.loading_percent
                self._print(f'Loading {int(self.loading_percent)}%')
            return
        
        if self.is_true_first_time(Check.LOGIN_SCREEN):
            self._print('Login screen detected')
            self.__login_wait_thread = threading.Thread(target=self.wait_for_login)
            self.__login_wait_thread.start()
            return
        
        if self.is_true_first_time(Check.QR_READY):
            # if self.__print_qr and self.qr_content is not None and not self.__is_qr_printed:
            if self.__print_qr:
                self.print_qr_code()
        
        if self.is_true_first_time(Check.QR_REFRESH):
            self.refresh_qr_code()

        if self.is_true_first_time(Check.LOGGED_IN):
            self._print('Logged in')
            self.emit(ClientEvents.LOGGED_IN)
            return

        if self.is_true(Check.LOGGED_IN):
            self.__check_tasks()
            return

    def __check_tasks(self):
        task = self.task_manager.get_task()
        if task is not None:
            # There is a task to do
            if not task.is_done:
                # Task is not done yet
                if not task.in_progress:
                    # Task is not in progress. Start it
                    self._print(f'Starting task {task}')
                    task.start()
   
    def start(self) -> None:
        threading.Thread(target=self.__start).start()
         
    def stop(self) -> None:
        self.__is_looping = False

        try:
            self.__update_timer.cancel()
        except Exception as e:
            print(f'Error while stopping timer: {e}')

        try:
            self.browser.stop()
        except Exception as e:
            print(f'Error while closing browser: {e}')
        
        self.emit(ClientEvents.STOP)

    def load_main_page(self) -> None:
        Check.remove_first_check(Check.MAIN_SCREEN)
        self.browser.load_url(WHATSAPP_URL)
    
    def load_chat_page(self, chat:Chat) -> None:
        self.browser.load_url(f"{WHATSAPP_PHONE_URL}{chat.phone_number}")

    @property
    def qr_content(self) -> str:
        if not self.is_qr_ready:
            return None

        if self.need_qr_refresh:
            self.refresh_qr_code()

        el_qr_content = self.browser.find_element(CSS.QR_CODE)
        if el_qr_content is None:
            return None

        self.__qr_content = el_qr_content.get_attribute('data-ref')

        if self.__last_qr_content != self.__qr_content:
            self._print('QR code updated.')
            self.__is_qr_printed = False
            self.__last_qr_content = self.__qr_content

        return self.__qr_content

    def refresh_qr_code(self) -> None:
        if not self.need_qr_refresh:
            return None
        
        el_qr_refresh = self.browser.find_element(CSS.QR_REFRESH)
        if el_qr_refresh is None:
            return None

        self._print('Refreshing QR code...')
        el_qr_refresh.click()
        time.sleep(LOOP_INTERVAL)
        Check.remove_first_check(Check.QR_REFRESH)
        Check.remove_first_check(Check.QR_READY)
        # self.browser.wait(LOOP_INTERVAL)()


    @property
    @__check_function_decorator(Check.WHATSAPP_URL)
    def is_whatsapp_url(self) -> bool:
        return self.browser.current_url.startswith(WHATSAPP_URL)
    
    @property
    @__check_function_decorator(Check.WHATSAPP_READY)
    def is_whatsapp_ready(self) -> bool:
        return self.is_whatsapp_url and self.browser.has_element(CSS.APP)

    @property
    @__check_function_decorator(Check.CONFIRM_POPUP)
    def has_confirm_popup(self) -> bool:
        return self.is_whatsapp_ready and self.browser.has_element(CSS.CONFIRM_POPUP)
    
    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_OK)
    def has_confirm_popup_ok(self) -> bool:
        return self.has_confirm_popup and self.browser.has_element(CSS.CONFIRM_POPUP_OK)
    
    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_CANCEL)
    def has_confirm_popup_cancel(self) -> bool:
        return self.has_confirm_popup and self.browser.has_element(CSS.CONFIRM_POPUP_CANCEL)

    @property
    @__check_function_decorator(Check.CONFIRM_POPUP_BUTTON)
    def has_confirm_popup_button(self) -> bool:
        return self.has_confirm_popup_cancel or self.has_confirm_popup_ok
    
    @property
    @__check_function_decorator(Check.LOADING_SCREEN)
    def is_loading_screen(self) -> bool:
        return self.is_whatsapp_ready and self.browser.has_element(CSS.LOADING_SCREEN)

    @property
    @__check_function_decorator(Check.LOGIN_SCREEN)
    def is_login_screen(self) -> bool:
        return self.is_whatsapp_ready and self.browser.has_element(CSS.LINK_WITH_PHONE)

    @property
    @__check_function_decorator(Check.QR_READY)
    def is_qr_ready(self) -> bool:
        return self.is_login_screen and self.browser.has_element(CSS.QR_CODE)
    
    @property
    @__check_function_decorator(Check.QR_REFRESH)
    def need_qr_refresh(self) -> bool:
        return self.is_qr_ready and self.browser.has_element(CSS.QR_REFRESH)

    @property
    @__check_function_decorator(Check.LOGGED_IN)
    def is_logged_in(self) -> bool:
        return self.is_whatsapp_ready and self.browser.has_element(CSS.MIDDLE_DRAWER)
    
    @property
    @__check_function_decorator(Check.MAIN_SCREEN)
    def is_main_screen(self) -> bool:
        return self.is_logged_in and self.browser.has_element(CSS.INTRO_TITLE)
    
    @property
    @__check_function_decorator(Check.CHAT_SCREEN)
    def is_chat_screen(self) -> bool:
        return self.is_logged_in and self.browser.has_element(CSS.CONVERSATION_PANEL)
    


    @property
    def loading_percent(self) -> float:
        if not self.is_loading_screen:
            return 0
        try:
            el = self.browser.find_element(CSS.LOADING_PROGRESS)
            value = el.get_attribute('value')
            max = el.get_attribute('max')
            if value is not None and max is not None:
                if max == '0':
                    return 0
                return (float(value) / float(max)) * 100
        except:
            pass
        return 0

    @property
    def confirm_popup_content(self) -> str:
        if not self.has_confirm_popup:
            return ''
        el = self.browser.find_element(CSS.CONFIRM_POPUP_CONTENTS)
        if el is not None:
            return el.text
        return ''

    @property
    def chat_title(self) -> str:
        el = self.browser.find_element(CSS.CHAT_TITLE)
        if el is not None:
            return el.text
        return ''
    
    @property
    def is_chat_info_open(self) -> bool:
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
        return self.browser.execute_script('return Array.from(document.querySelectorAll("[data-testid^=conv-msg-true_]")).reverse()[0]?.getAttribute("data-testid");')

    def get_message_from_data(self, data: str) -> WebElement:
        return self.browser.execute_script(f'return document.querySelector("[data-testid=\'{data}\']");')

    def confirm_popup(self) -> None:
        if not self.has_confirm_popup:
            return None

        try:
            self.browser.wait_until(lambda: self.has_confirm_popup_ok)
        except:
            self._print_error('Invalid popup.')
            return None
 
        self._print('Confirming popup...')
        ok = self.browser.find_element(CSS.CONFIRM_POPUP_OK)
        ok.click()
        time.sleep(LOOP_INTERVAL)
        return None

    def wait_for_login(self) -> None:
        self._print('Waiting for login...')
        while not self.is_logged_in:
            time.sleep(LOOP_INTERVAL)
        self._print('Logged in.')
        # remove check for login screen
        Check.remove_first_check(Check.LOGIN_SCREEN)


    def is_chat_open(self, phone_number: str) -> bool:
        if not self.is_chat_screen:
            self._print('is_chat_open -> not self.is_chat_screen')
            return False

        try:
            phone_number = str(int(phone_number.replace(' ', '')))
        except:
            self._print('is_chat_open -> invalid phone number')
            return False
        
        chat_title = self.chat_title
        try:
            chat_title = str(int(chat_title.replace(' ', '')))
        except:
            pass

        if chat_title == phone_number:
            self._print('is_chat_open -> chat_title == phone_number')
            return True

        el_chat_title = self.browser.find_element(CSS.CHAT_TITLE)
        if el_chat_title is None:
            self._print('is_chat_open -> el_chat_title is None')
            return False
        
        if not self.is_chat_info_open:
            self._print('is_chat_open -> not self.is_chat_info_open')
            el_chat_title.click()

            # if retry_until_true(lambda: self.is_chat_info_open):
            #     self._print('is_chat_open -> not self.is_chat_info_open')
            #     return False
            try:
                self.browser.wait_until(lambda: self.is_chat_info_open)
            except:
                self._print('is_chat_open -> not self.is_chat_info_open')
                return False

            # if retry_until_true(lambda: self.browser.find_element(CSS.CHAT_INFO_TITLE).text == chat_title):
            #     self._print('is_chat_open -> self.browser.find_element(CSS.CHAT_INFO_TITLE).text != chat_title')
            #     return False
            try:
                self.browser.wait_until(lambda: self.browser.find_element(CSS.CHAT_INFO_TITLE).text == chat_title)
            except:
                self._print('is_chat_open -> self.browser.find_element(CSS.CHAT_INFO_TITLE).text != chat_title')
                return False

        el_chat_info_subtitle = self.browser.find_element(CSS.CHAT_INFO_SUBTITLE)
        if el_chat_info_subtitle is None:
            self._print('is_chat_open -> el_chat_info_subtitle is None')
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
            self._print('is_chat_open -> chat_info_subtitle == phone_number')
            self.browser.execute_script('if (arguments[0]) arguments[0].innerText = arguments[1];', el_chat_title, chat_info_subtitle)
            return True

        self._print('is_chat_open -> False')
        return False


    def print_qr_code(self, invert=False, tty=False):
        self._print(f'Printing QR Code...')
        qr = qrcode.QRCode()
        qr.add_data(self.qr_content)
        qr.print_ascii(invert=invert, tty=tty)
        self.__is_qr_printed = True
    
    def new_chat(self, phone_number: str) -> Chat:
        chat = Chat(client=self, phone_number=phone_number)

        try:
            int(phone_number.replace(' ', ''))
        except:
            # self._print_error('Invalid phone number.')
            chat.is_phone_number_invalid = True
            raise Exception(f"Invalid phone number.")

        return chat
