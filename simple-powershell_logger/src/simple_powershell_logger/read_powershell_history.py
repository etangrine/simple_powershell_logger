from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
# from discord_webhook import DiscordWebhook
import requests
import subprocess
from collections import Counter
from pathlib import Path
import os
import time
import socket
import getpass
import base64
import json

from client_utils import encrypt_payload
# add 
# certin powershell history settings 
#  to the powershell profile, probably with ansible
URL = "http://100.95.68.26:5000"
hostname = socket.gethostname()
username = getpass.getuser()
#example PSK
PSK = "0feNcM1h9Cx2mWAopX6Rq8WZ9sHUvQG4TthfgCL2lk0="

# other_logger_paths = ""

class FileChecking(FileSystemEventHandler):
    def __init__(self):# think about having a check for new history files 
        # print("init")
        super()
        
        self.content = ""
       

        self.history_dirs = get_history_paths(is_dir=True)
        self.history_paths = get_history_paths()
        print(self.history_paths)
        self.history_files = {}
        self.file_positions = {}
        for path in self.history_paths:

            try:
                self.file_positions[path]= os.path.getsize(path)
                # print(self.file_positions[path])
            except Exception as e:
                print(f"* Error getting size for {path}: {e}")
                self.file_positions[path]=0

            with open(path,"r", encoding="utf-8",errors="replace") as user_con_history:# unessacary? 
                self.history_files[path] = user_con_history.readlines()

        
        
        
    def on_modified(self, event: FileSystemEvent):
        print("file event:")
        norm_path = os.path.normpath(event.src_path)
        # if normpath 
        if event.is_directory:
            return
        
        print(norm_path)
        # if norm_path == self.static_path:
        # could check if path is expected to be a history file?
        if norm_path in self.history_paths:
            time.sleep(0.1)
            try:
                prev_pos= self.file_positions.get(norm_path,0)
                current_size = os.path.getsize(norm_path) 
                if current_size > prev_pos:
                    
                    with open(norm_path,"r", encoding="utf-8",errors="replace") as user_con_history:
                        
                        user_con_history.seek(prev_pos)
                        new_data = user_con_history.read()
                        self.file_positions[norm_path] = user_con_history.tell()
                       
                        diff = [line.strip() for line in new_data.splitlines() if line.strip()]
                       
                        if diff:#doesn't do that much after testing
                            batched_cmds = ", ".join(diff)

                            username = str(norm_path.split("\\")[2])
                            # print(f"Command from {username}: {command}")
                            json_payload = {"command": batched_cmds, "hostname": hostname, "username": username}
                            endpoint = "log"
                            post_log(endpoint, json_payload)
                elif current_size < prev_pos:
                    print(f"[*] History file truncated or cleared for {norm_path}. Resetting position.")
                    self.file_positions[norm_path] = current_size
            except PermissionError: 
                print("skipping as file is likley locked")
            except Exception as e:
                print(f"[-] Unexpected error tracking file changes: {e}")

def get_history_paths(is_dir=False):
    
    base_dir = os.environ.get("SystemDrive") + r"\Users"
    print(base_dir)
    # could dynamically generate this
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
        encrypted_string = encrypt_payload(payload)#will need to format the object
        encrypted_payload = {"d":encrypted_string}
        # r = requests.post(f"{URL}/{endpoint}", json=payload, timeout=5)
        r = requests.post(f"{URL}/{endpoint}", json=encrypted_payload, timeout=5)

       
        return r.text
    except Exception as e:
        print(f"Error: {e}")
#should move these to seprate files eventually, will lead to changes in playbook and maybe structure
def _get_key() -> bytes:
    return base64.b64decode(PSK)

def main():
    # print(get_history_paths())
    print(hostname)
    checker = FileChecking()
    observer = Observer()

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