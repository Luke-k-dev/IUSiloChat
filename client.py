#!/usr/bin/env python3

import os, time, json, glob, pickle, threading, queue

# file directory (end with a slash so I don't have to use os.path.join everywhere)
DIR = "/tmp/" 
# filename prefix
FILE_PREFIX = "chat-v1-user-"
# maximum number of events to store before removing old ones
EVENT_RETENTION = 50
# obfuscation value
OBF_SHIFT = 34

def obfuscate(data):
    obj = list(json.dumps(data))
    for i in range(len(obj)):
        obj[i] = str(ord(obj[i]) + OBF_SHIFT) + "|"

    return "".join(obj)[:-1]

def deobfuscate(obj):
    obj = obj.split("|")
    for i in range(len(obj)):
        obj[i] = chr(int(obj[i]) - OBF_SHIFT)

    return json.loads("".join(obj))

class ReadFile:

    def __init__(self, filepath):
        self.fp = path

    def read(self):
        if os.path.isfile(self.fp):
            with open(self.fp, "r") as f:
                allEvents = deobfuscate(f.read())

            return allEvents

        else:
            return [{"type": "error", "ts": time.time(), "text": "file not found"},]

class WriteFile:

    def __init__(self, filepath):
        self.fp = filepath
        if not os.path.isfile(self.fp):
            with open(self.fp, "w") as f:
                f.write(obfuscate([]))

    def write(self, events):
        if os.path.isfile(self.fp):
            with open(self.fp, "r") as f:
                allEvents = deobfuscate(f.read())

            allEvents += events
        else:
            allEvents = events

        if len(allEvents) > EVENT_RETENTION:
            allEvents = allEvents[0 - EVENT_RETENTION:]

        with open(self.fp, "w") as f:
            f.write(obfuscate(allEvents))

        os.chmod(self.fp, 0o644) 

class Client:

    def __init__(self, username):
        self.user = username
        self.wFile = WriteFile(DIR + FILE_PREFIX + username)
        self.rFiles = glob.glob(DIR + FILE_PREFIX + "*")
        self.wQueue = queue.Queue()
        self.rQueue = queue.Queue()
        self.thread = threading.Thread(target=self.run)
        self.threadStop = threading.Event()
        self.lastEventTs = 0

    def start(self):
        self.threadStop.clear()
        self.thread.start()
        self.lastEventTs = time.time()
        self.send_event({"type": "join", "ts": time.time(), "user": self.user})

    def end(self):
        self.send_event({"type": "join", "ts": time.time(), "user": self.user})
        time.sleep(1)
        self.threadStop.set()
        self.thread.join()

    def run(self):
        readStartIndex = 0
        while not self.threadStop.is_set():
            time.sleep(1)

            # writing
            wEvents = []
            while not self.wQueue.empty():
                wEvents.append(self.wQueue.get())

            if len(wEvents) > 0:
                self.wFile.write(wEvents)

            self.rFiles = glob.glob(DIR + FILE_PREFIX + "*")
            allEvents = []
            for rFile in self.rFiles:
                allEvents += rFile.read()

            allEvents.sort(key=lambda x: x["ts"])
            if readStartIndex >= len(allEvents): readStartIndex = 0
            allEvents = allEvents[readStartIndex:]
            for event in allEvents:
                if event["ts"] > self.lastEventTs:
                    self.rQueue.put(event)
                    self.lastEventTs = event["ts"]

                readStartIndex += 1

    def send_event(self, event):
        self.wQueue.put(event)
        self.rQueue.put(event)

    def send_message(self, user, text)
        self.send_event({"type": "message", "ts": time.time(), "user": user, "text": text})
        
    def get_events(self, num = 0):
        events = []
        while not self.rQueue.empty() and num > 0 and len(events) < num:
            events.append(self.rQueue.get())
        
        return sorted(events, key=lambda x: x["ts"])

