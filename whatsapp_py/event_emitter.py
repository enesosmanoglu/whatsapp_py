from typing import Callable

class EventEmitter:
    """Emits events and calls the functions that are listening to them.

    Attributes:
        __listeners (dict[str, list[Callable]]): A dictionary that maps events to a list of functions that are listening to them.
    
    Methods:
        on(event: str): A decorator that adds a function to the list of functions that are listening to the event.
        emit(event: str, *args, **kwargs): Calls all the functions that are listening to the event.
        remove(event: str, func: Callable): Removes a function from the list of functions that are listening to the event.
        clear(event: str): Removes all the functions from the list of functions that are listening to the event.
    """
    __listeners: dict[str, list[Callable]] = {}

    @staticmethod
    def on(event: str):
        def decorator(func: Callable):
            if event not in EventEmitter.__listeners:
                EventEmitter.__listeners[event] = []
            EventEmitter.__listeners[event].append(func)
            return func
        return decorator
    
    @staticmethod
    def emit(event: str, *args, **kwargs):
        if event in EventEmitter.__listeners:
            for func in EventEmitter.__listeners[event]:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event {event}: {e}")
    
    @staticmethod
    def remove(event: str, func: Callable):
        if event in EventEmitter.__listeners:
            EventEmitter.__listeners[event].remove(func)
    
    @staticmethod
    def clear(event: str):
        if event in EventEmitter.__listeners:
            EventEmitter.__listeners[event].clear()