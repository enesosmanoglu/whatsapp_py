# Using with events

---

## Import classes
```py
from whatsapp_py import Client, ClientEvents
```

---

## Create client
See [Basic Usage](./basic.md#create-client) for more details.
```py
client = Client()
```

---

## Register event handlers
Decorate functions with `#!python @client.on('event_name')` to register event handlers.

Function name does not matter.

For the `#!python 'event_name'`, use the [`ClientEvents`](/reference/client_events) class.

!!! example

    ```py
    @client.on( ClientEvents.START )
    def on_start():
        print(">> Client started")
    ```

For the list of available events, see [All Client Events](#all-client-events) below.

---
## Client Events

### Summary

!!! tip

    Click on the **event name** to jump to the details.

|                Event Name                 |                                 Parameters                                 |                                              Description                                              |
| :---------------------------------------: | :------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------: |
| [BROWSER_CREATED](#browser-created-event) |                  [`Browser`](/reference/browser/#browser)                  |                            Browser instance created before starting client                            |
|           [START](#start-event)           |                                     -                                      |                               Client started after browser initialized                                |
|          [UPDATE](#update-event)          |                                     -                                      | Fired every [`LOOP_INTERVAL`](/reference/constants/#const.LOOP_INTERVAL) seconds after client started |
|            [STOP](#stop-event)            |                                     -                                      |                                        Client stopped on exit                                         |
|           [ERROR](#error-event)           | [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception) |                                         Client error occurred                                         |
|         [QR_CODE](#qr-code-event)         |                                   `str`                                    |                                           QR code received                                            |
|       [LOGGED_IN](#logged-in-event)       |                                     -                                      |                                           Client logged in                                            |
|      [LOGGED_OUT](#logged-out-event)      |                                     -                                      |                                           Client logged out                                           |
|    [TASK_STARTED](#task-started-event)    |             [`MessageTask`](/reference/task/#task.MessageTask)             |                                             Task started                                              |
|  [TASK_COMPLETED](#task-completed-event)  |             [`MessageTask`](/reference/task/#task.MessageTask)             |                                            Task completed                                             |
|    [NOTIFICATION](#notification-event)    |    [`Notification`](/reference/notification/#notification.Notification)    |                                         Notification received                                         |

---

### Details

#### Browser Created Event
* Fired when browser instance is created.

* Can be used to set [browser network conditions](/reference/browser/#browser.browser.Browser.set_network_conditions).

```py
@client.on(ClientEvents.BROWSER_CREATED)
def on_browser_created(browser):
    print(">> Browser created", browser)

    # Set network conditions
    browser.set_network_conditions(
        offline = False,
        latency = 0,
        download_throughput = 10 * 1024,
        upload_throughput = 10 * 1024
    )
```

#### Start Event
* Fired after browser is initialized.

```py
@client.on(ClientEvents.START)
def on_start():
    print(">> Client started")
 

```

#### Update Event
* Fired every [`LOOP_INTERVAL`](/reference/constants/#const.LOOP_INTERVAL) seconds.
* Fired after client is started successfully.
* Can be used to do periodic tasks while client is running.
* Can be used with [SQL Database](/usage/sql) to check for new datas periodically. 

```py
@client.on(ClientEvents.UPDATE)
def on_update():
    # print(">> Client update") # No need to print this every second :)
    
    # Do something periodically
    pass
```

#### Stop Event
* Fired when client is stopped.

```py
@client.on(ClientEvents.STOP)
def on_stop():
    print(">> Client stopped")
```

#### Error Event
* Fired when client encounters an error.

```py
@client.on(ClientEvents.ERROR)
def on_error(error: Exception):
    print(">> Client error", error)
```

#### QR Code Event
* Fired when QR code is received.
* Fired when QR code is refreshed.

```py
@client.on(ClientEvents.QR_CODE)
def on_qr_code(qr_code: str):
    print(">> Client QR code", qr_code)
```

#### Logged In Event
* Fired when main page is loaded after scanning QR code. 
* Can be used to send messages after client is logged in.

!!! info "• Fired after client is started if QR scanned in one of the previous sessions"

```py
@client.on(ClientEvents.LOGGED_IN)
def on_logged_in():
    print(">> Client logged in")
    
    # Send message
    chat = client.new_chat("{phone_number}")
    chat.send_message("Hello world")
```

#### Logged Out Event
* Fired when client is logged out.

```py
@client.on(ClientEvents.LOGGED_OUT)
def on_logged_out():
    print(">> Client logged out")
```

#### Task Started Event
* Fired when a task is started.
* See [Task](/reference/task) for more details.

```py
@client.on(ClientEvents.TASK_STARTED)
def on_task_started(message_task):
    print(">> Client task started", message_task)
```

#### Task Completed Event
* Fired when a task is completed.
* See [Task](/reference/task) for more details.

```py
@client.on(ClientEvents.TASK_COMPLETED)
def on_task_completed(message_task):
    print(">> Client task completed", message_task)
```

#### Notification Event
* Fired when a notification is received.
* See [Notification](/reference/notification) for more details.

```py
@client.on(ClientEvents.NOTIFICATION)
def on_notification(notification):
    print(">> Client notification", notification)
```