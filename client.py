import os, time, json, glob, threading, queue, math, pathlib

# filename prefix
FILE_PREFIX = "chat-v1-user-"
# maximum number of events to store before removing old ones
EVENT_RETENTION = 50

def shift(val):
                # simple PRNG
    return int((1337 * math.tan(val) % 1) * 256)

def obfuscate(data):
    obj = list(json.dumps(data).encode("utf-8"))
    for i in range(len(obj)):
        obj[i] = (obj[i] + shift(i)) % 256

    return bytes(obj)

def deobfuscate(obj):
    data = list(obj)
    for i in range(len(data)):
        data[i] = (data[i] - shift(i)) % 256

    try:
        return json.loads(bytes(data).decode("utf-8"))
    except json.decoder.JSONDecodeError:
        return False

class ReadFile:

    def __init__(self, filepath):
        self.fp = filepath

    def read(self):
        if os.path.isfile(self.fp):
            allEvents = False
            tries = 0
            while allEvents == False and tries < 10:
                tries += 1
                with open(self.fp, "rb") as f:
                    allEvents = deobfuscate(f.read())

            if allEvents == False:
                return [{"type": "error", "ts": time.time(), "text": "Couldn't read file contents. Path: '" + self.fp + "'"},]

            return allEvents

        else:
            return [{"type": "error", "ts": time.time(), "text": "File not found."},]

class WriteFile:

    def __init__(self, filepath):
        self.fp = filepath
        if not os.path.isfile(self.fp):
            with open(self.fp, "wb") as f:
                f.write(obfuscate([]))

    def write(self, events):
        if os.path.isfile(self.fp):
            with open(self.fp, "rb") as f:
                allEvents = deobfuscate(f.read())

            allEvents += events
        else:
            allEvents = events

        if len(allEvents) > EVENT_RETENTION:
            allEvents = allEvents[0 - EVENT_RETENTION:]

        with open(self.fp, "wb") as f:
            f.write(obfuscate(allEvents))

        os.chmod(self.fp, 0o644) 

class Client:

    def __init__(self, directory, username):
        self.user = username
        self.dir = directory
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        self.wFile = WriteFile(os.path.join(self.dir, FILE_PREFIX + username))
        self.wQueue = queue.Queue()
        self.rQueue = queue.Queue()
        self.thread = threading.Thread(target=self.run)
        self.threadStop = threading.Event()
        self.lastEventTs = 0

    def start(self, rate = 0.1, get_old_events = False):
        self.rate = rate
        self.threadStop.clear()
        self.thread.start()
        self.lastEventTs = 0 if get_old_events else time.time()
        self.send_event({"type": "join", "ts": time.time(), "user": self.user})

    def end(self):
        self.send_event({"type": "quit", "ts": time.time(), "user": self.user})
        time.sleep(self.rate * 1.5)
        self.threadStop.set()
        self.thread.join()

    def run(self):
        readStartIndex = 0
        while not self.threadStop.is_set():
            time.sleep(self.rate)

            # writing
            wEvents = []
            while not self.wQueue.empty():
                wEvents.append(self.wQueue.get())

            if len(wEvents) > 0:
                self.wFile.write(wEvents)

            self.rFiles = [ReadFile(fp) for fp in glob.glob(os.path.join(self.dir, FILE_PREFIX + "*"))]
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

    def send_message(self, text):
        self.send_event({"type": "message", "ts": time.time(), "user": self.user, "text": text})
        
    def get_events(self, num = 0):
        events = []
        while not self.rQueue.empty() and (num == 0 or len(events) < num):
            events.append(self.rQueue.get())
        
        return sorted(events, key=lambda x: x["ts"])

