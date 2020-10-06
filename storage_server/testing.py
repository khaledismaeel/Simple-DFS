import os

with os.scandir() as dir_entries:
    for entry in dir_entries:
        print(entry)
        info = entry.stat()
        print(info.st_mtime)