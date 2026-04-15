# simple_powershell_logger
A simple tool meant to log passwords to powershell

It has parts for the server and logger(client) and for the deployment

The client and server, located in simple-powershell_logger\src\simple_powershell_logger are python scripts meant to be running on the client and server. 

The client read_powershell_history.py:
* It starts a observer with a modified FileSystemEventHandler, FileChecking
* The FileChecking class finds the directory of the logfile on inititalization
* On modification to the logfile the script finds different line(s) in the current log file from the stored log file
* It then updates the current log file
* It then sends a post request to the server 

The observer then starts and then the program loops.

