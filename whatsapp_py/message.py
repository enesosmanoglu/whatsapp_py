from __future__ import annotations
import os
from datetime import datetime
from .css import CSS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .chat import Chat
    from .browser import WebElement

class Message:
    def __init__(self, chat:Chat=None, id:str=None, content:str=None, file:str=None, media:str=None, time:datetime=None, nonce:str=str(datetime.now().timestamp())):
        self.chat = chat
        self.id = id
        self.content = content
        self.file = file
        self.media = media
        self.time = time
        self.nonce = str(nonce)
        self.__check_arguments()
        self.element = None
        self.error = None
    
    def __str__(self):
        str_args = []
        if self.id is not None:
            str_args.append(f"id={self.id}")
        if self.chat is not None:
            str_args.append(f"chat={self.chat}")
        if self.content is not None:
            str_args.append(f"content={self.content}")
        if self.file is not None:
            str_args.append(f"file={self.file}")
        if self.media is not None:
            str_args.append(f"media={self.media}")
        if self.time is not None:
            str_args.append(f"time={self.time.strftime('%d/%m/%Y %H:%M:%S')}")
        if self.nonce is not None:
            str_args.append(f"nonce={self.nonce}")
        return f"Message({', '.join(str_args)})"

    def __check_arguments(self):
        if self.content is not None and self.content.replace(' ', '') == "":
            self.content = None

        if self.file is not None and self.file.replace(' ', '') == "":
            self.file = None
        
        if self.media is not None and self.media.replace(' ', '') == "":
            self.media = None

        if self.content is None and self.file is None and self.media is None:
            raise ValueError("Message must have content, file or media.")
    
        if self.file is not None and self.media is not None:
            raise ValueError("Message cannot have both file and media.")
        
        if self.file is not None:
            if not os.path.isabs(self.file):
                self.file = os.path.abspath(self.file)
            if not os.path.isfile(self.file):
                raise ValueError("File does not exist.")
        
        if self.media is not None:
            if not os.path.isabs(self.media):
                self.media = os.path.abspath(self.media)
            if not os.path.isfile(self.media):
                raise ValueError("Media does not exist.")
    
    def set_element(self, element: WebElement) -> Message:
        self.element = element
        return self

    def set_id(self, id:str) -> Message:
        self.id = id
        return self
    
    def set_time(self, time:datetime) -> Message:
        self.time = time
        return self
    
    @property
    def el_content(self):
        if self.element is None:
            return None
        return self.chat.client.browser.find_element(CSS._CONTENT, self.element)
    
    @property
    def el_meta(self):
        if self.element is None:
            return None
        return self.chat.client.browser.find_element(CSS._META, self.element)
    
    @property
    def el_time(self):
        if self.element is None:
            return None
        return self.chat.client.browser.find_element(CSS._META_TIME, self.element)
    
    @property
    def el_status(self):
        if self.element is None:
            return None
        return self.chat.client.browser.find_element(CSS._META_STATUS, self.element)

    @property
    def is_sent(self) -> bool:
        return self.element is not None
    
    # msg-time || msg-check || msg-dblcheck
    # Sending  || Delivered || Read
    @property
    def status_w(self) -> str:
        if self.el_status is None:
            return None
        return self.el_status.get_attribute("data-testid")

    @property
    def status_w_index(self) -> int:
        if self.status_w is None:
            return -1
        return ["msg-time", "msg-check", "msg-dblcheck"].index(self.status_w)

    @property
    def is_sending_w(self) -> bool:
        return self.status_w == "msg-time"
    
    @property
    def is_delivered_w(self) -> bool:
        return self.status_w == "msg-check"
    
    @property
    def is_read_w(self) -> bool:
        return self.status_w == "msg-dblcheck"

    @property
    def content_w(self) -> str:
        if self.el_content is None:
            return None
        return self.el_content.text
    
    @property
    def time_w(self) -> str:
        if self.el_time is None:
            return None
        return self.el_time.text
    
    @property
    def time_w_datetime(self) -> datetime:
        if self.time_w is None:
            return None
        return datetime.strptime(self.time_w, "%H:%M")
    
    