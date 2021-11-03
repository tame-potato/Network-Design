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

    print('\nAwaiting Connection...')

    # First message received should be a header
    header = serverSocket.recv(2048)

    # Unpack header
    numPackets, name = getHeaderParts(header)

    # Loop so that the server is constantly checking for incoming messages
    for i in range(numPackets):

        # Receive a message from the client and store the received datagram and the address of the sender (tuple)
        message = serverSocket.recv(2048)

        print(message)
        print(i)
        print(numPackets)

        # Decode the received message back into a string and make it upper case 
        messageList.append(copy.copy(message))

        break

    # Reassemble the file from packets
    data = binaryFromPackets(messageList)
    messageList.clear()

    # Print information about the received file
    print('\nReceived file ' + name + '  of size ' + str(len(data)) + ' bytes divided into ' + str(numPackets) + ' packets') 

    # Save file
    newFile = open(name, 'wb')
    newFile.write(data)

    print('\nSaved Succesfully!')

    # Ask for permission to continue
    while True:
        done = input('\nExit? (y/n):')

        if done == 'y' or done =='n':
            break

        print('Invaid Input:')


    if done is 'y':
        break

    

     
