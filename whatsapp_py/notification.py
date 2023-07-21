
from typing import NamedTuple

class Notification(NamedTuple):
    """Contains the information about a message notification.

    Attributes:
        phone_number (str): The phone number of the person who sent the message.
        body (str): The message body.
    """
    phone_number: str
    body: str