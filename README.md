# simple_powershell_logger
A simple tool meant to log the Powershell Command history. 

It has parts for the server and logger(client) and for the deployment

The client and server, located in simple-powershell_logger\src\simple_powershell_logger, are python scripts meant to be running on the client and server. 

Dependiencies: Python 3.12+, Poetry, and the Python libraries of flask, watchdog, requests, discord-webhook,Cryptography and nuitka if an executable is being deployed.  Also requires ansible 

Hardcoded elements: the server IP, the monitored file_path's directory, inventory ips and some values
Note: PSReadline needs to be active and configured for this tool to work

The client from read_powershell_history.py:
* It starts a observer with FileChecking derived from the FileSystemEventHandler class and gets the hostnmae , 
* The FileChecking class finds the directories of the logfiles for the different users on inititalization
* On modification to the logfile the script finds new data after the current stream position
* It then updates the current stream position to the end of the file
* It then encrypts the payload with a PSK sends a post request to the server with the command and the hostname

The observer then starts and then the program loops.

There also is an executable that can be generated:
* To create it first initalize the enviroment with poetry (poetry install, etc)
* In the directory with read_powershell_history.py run python -m poetry run python -m nuitka --onefile --windows-console-mode=disable --include-module=watchdog.observers.read_directory_changes  read_powershell_history.py

The server (log_server.py) is a server which uses gunicorn and nginx that
* has has an endpoint that the client sends to
* passes requests from the server port to a different port
* decrypts the payload from the request with a PSK
* extracts the command and the hostname from the post request
* batches the commands until the stored commands reach a certin size or a certin amount of time has passed (3 seconds)
* send the data to a discord server (right now its a test server) using a discord webhook 
* with the webhook url inserted through a template file
* It is meant to retry opon getting rate limited

The deployment for the server (with the log_server ansible playbook and uses a .j2 template) goes something like:
* configure the ssh key pair and ip of the server in the inventory file
* initalize the enviroment (system packages and python packages with poetry) along with the files (most of the used ones are from templates)
* Then starting or restarting the service for the server

The deployment on the windows client (with the deploy_py_logger ansible playbook) goes like:
* configure credentials and ips on the inventory file
* Installing pyton on the machine
* copying the file and executing the file (using async and poll for now)

### Note that the deploy_py_logger no longer works because the functionality is in multiple files

To deploy the executable:
* Generate the executable with for example nuitka (example:python -m poetry run python -m nuitka --onefile --windows-console-mode=disable  read_powershell_history.py)
* run the playbook deploy_exe_logger.yml instead of deploy_py_logger.yml
The executable is deployed with a scheduled task 



