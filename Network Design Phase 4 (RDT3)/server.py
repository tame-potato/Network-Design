#! /usr/bin/env python3

from socket import *
from packet import binaryFromPackets, getHeaderParts
from rdt3 import *
from time import *
from copy import copy

pktList = []

# Declare the port that will be assigned to the server
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to the chosen port on the local host
serverSocket.bind(('', serverPort))

while True:

    print('\nAwaiting Connection...')

    header = receiveRDT(serverSocket, 0)

    # Start timer
    timer = [time(), 0]

    # Unpack header
    numPackets, name = getHeaderParts(header)

    # Loop so that the server checks for all the packets in the message
    for i in range(1,numPackets):

        # Generate correct sequence number for current packet
        seq = i%2

        # Check for received message and loop until an in-order uncorrupted message has been received and Acked
        pkt = receiveRDT(serverSocket, seq, (i, numPackets))

        # Add a copy of the pacekt to the list of packets
        pktList.append(copy(pkt))

    # Stop Timer
    timer[1] = time()

    # Reassemble the file from packets
    data = binaryFromPackets(pktList)
    pktList.clear()

    # Print information about the received file
    print('\nReceived file ' + name + '  of size ' + str(len(data)) + ' bytes divided into ' + str(numPackets) + ' packets')
    print('Transmission Time: ' + str(timer[1] - timer[0]) + ' seconds')

    # Save file
    newFile = open(name, 'wb')
    newFile.write(data)

    print('\nSaved Succesfully!')

    # Ask for permission to continue
    while True:
        done = input('\nExit? (y/n):')

        if done == 'y' or done =='n':
            break

        print('Invalid Input:')


    if done == 'y':
        break

    

     
