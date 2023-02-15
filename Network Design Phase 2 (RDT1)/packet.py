#! /usr/bin/env python3

import math
import copy

def packetizeBinary(filePath, packetSize):

    packet = []
    packetList = []

    # Open file in reading and binary mode using the filePath
    with open(filePath, 'rb') as image:
        # Convert into an array of bytes that can be easily manipulated
        data = bytearray(image.read())

    # Loop one time per packet and round up because the packets can't be fractional
    for i in range(math.ceil(len(data)/packetSize)):
        
        # Loop through the data array in 1024 byte increments
        for j in range(i*packetSize, i*packetSize + packetSize):

            # If the index is larger than the length of the array stop and exit the loop
            if j < len(data):
                # Append the bytes into a list which will represent one packet
                packet.append(data[j])
            else:
                break

        # Append each packet into a list where each member is a packet
        packetList.append(copy.copy(packet))
        # Clear the packet list so that it can be filled with the next 1024 bytes in the next iteration
        packet.clear()

    # Print information about the packets
    print('The binary file ' + filePath + ' contains ' + str(len(data)) + ' bytes divided into ' + str(len(packetList)) + ', ' + str(packetSize) + ' byte packets')

    return packetList

def binaryFromPackets(packetList):

    data = []

    for i in packetList:
        data.extend(i)

    data = bytearray(data)

    return data

# Separate the header string into its two components
def getHeaderParts(header):

    # Find the index of the first space
    spacePosition = header.find(' ')

    # Extract everything after the space as the number of packets
    packetNumber = int(header[spacePosition+1:])

    # Extract everything before the space as the name of the file   
    name = header[:spacePosition]
    
    return [packetNumber, name]
        


