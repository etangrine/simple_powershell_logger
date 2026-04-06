from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
# from discord_webhook import DiscordWebhook
import requests
import subprocess
from collections import Counter
import os
import time
import socket
#todo: add 
# 
#  to the powershell profile, probably with ansible
URL = "http://100.105.239.51:5000"
hostname = socket.gethostname()
class FileChecking(FileSystemEventHandler):
    def __init__(self):
        # print("init")
        super()
        path_result = subprocess.run("powershell.exe (Get-PSReadlineOption).HistorySavePath", shell=True, capture_output=True).stdout.decode('utf-8').strip()
        # raw_path = repr(path_result)[1:-1]
        path_as_list = path_result.split("\\")
        dir = "\\".join(path_as_list[0:-1])
        print(dir)
        # print(path_result.split("\\"))
        # print(raw_path)
        # self.static_path = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
        self.static_path = path_result
        # print(self.static_path) 
        # self.static_dir = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine")
        self.static_dir = dir
        self.content = ""
        with open(self.static_path,"r", encoding="utf-8",errors="replace") as ps_con_history:
            self.content = ps_con_history.readlines()
        
    def on_modified(self, event: FileSystemEvent):
        print("file event:")
        if event.is_directory:
            return
        norm_path = os.path.normpath(event.src_path)
        if norm_path == self.static_path:
            time.sleep(0.1)
            try:
                with open(self.static_path,"r", encoding="utf-8",errors="replace") as ps_con_history:
                    current_content = ps_con_history.readlines()
                    diff = list((Counter(current_content)-Counter(self.content)).elements())
                    self.content = current_content
                    if command:
                        command = str(diff)[2:-4].strip()
                        json = {"command":command,"hostname":hostname}
                        endpoint = "log"
                        post_log(endpoint, json)
                        print(str(diff)[2:-4].strip())
            except PermissionError:
                print("skipping as file is likley locked")
def post_log(endpoint, payload):
    try:
        r = requests.post(f"{URL}/{endpoint}", json=payload, timeout=5)
        
        # print(response)

        # r = requests.post(f"{URL}", json=payload, timeout=5)
        return r.json()
    except Exception:
        return {}
def main():
    print(hostname)
    checker = FileChecking()
    observer = Observer()
    observer.schedule(checker, checker.static_dir)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:#probably could be better
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()