"""Helper functions for whatsapp_py."""

import time

from .const import *

def retry_until_true(method) -> bool:
    """Retries the method until it returns True or max retries is reached.

    Uses `time.sleep` to wait between retries.

    Args:
        method (Callable[[], bool]): The method to retry.

    Returns:
        not_completed (bool): True if max retries is reached, False otherwise.
    """
    retry = 0
    while not method():
        if retry > MAX_LOOP_RETRIES:
            return True
        retry += 1
        time.sleep(LOOP_INTERVAL)
    return False