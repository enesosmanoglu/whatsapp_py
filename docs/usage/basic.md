# Basic Usage

## Import class
```py
from whatsapp_py import Client
```

## Create client
!!! info

    Creating client will automatically start the browser, open WhatsApp Web, and wait for QR code scan.


### With default options
```py
client = Client()
```
### With custom options
```py
client = Client(
    print_qr_code=False, # default: True
    WebDriver=Client.Edge, # default: Client.Chrome
    user_data_dir='my_user_data', # default: 'user_data'
    headless=False, # default: True
    debug=True, # default: False
)
```