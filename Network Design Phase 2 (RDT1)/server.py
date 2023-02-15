#! /usr/bin/env python3

from socket import *
from packet import binaryFromPackets, getHeaderParts
import copy

messageList = []

# Declare the port that will be assigned to the server
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to the chosen port on the local host
serverSocket.bind(('', serverPort))

while True:

    header = serverSocket.recv(2048)

    numberPackets, name = getHeaderParts(header.decode())

    # Loop so that the server is constantly checking for incoming messages
    for i in range(numberPackets):

        # Receive a message from the client and store the received datagram and the address of the sender (tuple)
        message = serverSocket.recv(2048)

        # Decode the received message back into a string and make it upper case 
        messageList.append(copy.copy(message))

    data = binaryFromPackets(messageList)

    newFile = open(name, 'wb')
    newFile.write(data)

    messageList.clear()
