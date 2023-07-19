# Using with events

## Import classes
```py
from whatsapp_py import Client, ClientEvents
```

## Create client
See [Basic Usage](./basic.md#create-client) for more details.
```py
client = Client()
```

## Register event handlers
Decorate functions with `@client.on(event_name)` to register event handlers. Function name does not matter.

For the `event_name`, use the `ClientEvents` class.

For example, to register a handler for [Error Event](#error-event), decorate a function with `@client.on(ClientEvents.ERROR)`.

For the list of available events, see [Client Events](#client-events).

---

### Client Events

#### Browser Created Event
```py
@client.on(ClientEvents.BROWSER_CREATED)
def on_browser_created(*args, **kwargs):
    print(">> Browser created", *args, **kwargs)
```

#### Start Event
```py
@client.on(ClientEvents.START)
def on_start(*args, **kwargs):
    print(">> Client started", *args, **kwargs)
```

#### Update Event
```py
@client.on(ClientEvents.UPDATE)
def on_update(*args, **kwargs):
    print(">> Client update", *args, **kwargs)
```

#### Stop Event
```py
@client.on(ClientEvents.STOP)
def on_stop(*args, **kwargs):
    print(">> Client stopped", *args, **kwargs)
```

#### Error Event
```py
@client.on(ClientEvents.ERROR)
def on_error(*args, **kwargs):
    print(">> Client error", *args, **kwargs)
```

#### Logged In Event
```py
@client.on(ClientEvents.LOGGED_IN)
def on_logged_in(*args, **kwargs):
    print(">> Client logged in", *args, **kwargs)
```

#### Logged Out Event
```py
@client.on(ClientEvents.LOGGED_OUT)
def on_logged_out(*args, **kwargs):
    print(">> Client logged out", *args, **kwargs)
```

#### Task Started Event
```py
@client.on(ClientEvents.TASK_STARTED)
def on_task_started(*args, **kwargs):
    print(">> Client task started", *args, **kwargs)
```

#### Task Completed Event
```py
@client.on(ClientEvents.TASK_COMPLETED)
def on_task_completed(*args, **kwargs):
    print(">> Client task completed", *args, **kwargs)
```

#### Notification Event
```py
@client.on(ClientEvents.NOTIFICATION)
def on_notification(*args, **kwargs):
    print(">> Client notification", *args, **kwargs)
```