#! /usr/bin/env python3

from socket import *
from packet import packetizeBinary
from checksum import *
from rdt22 import *

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

# Request input from user for image to send
imageSave = input('\nEnter the name the image will be saved under (include file type extension): ')

# The header contains the number of packets in the message and its name separated by a space
header = str(len(packetList)) + ' ' + imageSave

# Send the number of packets and the name of the file as the first message so that the server knows when the transmission has ended
#clientSocket.sendto(header.encode(), (serverName, serverPort))
packetList.insert(0, header.encode())

# Loop over the list of packets and send them one by one in order
for i in range(len(packetList)):

    # Generate a sequence number for the given package
    seq = i%2

    # Add the sequence number and a checksum to the package
    makeRDT22(packetList[i], seq)

    # Continue resending package until matching uncorrupted ACK has been received
    while (True):

        clientSocket.sendto(bytearray(packetList[i]), (serverName, serverPort))

        print('Packet ' + i + 'has been sent\n')

        ack = clientSocket.recv(2048)

        if checkRDT22(ack, seq):
            print('Valid ACK received for packet ' + i + '\n')
            break

        print('Invalid ACK received for packet ' + i + ' RESENDING\n')

print('\nAll packets have been sent succesfully!')

# Close the client's socket
clientSocket.close()

