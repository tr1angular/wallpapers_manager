from watchdog.events import FileSystemEventHandler
from functools import partial


class WallpapersHandler(FileSystemEventHandler):
    def __init__(self, perform: partial):
        super().__init__()
        self.perform = perform

    def on_any_event(self, event):
        self.perform()
