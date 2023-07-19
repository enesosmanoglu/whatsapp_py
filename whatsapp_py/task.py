from __future__ import annotations
from datetime import datetime
from .const import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client
    from .message import Message

from .client_events import ClientEvents

class TaskType:
    SEND_MESSAGE = "send_message"

class Task:
    def __init__(self, client:Client, type:TaskType, priority:int = 0, start_date:datetime = datetime.now()):
        self.client = client
        self.type = type
        self.priority = priority
        self.start_date = start_date
        self.in_progress = False
        self.is_done = False
    
    def __str__(self):
        return f"Task({self.type})({self.priority})({self.start_date})"
    
    def start(self):
        self.in_progress = True
        self.client.emit(ClientEvents.TASK_STARTED, self)

    def done(self):
        self.in_progress = False
        self.is_done = True
        self.client.emit(ClientEvents.TASK_COMPLETED, self)


class MessageTask(Task):
    def __init__(self, client:Client, message:Message, priority:int = 0, start_date:datetime = datetime.now()):
        super().__init__(client, TaskType.SEND_MESSAGE, priority, start_date)
        self.message = message
    
    def start(self):
        super().start()
        try:
            self.message.chat._send_message(message=self.message)
        except Exception as e:
            self.message.error = str(e)
        self.done()
    
    def __str__(self):
        return f"Message{super().__str__()}({self.message})"

class TaskManager:
    def __init__(self):
        self.tasks:list[Task] = []
        self.current_task:Task = None
    
    @property
    def active_tasks(self):
        return sorted([task for task in self.tasks if task.start_date <= datetime.now() and not task.is_done], key=lambda task: task.start_date)
    
    def add_task(self, task:Task):
        self.tasks.append(task)

    def remove_task(self, task:Task):
        self.tasks.remove(task)

    def get_task(self):
        if self.current_task is not None:
            if not self.current_task.is_done:
                return self.current_task
            else:
                self.remove_task(self.current_task)
                self.current_task = None
        if len(self.tasks) == 0:
            return None
        task = max(self.active_tasks, key=lambda task: task.priority, default=None)
        self.current_task = task
        return task

