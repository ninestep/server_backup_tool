from watchdog.observers import Observer
from watchdog.events import *
import time
import os


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if not event.is_directory:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if not event.is_directory:
            print("file created:{0}".format(os.path.abspath(event.src_path)))

    def on_deleted(self, event):
        if not event.is_directory:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            print("file modified:{0}".format(event.src_path))


if __name__ == "__main__":
    observer = Observer()
    dirs = [r'/program/test1', r'test2']
    for dir in dirs:
        event_handler = FileEventHandler()
        observer.schedule(event_handler, dir, True)
    observer.start()
    observer.join()
    print(input("input any..."))