#! /usr/bin/env python3

from socket import *
from copy import copy
from packet import packetizeBinary
from time import *
from tcp import *


# Timeout threshold for socket operations in secs
SOCK_TIMEOUT = 1

# Obtain the name of the local host 
serverName = gethostname()

# Declare the port number of the server that the client will be communicating with
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Request input from user for image to send
image = input('Enter the name of the image you want to send (include file type extension): ')

# Declare packet size
pktSize = 1024

# Open and packetize the image message
pktList = packetizeBinary(image, pktSize)

numPkts = len(pktList)

# Request input from user for image to send
imageSave = input('\nEnter the name the image will be saved under (include file type extension): ')

# The header contains the number of packets in the message and its name separated by a space
header = str(numPkts) + ' ' + imageSave + ' ' + str(pktSize)

# Send the number of packets and the name of the file as the first message so that the server knows when the transmission has ended
pktList.insert(0, bytearray(header, 'utf-8'))
 
send_tcp(clientSocket, (serverName, serverPort), pktList, pktSize)

print('\nAll packets have been sent succesfully!')

# Close the client's socket
clientSocket.close()

