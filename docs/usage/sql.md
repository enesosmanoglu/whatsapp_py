# Using with SQL Database

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
