#!/usr/bin/env python3

from client import Client
from tkinter import *
import platform

# input the directory to store the files here
DIR = "/home/jamac/chat"

def message_in(event):
    msg = entry.get()
    if len(msg) > 0:
        chatClient.send_message(msg)

    entry.delete(0, END)

def show_messages():
    events = chatClient.get_events()
    for event in events:
        string = ""
        if event["type"] == "message":
            string = "<" + event["user"] + "> " + event["text"]
        if event["type"] == "join":
            string = "<<" + event["user"] + " has joined>>"
        if event["type"] == "quit":
            string = "<<" + event["user"] + " has left>>"
        if event["type"] == "error":
            string = "<<ERROR: " + event["text"] + " >>"

        if string:
            text.config(state=NORMAL)
            text.insert(END, string + "\n")
            text.see("end")
            text.config(state=DISABLED)

    root.after(100, show_messages)

user = input("username: ")
chatClient = Client(DIR, user)

monoFont = ("Courier New" if platform.system() == "Windows" else "Monospace", 11)

root = Tk()

text = Text(root, height=26, width=80)
text.config(state=DISABLED, font=monoFont)
text.pack(padx=10, pady=10)

entry = Entry(root, width=80)
entry.config(font=monoFont)
entry.bind("<Return>", message_in)
entry.pack(padx=10, pady=10, side=LEFT)

show_messages()
chatClient.start()
mainloop()
chatClient.end()

