from __future__ import annotations

import time
from datetime import datetime, timedelta

from .const import *
from .helpers import *
from .css import CSS
from .message import Message
from .task import MessageTask

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

class Chat:
    is_phone_number_invalid = False

    def __init__(self, client:Client, phone_number):
        self.client = client
        self.phone_number = phone_number

    def __str__(self):
        return f'Chat({self.phone_number})'

    def _print(self, *args, **kwargs):
        self.client._print(f'[{self}]', *args, **kwargs)
    
    def _print_error(self, *args, **kwargs):
        self.client._print_error(f'[{self}]', *args, **kwargs)

    @property
    def is_open(self):
        return self.client.is_chat_open(self.phone_number)

    def open(self):
        self._is_loading = True
        self.client.load_chat_page(self)
        
        # if retry_until_true(lambda: self.client.has_confirm_popup):
        #     self._print_error('Invalid request. Please report this issue.')
        #     return False
        try:
            self.client.browser.wait_until(lambda: self.client.has_confirm_popup_ok or not self.client.has_confirm_popup, timeout=30)
            # WebDriverWait(self.client.browser._driver, 30).until(lambda _: self.client.is_true(Check.CONFIRM_POPUP))
        except:
            # raise Exception('Invalid request.')
            self._print_error('Invalid request. Please report this issue.')
            return False
        
        # try:
        #     # WebDriverWait(self.client.driver, 10).until(lambda _: not self.client.has_confirm_popup_cancel)
        #     self.client.browser.wait_until(lambda: not self.client.has_confirm_popup_cancel, timeout=20)
        # except:
        #     raise Exception('Invalid popup.')
        #     self._print_error('Invalid popup.')
        #     return False

        self._print('Chat page loaded.')
        self._is_loading = False
        
        if self.client.has_confirm_popup_ok:
            self.client.confirm_popup()
            self.is_phone_number_invalid = True
            self._print('Invalid phone number.')
            return False

        # retry = 0
        # while not self.is_open:
        #     if retry > MAX_LOOP_RETRIES:
        #         return False
        #     retry += 1
        #     time.sleep(LOOP_INTERVAL)
        try:
            self.client.browser.wait_until(lambda: self.is_open)
        except:
            raise Exception('Unable to open chat.')
            self._print_error('Unable to open chat.')
            return False
        
        return True
    
    def send_message(self, content:str=None, file:str=None, media:str=None, delay:timedelta = None, at_time:datetime=None, nonce:str=str(datetime.now().timestamp())) -> Message:
        message = Message(chat=self, content=content, file=file, media=media, time=None, nonce=nonce)
        task = MessageTask(client=self.client, message=message)

        if at_time is not None:
            task.start_date = at_time

        if delay is not None:
            task.start_date += delay

        self.client.task_manager.add_task(task)
        self._print(f"Message scheduled: {task}")

        return message
        
    
    def _send_message(self, message:Message) -> Message:
        if self.is_phone_number_invalid:
            raise Exception(f"Invalid phone number.")
            self._print_error(f"Invalid phone number. Please don't use this chat object anymore.")
            return

        if not self.is_open:
            self._print(f"Chat is not open. Opening chat to send message.")
            _success = self.open()
            if not _success:
                if self.is_phone_number_invalid:
                    raise Exception(f"Invalid phone number.")
                    self._print_error(f"Invalid phone number. Please don't use this chat object anymore.")
                else:
                    raise Exception(f"Unable to open chat.")
                    self._print_error(f"Unable to open chat. Please report this issue.")
                return
        
        # Send message
        chat_input = self.client.browser.find_element(CSS.CHAT_INPUT)
        if chat_input is None:
            raise Exception(f"Chat input box not found.")
            self._print_error(f"Chat input box not found. Please report this issue.")
            return

        last_sent_message_data = self.client.last_sent_message_data
        self._print(f"Last sent message data: {last_sent_message_data}")

        chat_input.clear()

        if message.content is not None:
            self._print(f"Typing message content: {message.content}")
            chat_input.send_keys(message.content)
            time.sleep(0.1)

        if message.file is not None or message.media is not None:
            clip_buttton = self.client.browser.find_element(CSS.CLIP_BUTTON)
            if clip_buttton is None:
                raise Exception(f"Clip button not found.")
                self._print_error(f"Clip button not found. Please report this issue.")
                return
            
            clip_buttton.click()

            self._print(f"Uploading: {message.file}")
            document_input = self.client.browser.find_element(CSS.DOCUMENT_INPUT if message.file is not None else CSS.MEDIA_INPUT)
            if document_input is None:
                raise Exception(f"File selection input not found.")
                self._print_error(f"File selection input not found. Please report this issue.")
                return
            
            self.client.browser.execute_script("arguments[0].style.display = 'block';", document_input)
            
            try:
                document_input.send_keys(message.file if message.file is not None else message.media)
            except Exception as e:
                raise Exception(f"File not found: {message.file if message.file is not None else message.media}")
                self._print_error(f"File not found: {message.file if message.file is not None else message.media}")
                return
            
            try:
                self.client.browser.wait_until(lambda: self.client.browser.find_element(CSS.MEDIA_CAPTION), timeout=10)
            except:
                raise Exception(f"File upload failed.")
                self._print_error(f"File upload failed. Please report this issue.")
                return


        el_send_button = self.client.browser.find_element(CSS.SEND_BUTTON)
        if el_send_button is None:
            raise Exception(f"Send button not found.")
            self._print_error(f"Send button not found. Please report this issue.")
            return
        
        el_send_button.click()

        # Wait for message to be sent
        time.sleep(0.2)
        
        # if message.content is not None:
        #     try:
        #         self._print(f"Waiting for message to be sent... (content: {message.content})")
        #         self.client.browser._driver.execute_script("Array.from(arguments[0].querySelectorAll('img')).forEach(e=>e.outerHTML = e.getAttribute('data-plain-text'))", self.client.browser.find_element(CSS.LAST_MESSAGE_CONTENT))
        #         self.client.browser.wait_until(lambda: self.client.browser.find_element(CSS.LAST_MESSAGE_CONTENT).text == message.content)
        #     except:
        #         self._print_error(f"Unable to send message. Please report this issue.")
        #         return

        # wait until last_sent_message_data is updated
        self._print(f"Waiting for message to be sent... {message}")
        try:
            self.client.browser.wait_until(lambda: self.client.last_sent_message_data != last_sent_message_data, timeout=20)
        except:
            raise Exception(f"Unable to send message.")
            self._print_error(f"Unable to send message. Please report this issue.")
            return
        
        last_sent_message_data = self.client.last_sent_message_data
        
        is_sent, phone_mail, message_id, *_ = last_sent_message_data.split("_") # last_message_row.get_attribute("data-id").split("_")
        self._print(f"Message datas from WhatsApp:"\
            f"\n\t└─╴ {is_sent}"\
            f"\n\t└─╴ {phone_mail}"\
            f"\n\t└─╴ {message_id}"\
        )

        message.set_id(message_id) \
            .set_time(datetime.now()) \
            .set_element(self.client.get_message_from_data(last_sent_message_data))

        if message.content is not None:
            el_message_content = message.el_content # self.client.browser.find_element(CSS.LAST_MESSAGE_CONTENT)
            if el_message_content.text != message.content:
                raise Exception(f"Message content does not match.")
                self._print_error(f"Error: Message content does not match. Please report this issue."\
                    f"\n\t└─╴ Expected: {message.content}"\
                    f"\n\t└─╴ Actual: {el_message_content.text}")
                return
        
        try:
            self.client.browser.wait_until(
                # msg-time || msg-check || msg-dblcheck
                # Sending  || Delivered || Read
                # lambda: self.client.browser.find_element(CSS.LAST_MESSAGE_STATUS).get_attribute('data-testid') in ['msg-check', 'msg-dblcheck'],
                # lambda: message.element_status.get_attribute('data-testid') in ['msg-check', 'msg-dblcheck'],
                lambda: message.is_delivered_w or message.is_read_w,
                timeout=30,
            )
            sent_in_time = True
        except:
            sent_in_time = False

        if not sent_in_time:
            self._print_error(f"Message could not be sent in time due to slow internet connection."\
                f"\n\t└─╴ Message may have been sent. Please check your WhatsApp to make sure.")
        else:
            self._print(f"Message sent successfully.")

        # message = Message(chat=self, id=message_id, content=content, file=None, media=None, time=None)
        self._print(f"Message: {message}")
        return message


