# Basic Usage

---

## Import class
```py
from whatsapp_py import Client
```

---

## Create client
See [Client()](/reference/client/#client.Client) for more information.

!!! info

    Creating client will automatically start the browser, open WhatsApp Web, and wait for QR code scan.

=== "Default Options"

    ```py
    client = Client()
    ```
=== "Custom Options"

    ```py
    client = Client(
        print_qr_code=False, # default: True
        WebDriver=Client.Edge, # default: Client.Chrome
        user_data_dir='my_user_data', # default: 'user_data'
        headless=False, # default: True
        debug=True, # default: False
    )
    ```

!!! info
    Session data will be saved in ``user_data_dir`` folder in the current directory.
    
    So, you don't need to scan QR code again next time you run the script.

---

## Create chat
```py
chat = client.new_chat('{phone_number}')
```
!!! danger

    For the phone number, you must use any of the following formats:
    
    * **+1234567890** _`(country code is required)`_
    * **1234567890** _`(without plus sign)`_
    * **+1 234 567 890** _`(spaces are ignored)`_

---

## Send message
See [Chat.send_message()](/reference/chat/#chat.Chat.send_message) for more information.
##### Send text message
```py
chat.send_message('This is text message')
```
##### Send media message (image, video, etc.)
=== "with caption"

    ```py
    chat.send_message('This is caption', media='{path_to_media}')
    ```
=== "without caption"

    ```py
    chat.send_message(media='{path_to_media}')
    ```
##### Send file message (document, etc.)
=== "with caption"

    ```py
    chat.send_message('This is caption', file='{path_to_file}')
    ```
=== "without caption"

    ```py
    chat.send_message(file='{path_to_file}')
    ```

!!! info
    You can give ``relative path`` or ``absolute path`` to the file and media.

!!! warning
    You can't set ``file`` and ``media`` at the same time.

    ```py
    chat.send_message(file='{path_to_file}', media='{path_to_media}')
    ```

---


## Send scheduled message
```py
from datetime import datetime, timedelta
```

##### Send delayed message
```py
delay = timedelta(seconds=10)
```
```py
chat.send_message('This is text message', delay=delay)
```

##### Send message at specific time
```py
at_time = datetime(2023, 07, 20, 16, 54)
```
```py
chat.send_message('This is text message', at_time=at_time)
```

!!! tip
    You can use ``delay`` and ``at_time`` at the same time.

    ```py
    chat.send_message('This is text message', delay=delay, at_time=at_time)
    ```

--- 