from socket import *
from sys import argv
import time

MAXLINE = 1024
serverName = "127.0.0.1"
filename = "file_receive.txt"
hostname = ""

if len(argv)>=2:
    MAXLINE = int(argv[1])
if len(argv)>=3:
    serverName = argv[2]
if len(argv)>=4:
    hostname = argv[3]
    filename = "file_receive_" + hostname + ".txt"

START_TIME = time.time()

serverPort = 2683
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

# To speed up, skip the process of saving it to the memory first.
with open(filename,"wb") as f:
    for i in range(MAXLINE/1024):
        f.write(clientSocket.recv(1024).decode())

END_TIME = time.time()

clientSocket.close()

elapsed_time = END_TIME-START_TIME
print(elapsed_time)

with open("result_py.dat","a") as rf:
    rf.write(hostname + "\t" + str(elapsed_time) + "\n")