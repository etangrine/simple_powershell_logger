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
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives import padding
# from cryptography.hazmat.backends import default_backend
from client_utils import encrypt_payload
# import difflib
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
    def __init__(self):
        # print("init")
        super()
        # path_result = subprocess.run("powershell.exe (Get-PSReadlineOption).HistorySavePath", shell=True, capture_output=True).stdout.decode('utf-8').strip()
        # raw_path = repr(path_result)[1:-1]
        # path_as_list = path_result.split("\\")
        # dir = "\\".join(path_as_list[0:-1])
        # print(dir)
        # print(path_result.split("\\"))
        # print(raw_path)
        # self.static_path = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
        # self.static_path = path_result
        # print(self.static_path) 
        # self.static_dir = os.path.normpath(r"C:\Users\ericd\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine")
        # self.static_dir = dir
        self.content = ""
        # self.pos = None
        # with open(self.static_path,"r", encoding="utf-8",errors="replace") as ps_con_history:
        #     self.content = ps_con_history.readlines()
            # ps_con_history.seek(0,2)
            # self.pos = ps_con_history.tell()
            # self.content = set()

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
    def on_moved(self, event: FileSystemEvent):
        if event.is_directory:
            source_path = Path(os.path.normpath(event.src_path))
            for path in self.history_paths:
                path = Path(path)
                is_sub = path.is_relative_to(source_path)
                if is_sub:
                    # diff the path with the new destination path
                    trailing_path = path.relative_to(source_path)
                    new_path = Path(os.path.normpath(event.dest_path))
                    # check if this works
                    path = new_path / trailing_path 
        pass
        
        # if event.is_directory:
            # check if its history paths
            # change history paths
        # (its a file), change the file the history path is pointing to. 
        
    def on_modified(self, event: FileSystemEvent):
        print("file event:")
        norm_path = os.path.normpath(event.src_path)
        # if normpath 
        if event.is_directory:
            return
        
        print(norm_path)
        # if norm_path == self.static_path:
        if norm_path in self.history_paths:
            time.sleep(0.1)
            try:
                prev_pos= self.file_positions.get(norm_path,0)
                current_size = os.path.getsize(norm_path) 
                if current_size > prev_pos:
                    
                    with open(norm_path,"r", encoding="utf-8",errors="replace") as user_con_history:
                        # current_content = user_con_history.readlines()
                        # print(f"current content {current_content}")
                        # prev_content = self.history_files[norm_path]
                        # print(f"prev content: {prev_content}")
                        #this could be more efficent especially if the history file is large
                        # diff = list((Counter(current_content)-Counter(self.content)).elements())#think about what happens if the log file is full
                        # diff = list((Counter(current_content)-Counter(prev_content)).elements())
                        # self.history_files[norm_path] = current_content

                        # ps_con_history.seek(self.pos)
                        # print(str(ps_con_history.readlines())[2:-4].strip())
                        # ps_con_history.seek(0,2)
                        # self.pos = ps_con_history.tell()
                        user_con_history.seek(prev_pos)
                        new_data = user_con_history.read()
                        self.file_positions[norm_path] = user_con_history.tell()
                        # command = str(diff)[2:-4].strip()

                        # cleaned_commands = [cmd.strip() for cmd in diff if cmd.strip()]
                        # command = "\n".join(cleaned_commands)

                        # if command:
                        #     # username = getpass.getuser()
                        #     username = str(norm_path.split("\\")[2])
                        #     print(username)
                        #     json_payload = {"command":command,"hostname":hostname, "username":username}
                        #     endpoint = "log"
                            # post_log(endpoint, json_payload)
                            # print(str(diff)[2:-4].strip())
                        diff = [line.strip() for line in new_data.splitlines() if line.strip()]
                        # command = "\n".join(cleaned_commands)
                        # for command in diff:
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
    # cmd = "powershell -Command \"Get-LocalUser | Select-Object -ExpandProperty Name\""
    # cmd = "powershell -Command \"Get-ADUser | Select-Object -ExpandProperty Name\""

    # output = subprocess.check_output(cmd, shell=True).decode().splitlines()
    # print(output) 
    #could try to get the paths a bit more dynamically
    # base_dir = r"C:\Users"
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

        # r= requests.post(f"{URL}/{endpoint}", json=encrypt_payload(payload), timeout=5)
        # print(response)

        # r = requests.post(f"{URL}", json=payload, timeout=5)
        return r.text
    except Exception as e:
        print(f"Error: {e}")
#should move these to seprate files eventually, will lead to changes in playbook and maybe structure
def _get_key() -> bytes:
    return base64.b64decode(PSK)

# def encrypt_payload(data: dict) -> str:

#     plaintext = json.dumps(data).encode("utf-8")

#     # PKCS7 padding
#     padder = padding.PKCS7(128).padder()
#     padded = padder.update(plaintext) + padder.finalize()

#     iv = os.urandom(16)
#     cipher = Cipher(algorithms.AES(_get_key()), modes.CBC(iv), backend=default_backend())
#     encryptor = cipher.encryptor()
#     ciphertext = encryptor.update(padded) + encryptor.finalize()

#     return base64.b64encode(iv + ciphertext).decode("ascii")

def main():
    # print(get_history_paths())
    print(hostname)
    checker = FileChecking()
    observer = Observer()
    # observer.schedule(checker, checker.static_dir)
    # check if other instances are running
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