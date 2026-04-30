from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
# from discord_webhook import DiscordWebhook
import requests
import subprocess
from collections import Counter
import os
import time
import socket
import getpass
# import difflib
# add 
# certin powershell history settings 
#  to the powershell profile, probably with ansible
URL = "http://100.95.68.26:5000"
hostname = socket.gethostname()
username = getpass.getuser()
class FileChecking(FileSystemEventHandler):
    def __init__(self):
        # print("init")
        super()
        path_result = subprocess.run("powershell.exe (Get-PSReadlineOption).HistorySavePath", shell=True, capture_output=True).stdout.decode('utf-8').strip()
        # raw_path = repr(path_result)[1:-1]
        path_as_list = path_result.split("\\")
        dir = "\\".join(path_as_list[0:-1])
        # print(dir)
        # print(path_result.split("\\"))
        # print(raw_path)
        # self.static_path = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
        self.static_path = path_result
        # print(self.static_path) 
        # self.static_dir = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine")
        self.static_dir = dir
        self.content = ""
        # self.pos = None
        with open(self.static_path,"r", encoding="utf-8",errors="replace") as ps_con_history:
            self.content = ps_con_history.readlines()
            # ps_con_history.seek(0,2)
            # self.pos = ps_con_history.tell()
            # self.content = set()

        self.history_dirs = get_history_paths(is_dir=True)
        self.history_paths = get_history_paths()
        print(self.history_paths)
        self.history_files = {}
        for path in self.history_paths:
            with open(path,"r", encoding="utf-8",errors="replace") as user_con_history:
                self.history_files[path] = user_con_history.readlines()

        
    def on_modified(self, event: FileSystemEvent):
        print("file event:")
        if event.is_directory:
            return
        norm_path = os.path.normpath(event.src_path)
        print(norm_path)
        # if norm_path == self.static_path:
        if norm_path in self.history_paths:
            time.sleep(0.1)
            try:
                with open(norm_path,"r", encoding="utf-8",errors="replace") as user_con_history:
                    current_content = user_con_history.readlines()
                    # print(f"current content {current_content}")
                    prev_content = self.history_files[norm_path]
                    # print(f"prev content: {prev_content}")
                    #this could be more efficent especially if the history file is large
                    # diff = list((Counter(current_content)-Counter(self.content)).elements())#think about what happens if the log file is full
                    diff = list((Counter(current_content)-Counter(prev_content)).elements())
                    self.history_files[norm_path] = current_content

                    # ps_con_history.seek(self.pos)
                    # print(str(ps_con_history.readlines())[2:-4].strip())
                    # ps_con_history.seek(0,2)
                    # self.pos = ps_con_history.tell()
                    
                    command = str(diff)[2:-4].strip()
                    if command:
                        # username = getpass.getuser()
                        username = str(norm_path.split("\\")[2])
                        print(username)
                        json = {"command":command,"hostname":hostname, "username":username}
                        endpoint = "log"
                        post_log(endpoint, json)
                        print(str(diff)[2:-4].strip())
            except PermissionError:
                print("skipping as file is likley locked")

def get_history_paths(is_dir=False):
    # cmd = "powershell -Command \"Get-LocalUser | Select-Object -ExpandProperty Name\""
    # cmd = "powershell -Command \"Get-ADUser | Select-Object -ExpandProperty Name\""

    # output = subprocess.check_output(cmd, shell=True).decode().splitlines()
    # print(output) 
    #could try to get the paths a bit more dynamically
    base_dir = r"C:\Users"
    relative_history_path = os.path.join(
            "AppData", "Roaming", "Microsoft", "Windows", 
            "PowerShell", "PSReadLine", "ConsoleHost_history.txt"
        )
    if is_dir: 
        relative_history_path = os.path.join(
            "AppData", "Roaming", "Microsoft", "Windows", 
            "PowerShell", "PSReadLine"
        )
    history_paths = []

    
    user_folders = os.listdir(base_dir)

    for folder in user_folders:
        try:
            full_user_path = os.path.join(base_dir,folder)
            if os.path.isdir(full_user_path):
                target_file = os.path.join(full_user_path, relative_history_path)

                if os.path.exists(target_file):
                    history_paths.append(target_file)
        except PermissionError:
            print("Please run this script with proper permissions")

    return history_paths

def post_log(endpoint, payload):
    try:
        r = requests.post(f"{URL}/{endpoint}", json=payload, timeout=5)
        
        # print(response)

        # r = requests.post(f"{URL}", json=payload, timeout=5)
        return r.json()
    except Exception:
        return {}
def main():
    # print(get_history_paths())
    print(hostname)
    checker = FileChecking()
    observer = Observer()
    # observer.schedule(checker, checker.static_dir)
    for dir in checker.history_dirs:
        observer.schedule(checker, dir)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:#probably could be better
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()