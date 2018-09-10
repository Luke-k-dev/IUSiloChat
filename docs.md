#Back-End Documentation

##Global Functions

    ```
    obfuscate(data)
        Takes any object and converts it into an obfuscated string.
        args: any type data
        returns: string

    deobfuscate(obj)
        Deobfuscates an obfuscated string
        args: string obj
        returns: any type
    ```

##Classes

   ###ReadFile

        ```
        ReadFile(filepath)
            args: string filepath

        read()
            Reads all events from the file
            args: int num
            returns: list
        ```

    ###WriteFile

        ```
        WriteFile(filepath)
            args: string filepath

        write(events)
            Writes every event in events to the file.
            args: list events
        ```

    ###Client

        ```
        Client(username)
            args: string username

        start()
            Starts the client on a new thread.

        end()
            Ends the client thread.

        run()
            The function called by start() on a new thread.

        send_event(event)
            Sends the given event.
            args: dict event

        send_message(user, text)
            Wrapper function for send_event() to send a message event with the given message text and username.
            
        get_events(num = 0)
            Returns a list containing all of the new events since the last call, with an optional maximum num.
            keyword args: int num
            returns: list
        ```

