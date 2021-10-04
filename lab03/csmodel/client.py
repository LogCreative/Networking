from socket import *
from sys import argv

MAXLINE = 1024
serverName = "127.0.0.1"
filename = "file_receive.txt"

if len(argv)>=2:
    MAXLINE = int(argv[1])
if len(argv)>=3:
    serverName = int(argv[2])
if len(argv)>=4:
    filename = "file_receive_" + argv[3] + ".txt"

serverPort = 2683
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

print(MAXLINE)

with open(filename,"wb") as f:
    for i in range(MAXLINE/1024):
        f.write(clientSocket.recv(1024).decode())

clientSocket.close()