import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FolderWatcher:
    def __init__(self, folder_path, on_change_callback):
        self.folder_path = folder_path
        self.on_change = on_change_callback
        self.observer = None
        self._debounce_timer = None
        self._lock = threading.Lock()

    def _debounced_callback(self):
        """Debounce rapid file system changes."""
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(1.0, self.on_change)
            self._debounce_timer.start()

    def start(self):
        handler = _ChangeHandler(self._debounced_callback)
        self.observer = Observer()
        self.observer.schedule(handler, self.folder_path, recursive=True)
        self.observer.daemon = True
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()

    def update_folder(self, new_path):
        self.stop()
        self.folder_path = new_path
        self.start()


class _ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        self.callback()
