class ClientEvents:
    """Client events."""
    # TODO: Convert to Enum

    BROWSER_CREATED = 'browser_created'
    """Fired when the browser is created."""

    START = 'start'
    """Fired when the client is started."""

    UPDATE = 'update'
    """Fired when the client is updated. Default interval is 0.5 seconds."""

    STOP = 'stop'
    """Fired when the client is stopped."""

    ERROR = 'error'
    """Fired when the client encounters an error."""

    LOGGED_IN = 'logged_in'
    """Fired when the client is logged in."""

    LOGGED_OUT = 'logged_out'
    """Fired when the client is logged out."""

    TASK_STARTED = 'task_started'
    """Fired when a task is started."""

    TASK_COMPLETED = 'task_completed'
    """Fired when a task is completed."""

    NOTIFICATION = 'notification'
    """Fired when a notification is received."""
