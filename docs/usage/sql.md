# Using with SQL Database
In this example, we will create a client that will send messages from a SQL database. 

* The client will send messages from rows that are not completed yet. 
* After the message is sent, the client will update the row with the message id. 
* If the message failed to send, the client will update the row with the error message. 

## Database Schema

In this example database, we have 3 tables: `Tasks`, `Messages`, and `Statuses`.

* `Tasks` table contains the messages that will be sent.
* `Messages` table contains the messages that have been sent.
* `Statuses` table contains the statuses of the messages that have been sent.

Create a database named `DbWhatsApp` and run the following scripts to create the tables.

#### Tasks

```sql
CREATE TABLE Tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    text_content VARCHAR(1000) NOT NULL,
    file_path VARCHAR(1000) NULL,
    media_path VARCHAR(1000) NULL,
    start_at DATETIME NULL,
    msg_id VARCHAR(100) NULL,
    error VARCHAR(1000) NULL
)
```

| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| `id` | `INT` | `false` | The id of the task. |
| `phone_number` | `VARCHAR(20)` | `false` | The phone number of the recipient. |
| `text_content` | `VARCHAR(1000)` | `false` | The text content of the message. |
| `file_path` | `VARCHAR(1000)` | `true` | The file path of the file to be sent. |
| `media_path` | `VARCHAR(1000)` | `true` | The media path of the media to be sent. |
| `start_at` | `DATETIME` | `true` | The time when the message will be sent. |
| `msg_id` | `VARCHAR(100)` | `true` | The id of the message. |
| `error` | `VARCHAR(1000)` | `true` | The error message if the message failed to send. |

#### Messages

```sql
CREATE TABLE Messages (
    id VARCHAR(100) PRIMARY KEY,
    sent_at DATETIME NOT NULL,
    status_id INT NOT NULL
)
```

| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| `id` | `VARCHAR(100)` | `false` | The id of the message. |
| `sent_at` | `DATETIME` | `false` | The time when the message was sent. |
| `status_id` | `INT` | `false` | The id of the status. |

#### Statuses

```sql
CREATE TABLE Statuses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
    description VARCHAR(1000) NULL
)

INSERT INTO Statuses (name, description) VALUES
    ('msg-time', 'Sending'),
    ('msg-check', 'Delivered'),
    ('msg-dblcheck', 'Read')
```

| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| `id` | `INT` | `false` | The id of the status. |
| `name` | `VARCHAR(100)` | `false` | The name of the status. |
| `description` | `VARCHAR(1000)` | `true` | The description of the status. |

---

## How it works

* The client will get all rows from `Tasks` table that are not completed yet.
* The client will iterate through the rows.
* The client will create a chat with the recipient's phone number.
* The client will send the message.
* If the message is sent successfully, the client will update the row with the message id.
* If the message failed to send, the client will update the row with the error message.
* The client will repeat the process every time the `UPDATE` event is emitted.

---

## Import classes
```py
from whatsapp_py import Client, ClientEvents
```
```py
from whatsapp_py import SQL, ConnectionConfig
```
```py
from whatsapp_py import MessageTask, SqlResult # for type hinting
```

---

## Create client
See [Basic Usage](./basic.md#create-client) for more details.
```py
client = Client()
```

---

## Create SQL instance
See [SQL Reference](/reference/database/sql/#sql) for more details.
```py
sql = SQL (
    ConnectionConfig (
        Driver = "{ODBC Driver 17 for SQL Server}",
        Server = "localhost",
        Database = "DbWhatsApp",
        Trusted_Connection = True,
        Encrypt = False,
        LongAsMax = True,
        APP = "whatsapp_py module test",
    ),
    autocommit = True,
)
```

---

## Register event handlers
See [Using with events](./events.md#register-event-handlers) for more details.
```py
# Save rows that are in progress to prevent duplicate tasks
progressing_rows = {}
```
```py
@client.on(ClientEvent.UPDATE)
def on_update():
    # Get all rows that are not completed
    result = sql.execute("""
        SELECT * FROM Tasks
        WHERE msg_id IS NULL AND error IS NULL
    """)
    
    # Iterate through rows
    for row in result.rows_dict:

        id = row['id']

        # Skip if already in progress
        if id in progressing_rows:
            continue

        # Add to progressing rows
        progressing_rows[id] = row
        
        # Get datas from row
        phone_number = row['phone_number']
        text_content = row['text_content']
        file_path = row['file_path']
        media_path = row['media_path']
        start_at = row['start_at']

        try:
            # Create chat
            chat = client.new_chat(phone_number)

            # Send message with task id as nonce
            chat.send_message(
                nonce = id, 
                content = text_content, 
                file = file_path,
                media = media_path,
                at_time = start_at,
            )

        except Exception as e:
            print(f">> Client Error:", e)

            # Update row with error message
            sql.execute("""
                UPDATE Tasks
                SET
                    error = ?
                WHERE id = ?
            """, str(e), id)

        else:
            print(f">> SQL message {id} added to task queue")
```
```py
@client.on(ClientEvent.TASK_COMPLETED)
def on_task_completed(task: MessageTask):
    # Skip if not in progressing rows
    if task.message.nonce not in progressing_rows:
        return

    print(">> Client task completed", task)

    # Create variables to store sql results
    res: SqlResult = None
    res2: SqlResult = None

    try:
        # Check if task has error
        if task.message.error is not None:
            print(f">> Message Error:", task.message.error)

            # Update row with error message
            res = sql.execute(
                """
                    UPDATE Tasks
                    SET
                        error = ?
                    WHERE id = ?
                """, 
                task.message.error, 
                task.message.nonce
            )
        else:
            # Insert message to database
            res = sql.execute(
                """
                    INSERT INTO Messages (id, sent_at, status_id)
                    VALUES (?, ?, ?)
                """, 
                task.message.id, 
                task.message.time, 
                task.message.status_w_index + 1
            )

            # Update task with message id
            res2 = sql.execute(
                """
                    UPDATE Tasks
                    SET 
                        msg_id = ?
                    WHERE id = ?
                """, 
                task.message.id, 
                task.message.nonce
            )

        # Remove from progressing rows
        progressing_rows.pop(task.message.nonce, None)

        # Print sql results as json (for debugging)
        import json
        str_res = json.dumps(res._asdict(), indent=2, default=str)
        print(f">> SQL Result:", str_res)

        if res2 is not None:
            str_res = json.dumps(res2._asdict(), indent=2, default=str)
            print(f">> SQL Result 2:", str_res)

    except Exception as e:
        print(f">> SQL Error:", e)
```
