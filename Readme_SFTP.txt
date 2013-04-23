Assumptions:
Python 3.3.1 is installed.

Command to Enter to Run Server:
Simple_ftp_server <port#> <file-name> <p>

Command to Enter to Run Client:
Simple_ftp_client <server-host-name> <server-port#> <file-name> <N> <MSS> 

Steps to Run:
1. Go the folder containing the "server.py" file from the command line
2. Enter the command to run server provided above with appropraite values for fields enclosed in "<>".
3. For client side, the file-name that you enter should be present in the folder containing the client script.
4. Run the server first and then the client. Wait till you receive the "End of Program" line at the client which signals the end of program.
5. Repeat the same steps for Selective Repeat with the script files provided in the respective folder.

Note#1: The execution at server and client won't return to the command prompt till ctrl+c is entered.
Note#2: For Selective Repeat ARQ protocol, "END" packet is being sent to inform the receiver that the data has been transmitted so that it can create a file and copy the data from the buffer into the file.