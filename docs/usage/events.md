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

For the list of available events, see [Client Events](#client-events) below.

---

## Client Events

| <center>Event Name</center>                                | <center>Parameters</center>                                                                 | <center>Description</center>                                                                          |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| <center>[BROWSER_CREATED](#browser-created-event)</center> | <center>[`Browser`](/reference/browser/#browser)</center>                                   | Browser instance created before starting client                                                       |
| <center>[START](#start-event)</center>                     | <center>-</center>                                                                          | Client started after browser initialized                                                              |
| <center>[UPDATE](#update-event)</center>                   | <center>-</center>                                                                          | Fired every [`LOOP_INTERVAL`](/reference/constants/#const.LOOP_INTERVAL) seconds after client started |
| <center>[STOP](#stop-event)</center>                       | <center>-</center>                                                                          | Client stopped on exit                                                                                |
| <center>[ERROR](#error-event)</center>                     | <center>[`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)</center> | Client error occurred                                                                                 |
| <center>[QR_CODE](#qr-code-event)</center>                 | <center>`str`</center>                                                                      | QR code received                                                                                      |
| <center>[LOGGED_IN](#logged-in-event)</center>             | <center>-</center>                                                                          | Client logged in                                                                                      |
| <center>[LOGGED_OUT](#logged-out-event)</center>           | <center>-</center>                                                                          | Client logged out                                                                                     |
| <center>[TASK_STARTED](#task-started-event)</center>       | <center>[`MessageTask`](/reference/task/#task.MessageTask)</center>                                            | Task started                                                                                          |
| <center>[TASK_COMPLETED](#task-completed-event)</center>   | <center>[`MessageTask`](/reference/task/#task.MessageTask)</center>                                            | Task completed                                                                                        |
| <center>[NOTIFICATION](#notification-event)</center>       | <center>[`Notification`](/reference/notification/#notification.Notification)</center>                    | Notification received                                                                                 |

---

#### Client Events Examples

##### Browser Created Event
```py
@client.on(ClientEvents.BROWSER_CREATED)
def on_browser_created(browser):
    print(">> Browser created", browser)
```

##### Start Event
```py
@client.on(ClientEvents.START)
def on_start():
    print(">> Client started")
```

##### Update Event
```py
@client.on(ClientEvents.UPDATE)
def on_update():
    print(">> Client update")
```

##### Stop Event
```py
@client.on(ClientEvents.STOP)
def on_stop():
    print(">> Client stopped")
```

##### Error Event
```py
@client.on(ClientEvents.ERROR)
def on_error(error: Exception):
    print(">> Client error", error)
```

##### QR Code Event
```py
@client.on(ClientEvents.QR_CODE)
def on_qr_code(qr_code: str):
    print(">> Client QR code", qr_code)
```

##### Logged In Event
```py
@client.on(ClientEvents.LOGGED_IN)
def on_logged_in():
    print(">> Client logged in")
```

##### Logged Out Event
```py
@client.on(ClientEvents.LOGGED_OUT)
def on_logged_out():
    print(">> Client logged out")
```

##### Task Started Event
```py
@client.on(ClientEvents.TASK_STARTED)
def on_task_started(message_task):
    print(">> Client task started", message_task)
```

##### Task Completed Event
```py
@client.on(ClientEvents.TASK_COMPLETED)
def on_task_completed(message_task):
    print(">> Client task completed", message_task)
```

##### Notification Event
```py
@client.on(ClientEvents.NOTIFICATION)
def on_notification(notification):
    print(">> Client notification", notification)
```