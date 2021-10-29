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

    ack = bytearray()

    while True:
        # First message received should be a header
        header, clientAddress = serverSocket.recvfrom(2048)

        # Check header checksum
        if checkRDT22(header, 0):
            serverSocket.sendto(AckRDT22(0), clientAddress)
            break
        else:
            serverSocket.sendto(AckRDT22(1), clientAddress)

    # Unpack header
    numPackets, name = getHeaderParts(header)

    # Loop so that the server is constantly checking for incoming messages
    for i in range(1,numPackets+1):

        seq = i%2

        while True:
            # Receive a message from the client and store the received datagram and the address of the sender (tuple)
            message, clientAddress = serverSocket.recvfrom(2048)

            # Check message checksum
            if checkRDT22(message, seq):
                serverSocket.sendto(AckRDT22(seq), clientAddress)
                break
            else:
                serverSocket.sendto(AckRDT22(0 if seq else 1), clientAddress)

        # Decode the received message back into a string and make it upper case 
        messageList.append(copy.copy(message))

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


    if done == 'y':
        break

    

     
