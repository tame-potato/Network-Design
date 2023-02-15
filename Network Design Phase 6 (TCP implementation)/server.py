#! /usr/bin/env python3

from socket import *
from packet import binaryFromPackets, getHeaderParts
from tcp import *
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

    name, data, transTime = receive_tcp(serverSocket)

    print('File ' + name + ' received succesfully!\n')
    print('Transmission Time: ' + str(transTime) + ' seconds')

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

    

     
