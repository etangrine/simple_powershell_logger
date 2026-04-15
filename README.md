# simple_powershell_logger
A simple tool meant to log passwords to powershell

It has parts for the server and logger(client) and for the deployment

The client and server, located in simple-powershell_logger\src\simple_powershell_logger are python scripts meant to be running on the client and server. 

The client read_powershell_history.py:
* It starts a observer with FileChecking derived from the FileSystemEventHandler class, 
* The FileChecking class finds the directory of the logfile on inititalization
* On modification to the logfile the script finds different line(s) in the current log file from the stored log file
* It then updates the current log file
* It then sends a post request to the server with the command and the hostname

The observer then starts and then the program loops.

The server (log_server.py) is a basic flask server that
* has has an endpoint that the client sends to
* extracts the command and the hostname from the post request
* send the data to a discord server (right now its a test server) using a discord webhook
* It is meant to retry opon getting rate limited

The deployment for the server (with the log_server ansible playbook) goes something like:
* initalize the enviroment (system packages and python packages with poetry) along with the files
* Then starting a flask service

The deployment on the windows client (with the deploy_py_logger ansible playbook) goes like:
* Installing pyton on the machine
* copying the file and executing the file (using async and poll for now)



