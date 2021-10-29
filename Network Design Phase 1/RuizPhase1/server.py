#! /usr/bin/env python3

from socket import *

# Declare the port that will be assigned to the server
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to the chosen port on the local host
serverSocket.bind(('', serverPort))

# Loop so that the server is constantly checking for incoming messages
while True:

    # Receive a message from the client and store the received datagram and the address of the sender (tuple)
    message, clientAddress = serverSocket.recvfrom(2048)

    # Decode the received message back into a string and make it upper case 
    modifiedMessage = message.decode().upper()

    # Encode the message into a datagram and send it back to the address it was originally received from
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
