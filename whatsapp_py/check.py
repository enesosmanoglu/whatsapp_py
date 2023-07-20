from typing import Callable

class Check:
    """Contains all the check types that are used to check if the check is true or not."""
    # TODO: Convert to Enum
    WHATSAPP_URL = 'whatsapp_url'
    WHATSAPP_READY = 'whatsapp_ready'
    CONFIRM_POPUP = 'confirm_popup'
    CONFIRM_POPUP_OK = 'confirm_popup_ok'
    CONFIRM_POPUP_CANCEL = 'confirm_popup_cancel'
    CONFIRM_POPUP_BUTTON = 'confirm_popup_button'
    LOADING_SCREEN = 'loading_screen'
    LOGIN_SCREEN = 'login_screen'
    QR_READY = 'qr_ready'
    QR_REFRESH = 'qr_refresh'
    LOGGED_IN = 'logged_in'
    MAIN_SCREEN = 'main_screen'
    CHAT_SCREEN = 'chat_screen'

    true_once: list[str] = []
    funcs: dict[str, Callable] = {}

    @staticmethod
    def remove_first_check(name: str):
        if name in Check.true_once:
            Check.true_once.remove(name)