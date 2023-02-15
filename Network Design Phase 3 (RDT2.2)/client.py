#! /usr/bin/env python3

from socket import *
from copy import copy
from packet import packetizeBinary
from time import *
from rdt22 import *

# TImeout threshold for socket operations in secs
SOCK_TIMEOUT = 1

# Obtain the name of the local host 
serverName = gethostname()

# Declare the port number of the server that the client will be communicating with
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Set timeout value for the socket operations
clientSocket.settimeout(SOCK_TIMEOUT)

# Rquest input from user for image to send
image = input('Enter the name of the image you want to send (include file type extension): ')

# Open and packetize the image message
pktList = packetizeBinary(image, 1024)

# Request input from user for image to send
imageSave = input('\nEnter the name the image will be saved under (include file type extension): ')

# The header contains the number of packets in the message and its name separated by a space
header = str(len(pktList)) + ' ' + imageSave

# Send the number of packets and the name of the file as the first message so that the server knows when the transmission has ended
pktList.insert(0, bytearray(header, 'utf-8'))

# Loop over the list of packets and send them one by one in order
for i in range(len(pktList)):

    # Generate a sequence number for the given package
    seq = i%2

    # Add the sequence number and a checksum to the package
    makeRDT22(pktList[i], seq)

    # Continue resending package until matching uncorrupted ACK has been received
    while (True):

        # Randomly corrupt the checksum of some packages
        out = randomCorrupt(copy(pktList[i]))

        # Send out the packet
        clientSocket.sendto(bytearray(out), (serverName, serverPort)) 

        print('Packet ' + str(i) + ' has been sent')

        # Wait until ack is receieved
        ack = clientSocket.recv(2048)

        # Validate the ack, send next packet valid, else resend current packet
        if checkRDT22(ack, seq):
            print('Valid ACK received for packet ' + str(i) + '\n')
            break

        print('Invalid ACK received for packet ' + str(i) + ' RESENDING\n')


print('\nAll packets have been sent succesfully!')

# Close the client's socket
clientSocket.close()

