import time

from .const import *

def retry_until_true(method) -> bool:
    retry = 0
    while not method():
        if retry > MAX_LOOP_RETRIES:
            return True
        retry += 1
        time.sleep(LOOP_INTERVAL)
    return False