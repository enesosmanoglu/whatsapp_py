from typing import Callable

class EventEmitter:
    """Emits events and calls the functions that are listening to them.

    Attributes:
        __listeners (dict[str, list[Callable]]): A dictionary that maps events to a list of functions that are listening to them.
    """
    __listeners: dict[str, list[Callable]] = {}

    @staticmethod
    def on(event: str) -> Callable:
        """A decorator that adds a function to the list of functions that are listening to the event.

        Args:
            event (str): The event that the function is listening to.

        Returns:
            Callable: The function that is listening to the event.
        """
        def decorator(func: Callable):
            if event not in EventEmitter.__listeners:
                EventEmitter.__listeners[event] = []
            EventEmitter.__listeners[event].append(func)
            return func
        return decorator
    
    @staticmethod
    def emit(event: str, *args, **kwargs):
        """Calls all the functions that are listening to the event.

        Args:
            event (str): The event that is emitted.
            *args (Any): The arguments that are passed to the functions that are listening to the event.
            **kwargs (Any): The keyword arguments that are passed to the functions that are listening to the event.
        """
        if event in EventEmitter.__listeners:
            for func in EventEmitter.__listeners[event]:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event {event}: {e}")
    
    @staticmethod
    def remove(event: str, func: Callable):
        """Removes a function from the list of functions that are listening to the event.

        Args:
            event (str): The event that the function is listening to.
            func (Callable): The function that is listening to the event.
        """
        if event in EventEmitter.__listeners:
            EventEmitter.__listeners[event].remove(func)
    
    @staticmethod
    def clear(event: str):
        """Removes all the functions from the list of functions that are listening to the event.

        Args:
            event (str): The event that the functions are listening to.
        """
        if event in EventEmitter.__listeners:
            EventEmitter.__listeners[event].clear()