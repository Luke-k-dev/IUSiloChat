
# Back-End Documentation

## Global Functions

```
shift(val)
    Takes a seed value and returns a pseudo-random integer in [0, 256)
    args: number val

obfuscate(data)
    Takes any object and converts it into an obfuscated string.
    args: any type data
    returns: string

deobfuscate(obj)
    Deobfuscates an obfuscated string
    args: string obj
    returns: any type
```

## Classes

### ReadFile

```
ReadFile(filepath)
    args: string filepath

read()
    Reads all events from the file
    args: int num
    returns: list
```

### WriteFile

```
WriteFile(filepath)
    args: string filepath

write(events)
    Writes every event in events to the file.
    args: list events
```

### Client

```
Client(directory, username)
    args: string directory, string username

start(rate = 0.1, get_old_events = False)
    Starts the client on a new thread. The value of rate determines the amount of time between each read/write, in seconds. If get_old_events is set to True, the client will put every stored event into the event queue upon startup. Otherwise, it will only put events that occur after startup.
    keyword args: number rate, bool get_old_events

end()
    Ends the client thread.

run()
    The function called by start() on a new thread.

send_event(event)
    Sends the given event.
    args: dict event

send_message(text)
    Wrapper function for send_event() to send a message event with the given message text and username.

get_events(num = 0)
    Returns a list containing all of the new events since the last call, with an optional maximum num.
    keyword args: int num
    returns: list
```

