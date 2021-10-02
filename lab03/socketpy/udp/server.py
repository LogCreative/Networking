from socket import *
serverPort = 2680
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("Ready to receive.")
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print("[", clientAddress, ": ", message, "]")
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(),clientAddress)