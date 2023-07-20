from __future__ import annotations
from datetime import datetime
from .const import *

from typing import TYPE_CHECKING, Self
if TYPE_CHECKING:
    from .client import Client
    from .message import Message

from .client_events import ClientEvents

class TaskType:
    """Task types."""
    # TODO: Convert to Enum
    SEND_MESSAGE = "send_message"

class Task:
    """Contains the information about a task.

    Args:
        client (Client): The client that the task belongs to.
        type (TaskType): The type of the task.
        priority (int): The priority of the task.
        start_date (datetime): The time that the task was started.
    """
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
        """Starts the task.
        
        * Emits `ClientEvents.TASK_STARTED` event.
        """
        self.in_progress = True
        self.client.emit(ClientEvents.TASK_STARTED, self)

    def done(self):
        """Marks the task as done.

        * Emits `ClientEvents.TASK_COMPLETED` event.
        """
        self.in_progress = False
        self.is_done = True
        self.client.emit(ClientEvents.TASK_COMPLETED, self)


class MessageTask(Task):
    """Contains the information about a message task.

    Args:
        client (Client): The client that the task belongs to.
        message (Message): The message to be sent.
        priority (int): The priority of the task.
        start_date (datetime): The time that the task was started.
    """
    def __init__(self, client:Client, message:Message, priority:int = 0, start_date:datetime = datetime.now()):
        super().__init__(client, TaskType.SEND_MESSAGE, priority, start_date)
        self.message = message
    
    def start(self):
        """Starts the task.

        * Emits `ClientEvents.TASK_STARTED` event.
        * Sends the message. If an error occurs, the error is set to the message.
        * Emits `ClientEvents.TASK_COMPLETED` event after the message is sent or an error occurs.
        """
        super().start()
        try:
            self.message.chat._send_message(message=self.message)
        except Exception as e:
            self.message.error = str(e)
        self.done()
    
    def __str__(self):
        return f"Message{super().__str__()}({self.message})"

class TaskManager:
    """Manages the tasks."""
    tasks:list[Task] = []
    """The list of tasks."""
    current_task:Task = None
    """The current task."""
    
    def __init__(self):
        self.tasks:list[Task] = []
        self.current_task:Task = None
    
    @property
    def active_tasks(self):
        """Filters the tasks with `start_date` before now and `is_done` is `False` and sorts them by `start_date`.
        
        Returns:
            active_tasks (list[Task]): The list of active tasks.
        """
        return sorted([task for task in self.tasks if task.start_date <= datetime.now() and not task.is_done], key=lambda task: task.start_date)
    
    def add_task(self, task:Task) -> Self:
        """Adds a task to the list of tasks.

        Args:
            task (Task): The task to be added.

        Returns:
            task_manager (TaskManager): The task manager instance.
        """
        self.tasks.append(task)
        return self

    def remove_task(self, task:Task) -> Self:
        """Removes a task from the list of tasks.

        Args:
            task (Task): The task to be removed.

        Returns:
            task_manager (TaskManager): The task manager instance.
        """
        self.tasks.remove(task)
        return self

    def get_task(self) -> Task:
        """Gets the next task to be executed.

        * If the current task is not done, it returns the current task.
        * If the current task is done, it removes the current task from the list of tasks and returns the next task.

        Returns:
            task (Task): The next task to be executed.
        """
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

