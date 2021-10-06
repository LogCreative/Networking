from socket import *
import threading

serverPort = 2683
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(20)

with open("file.txt","rb") as f:
    content = f.read()

class SendThread(threading.Thread):
    def __init__(self, connectionSocket):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
    def run(self):
        sendout(self.connectionSocket)

def sendout(connectionSocket):
    connectionSocket.send(content.encode())
    connectionSocket.close()

with open("file_send.txt","wb") as f:
    f.write(content)
with open("result_py.dat","w") as rf:
    rf.write("Host\tTime\n")
print('Ready to send.')

while True:
    connectionSocket, addr = serverSocket.accept()
    print(addr)
    sth = SendThread(connectionSocket)
    sth.start()