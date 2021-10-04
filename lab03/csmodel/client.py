from socket import *
from sys import argv

if len(argv)==1:
    serverName = "127.0.0.1"
else:
    serverName = argv[1]
serverPort = 2680
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

receivedFileContent = ""
for i in range(100):
    receivedFileContent = receivedFileContent + clientSocket.recv(1024).decode()

if len(argv)==3:
    filename = "file_receive_" + argv[2] + ".txt"
else:
    filename = "file_receive.txt"

with open(filename,"wb") as f:
    f.write(receivedFileContent)

clientSocket.close()