# simple_powershell_logger
A simple tool meant to log the Powershell Command history. 

It has parts for the server and logger(client) and for the deployment

The client and server, located in simple-powershell_logger\src\simple_powershell_logger are python scripts meant to be running on the client and server. 

Dependiencies: Python 3.12+, Poetry, and the Python libraries of flask, watchdog, requests, discord-webhook, and nuitka if an executable is being deployed. Also requires ansible 

Hardcoded elements: the server IP, the monitored file_path's directory, and discord webhook url
Note: PSReadline needs to be active and configured for this tool to work

The client from read_powershell_history.py:
* It starts a observer with FileChecking derived from the FileSystemEventHandler class and gets the hostnmae , 
* The FileChecking class finds the directories of the logfiles for the different users on inititalization
* On modification to the logfile the script finds different line(s) in the current log file from the stored log file
* It then updates the current log file 
* It then sends a post request to the server with the command and the hostname

The observer then starts and then the program loops.

There also is an executable that can be generated:
* To create it first initalize the enviroment with poetry (poetry install, etc)
* In the directory with read_powershell_history.py run python -m poetry run python -m nuitka --onefile --windows-console-mode=disable --include-module=watchdog.observers.read_directory_changes  read_powershell_history.py

The server (log_server.py) is a basic flask server that
* has has an endpoint that the client sends to
* extracts the command and the hostname from the post request
* send the data to a discord server (right now its a test server) using a discord webhook
* It is meant to retry opon getting rate limited

The deployment for the server (with the log_server ansible playbook) goes something like:
* initalize the enviroment (system packages and python packages with poetry) along with the files
* Then starting or restarting a flask service

The deployment on the windows client (with the deploy_py_logger ansible playbook) goes like:
* Installing pyton on the machine
* copying the file and executing the file (using async and poll for now)

To deploy the executable:
* Generate the executable 
* run the playbook deploy_exe_logger.yml instead of deploy_py_logger.yml

