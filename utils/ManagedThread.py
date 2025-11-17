import threading
import time

class ManagedThread:
    def __init__(self, target, name):
        self.thread = threading.Thread(target=target, name=name)
        self.start_time = time.time()
        self.status = "running"

    def is_alive(self):
        return self.thread.is_alive()

    def elapsed(self):
        return time.time() - self.start_time

    def start(self):
        self.thread.start()

