# python peer.py [chunkSize] [serverIP] [hostIP]

from socket import *
from sys import argv
import threading
import time

chunkSize = 1024
serverName = "127.0.0.1"
filename = "file_receive.txt"
hostName = "127.0.0.1"
hostname = ""

if len(argv)>=2:
    chunkSize = int(argv[1])
if len(argv)>=3:
    serverName = argv[2]
if len(argv)>=4:
    hostName = argv[3]
    hostname = "h" + hostName.split(".")[-1]
    filename = "file_receive_" + hostname + ".txt"

START_TIME = time.time()

with open("tracker.dat","r") as tf:
    tls = tf.read().splitlines()
    # chunkID \t requestIP
    trackers = [[int(tl.split("\t")[0]),tl.split("\t")[1],False] for tl in tls]

content = {}

def DownContent(chunkNumber):
    # Check if this peer has the chunk first.
    if not trackers[chunkNumber][2]:
        # Server use 2684 for communication.
        clientPort = 2684
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, clientPort))
        # send out the chunkNumber
        clientSocket.send(str(chunkNumber).encode())

        # expect to receive the chunk from the server.
        fileChunk = ""
        for i in range(chunkSize/1024):
            fileChunk = fileChunk + clientSocket.recv(1024).decode()
        # threadLock.acquire()
        content[chunkNumber] = fileChunk           # write to self content  
        # threadLock.release()
        trackers[chunkNumber][2] = True            # declare to be useable
        print("Received Size from " + serverName + " :" + str(len(fileChunk)))

        clientSocket.close()
    else:
        fileChunk = content[chunkNumber]
    return fileChunk

class SendThread(threading.Thread):
    def __init__(self, connectionSocket, chunkNumber):
        threading.Thread.__init__(self)
        self.chunkNumber = chunkNumber
        self.connectionSocket = connectionSocket
    def run(self):
        # Detect the downloading first.
        downFileChunk = DownContent(self.chunkNumber)

        # Then send it to the peer
        self.connectionSocket.send(downFileChunk.encode())
        self.connectionSocket.close()

class ServiceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        # peer use 2685 for communication.
        receivePeerPort = 2685
        receivePeerSocket = socket(AF_INET, SOCK_STREAM)
        receivePeerSocket.bind(('', receivePeerPort))
        receivePeerSocket.listen(20)
        receivePeerSocket.settimeout(10)

        while True:
            try:
                connectionSocket, addr = receivePeerSocket.accept()
            except timeout:
                if len(content)==len(trackers):
                    # The transmission has been complete.
                    break
                else:
                    continue
            chunkNumber = int(connectionSocket.recv(1024).decode())
            print(addr, chunkNumber)
            sth = SendThread(connectionSocket,chunkNumber)
            sth.start()

def getContent(tracker):
    sendPeerPort = 2685
    sendPeerSocket = socket(AF_INET, SOCK_STREAM)
    
    try:
        time.sleep(0.5)
        sendPeerSocket.connect((tracker[1],sendPeerPort))
    except:
        print("- Retry connect to "+ tracker[1] + " after 3 sec.")
        time.sleep(3)
        sendPeerSocket.connect((tracker[1],sendPeerPort))
        print("+ Connect to "+ tracker[1] + " success.")

    sendPeerSocket.send(str(tracker[0]).encode())
    # expect to receive the chunk from the server.
    receivedFileChunk = ""
    for i in range(chunkSize/1024):
        receivedFileChunk = receivedFileChunk + sendPeerSocket.recv(1024).decode()
    print("Received Size from " + tracker[1] + " :" + str(len(receivedFileChunk)))
    content[tracker[0]] = receivedFileChunk           # write to self content  
    trackers[tracker[0]][2] = True            # declare to be useable
    sendPeerSocket.close()

class ReceiveThread(threading.Thread):
    def __init__(self, tracker):
        threading.Thread.__init__(self)
        self.tracker = tracker
    def run(self):
        getContent(self.tracker)
class FetchingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        rths = []
        for tracker in trackers:
            # To avoid conflict, will be called by other peer.
            if not tracker[1] == hostName:
                rth = ReceiveThread(tracker)
                rth.start()
                rths.append(rth)
        for rth in rths:
            rth.join()

# Start servicing.
serth = ServiceThread()
serth.start()

# Start fetching
fetth = FetchingThread()
fetth.start()

# Wait for merge
fetth.join()

# Now, force to download the own chunk if it is not downloaded.
for tracker in trackers:
    if tracker[1] == hostName and tracker[2] == False:
        DownContent(tracker[0])

# should be done with all file chunks, unless error occurred.
with open(filename,"wb") as f:
    for i in range(len(content)):
        if i in content.keys():
            f.write(content[i])
        else:
            print("- " + hostname + " lost chunk " + str(i))

END_TIME = time.time()

elapsed_time = END_TIME-START_TIME
print(elapsed_time)

with open("result_py.dat","a") as rf:
    rf.write(hostname + "\t" + str(elapsed_time) + "\n")