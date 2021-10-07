# python server.py [chunkSize]

from socket import *
from sys import argv
import threading

serverPort = 2684
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(20)

with open("file.txt","rb") as f:
    content = f.read()

chunkSize = 1024
if len(argv)==2:
    chunkSize = int(argv[1])

class SendThread(threading.Thread):
    def __init__(self, connectionSocket, chunkNumber):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.chunkNumber = chunkNumber
    def run(self):
        sendout(self.connectionSocket, chunkNumber)

def sendout(connectionSocket, cnum):
    connectionSocket.send(content[cnum*chunkSize:(cnum+1)*chunkSize].encode())
    connectionSocket.close()

with open("file_send.txt","wb") as f:
    f.write(content)
with open("result_py.dat","w") as rf:
    rf.write("Host\tTime\n")
print('Ready to send.')

while True:
    connectionSocket, addr = serverSocket.accept()
    chunkNumber = int(connectionSocket.recv(1024).decode())
    print(addr, chunkNumber)
    sth = SendThread(connectionSocket, chunkNumber)
    sth.start()