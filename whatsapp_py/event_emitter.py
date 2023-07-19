from typing import Callable

class EventEmitter:
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