#! /usr/bin/env python3

from socket import *
from packet import packetizeBinary

# Obtain the name of the local host 
serverName = gethostname()

# Declare the port number of the server that the client will be communicating with
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Rquest input from user for image to send
image = input('Enter the name of the image you want to send (include file type extension): ')

# Open and packetize the image message
packetList = packetizeBinary(image, 1024)

# Rquest input from user for image to send
imageSave = input('Enter the name the image will be saved under (include file type extension): ')

# The header contains the number of packets in the message and its name separated by a space
header = imageSave + ' ' + str(len(packetList))

# Send the number of packets as the first message so that the server knows when the transmission has ended
# and send the name that the server will use to save the file
clientSocket.sendto(header.encode(), (serverName, serverPort))

# Loop over the list of packets and send them one by one in order
for message in packetList:

    # Encode the message into a datagram and send it to the server 
    clientSocket.sendto(bytearray(message), (serverName, serverPort))

# Close the client's socket
clientSocket.close()

