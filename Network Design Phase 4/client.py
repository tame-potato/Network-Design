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

numPkts = len(pktList)

# Loop over the list of packets and send them one by one in order
for i in range(numPkts):

    # Generate a sequence number for the given package
    seq = i%2

    # Add the sequence number and a checksum to the package
    makeRDT22(pktList[i], seq)

    # Send packet using RDT 3.0 protocol
    sendRDT(pktList[i], (clientSocket, seq, pktList[i], (serverName, serverPort), (i, numPkts))

print('\nAll packets have been sent succesfully!')

# Close the client's socket
clientSocket.close()

