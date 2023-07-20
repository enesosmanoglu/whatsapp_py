class CSS:
    """Contains CSS Selectors for WhatsApp Web"""
    APP = f"div#app"
    _TEXT = f".selectable-text.copyable-text"

    CONFIRM_POPUP = f"{APP} [data-testid=confirm-popup][role=dialog] div"
    CONFIRM_POPUP_CONTENTS = f"{CONFIRM_POPUP} [data-testid=popup-contents]"
    CONFIRM_POPUP_CANCEL = f"{CONFIRM_POPUP} [data-testid=popup-controls-cancel]"
    CONFIRM_POPUP_OK = f"{CONFIRM_POPUP} [data-testid=popup-controls-ok]"

    # MAIN_PAGE = "div[data-testid=drawer-left]"
    LOADING_SCREEN = f"{APP} div[data-testid=wa-web-loading-screen]"
    LOADING_PROGRESS = f"{LOADING_SCREEN} progress"

    LANDING_WINDOW = f"{APP} div.landing-window"
    LINK_WITH_PHONE = f"{LANDING_WINDOW} [data-testid=link-device-qrcode-alt-linking-hint]"
    QR_CODE = f"{LANDING_WINDOW} [data-testid=qrcode]"
    QR_REFRESH = f"{QR_CODE} [data-testid=refresh-large]"

    MIDDLE_DRAWER = f"{APP} [data-testid=drawer-middle]"
    RIGHT_DRAWER = f"{APP} [data-testid=drawer-right]"
    CHAT_INFO_DRAWER = f"{RIGHT_DRAWER} [data-testid=chat-info-drawer]"

    INTRO_TITLE = f"{APP} [data-testid=intro-title]"
    CONVERSATION_PANEL = f"{APP} [data-testid=conversation-panel-wrapper]"

    CHAT_INPUT = f"{CONVERSATION_PANEL} div[data-testid=conversation-compose-box-input] p"
    MEDIA_CAPTION = f"{APP} div[data-testid=media-caption-input-container] p"
    CLIP_BUTTON = f"{CONVERSATION_PANEL} [data-testid=conversation-clip] [role=button]"
    DOCUMENT_INPUT = f"{APP} [data-testid=attach-document]+input"
    MEDIA_INPUT = f"{APP} [data-testid=attach-image]+input"
    SEND_BUTTON = f"{APP} span[data-testid=send]"

    CONVERSATION_PANEL_MESSAGES = f"{CONVERSATION_PANEL} div[data-testid=conversation-panel-messages]"
    LAST_MESSAGE_ROW = f"{CONVERSATION_PANEL_MESSAGES} [role=application] [role=row]:last-child div"
    _CONTENT = f"span.copyable-text"
    _META = f"div[data-testid=msg-meta]"
    _META_TIME = f"{_META} span"
    _META_STATUS = f"{_META} div span"
    LAST_MESSAGE_CONTENT = f"{LAST_MESSAGE_ROW} {_CONTENT}"
    LAST_MESSAGE_META = f"{LAST_MESSAGE_ROW} {_META}"
    LAST_MESSAGE_TIME = f"{LAST_MESSAGE_ROW} {_META_TIME}"
    LAST_MESSAGE_STATUS = f"{LAST_MESSAGE_ROW} {_META_STATUS}"

    CHAT_TITLE = f"{CONVERSATION_PANEL} [data-testid=conversation-info-header-chat-title]"
    CHAT_INFO_TITLE = f"{CHAT_INFO_DRAWER} [data-testid=contact-info-subtitle]"
    CHAT_INFO_SUBTITLE = f"{CHAT_INFO_DRAWER} span>span"
    CHAT_INFO_CLOSE = f"{CHAT_INFO_DRAWER} [data-testid=btn-closer-drawer]"

    @staticmethod
    def concat(*args: str) -> str:
        """Concatenates the given arguments with a space in between.
        
        Args:
            *args (str): The arguments to concatenate."""
        return " ".join(args)