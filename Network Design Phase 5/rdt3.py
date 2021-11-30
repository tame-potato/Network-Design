#! /usr/bin/env python3

# Reliable Data Transfer 3.0 (RDT3) functions

from socket import *
from checksum import *
from random import seed, random
from time import time
from copy import copy

# Probability of data corruption as a percentage
CORRUPT_PROB = 0

# Timeout calculation variables
timeoutInterval = 1
estimatedRTTPrev = 0
devRTTPrev = 0

# Seed the random number generator function with the current time in sec
seed(time())

# Receives packet as bytearray and sequence number and inserts the sequence number at the front
def addSequence(pkt, n):

    pkt.insert(0, n)


# Receives packet as a bytearray and adds a sequence number and checksum
def makeRDT22(pkt, n):

    addSequence(pkt, n)
    addChecksum(pkt)


# Receives a sequence number (one byte) and generates an ACK msg from it including a checksum
def AckRDT22(n):

    ack = bytearray()

    makeRDT22(ack, n)

    return ack

# Randomly corrupt the checksum of the given packet by flipping the bits
def randomCorrupt(pkt):

    out = copy(pkt)

    if random()*100 < CORRUPT_PROB:
        out[0] = abs(~pkt[0]-1)
        out[1] = abs(~pkt[1]-1)

    return out


# Generate a randomly corrupted ack packet
def randomCorruptAck(seq):

    ack = AckRDT22(seq)

    out = randomCorrupt(ack)

    return out


# Timeout threshold realtime update calculation
def timeoutUpdate(sampleRTT):

    global estimatedRTTPrev
    global devRTTPrev

    alpha = 1/8

    beta = 2 * alpha

    # Calculate the running RTT average
    estimatedRTT = (1-alpha) * estimatedRTTPrev + alpha * sampleRTT

    # Calculate the running average deviation from RTT
    devRTT = (1-beta) * devRTTPrev + beta * abs(sampleRTT - estimatedRTT)

    # Calculate safety factor
    safetyFactor = 4 * devRTT

    # Calcuilate the timeout interval for this iteration
    timeoutInterval = estimatedRTT + safetyFactor

    estimatedRTTPrev = estimatedRTT

    devRTTPrev = devRTT



# Check a packet for its sequence and checksum
def checkRDT22(pkt, n):

    if n == pkt[2]:

        print('Sequence numbers match')

        if compareChecksum(pkt):
            print('Checksum matches')
            pkt.pop(0)
            return True
        else:
            print('Checksums do not match')

    else:
        print('Sequence numbers do not match')

    return False


# Waits for the correct packet and sends the sender an ack with the number of the expected sequence
def receiveRDT(socket, seq, position = None):

    while True:

        # Receive a msg from the client and store the received datagram and the address of the sender (tuple)
        msg, clientAddress = socket.recvfrom(2048)

        # Convert the bytes type object to a bytearray to make it mutable
        msg = bytearray(msg)

        if position is None:
            print('\nMessage Header Received')
        else:
            print('\nPacket ' + str(position[0]) + '/' + str(position[1]) + ' Received')

        # Check msg checksum
        if checkRDT22(msg, seq):

            ack = randomCorruptAck(seq) 
            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq ' + str(seq))
            return msg

        else:

            ack = randomCorruptAck(0 if seq else 1)
            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq ' + str(0 if seq else 1))

def sendRDT(socket, seq, pkt, addr, position = None):
    
    # Add the sequence number and a checksum to the package
    makeRDT22(pkt, seq)

    while True:

        # Set timeout value for the socket operations
        socket.settimeout(timeoutInterval)

        # Randomly corrupt the checksum of some packages
        out = randomCorrupt(pkt)

        # Send out the packet
        socket.sendto(out, addr) 

        # Start RTT timer
        startRTT = time()

        if position is None:
            print('\nPacket Sent')
        else:
            print('\nPacket ' + str(position[0]+1) + '/' + str(position[1]) + ' Sent')

        # Receive an ack and store the received datagram and the address of the sender (tuple)
        try:
            ack = socket.recv(2048)
        except timeout:
            print('No response received within Timeout window. Assuming pkt loss. RESENDING.')
            continue

        # Stop RTT timer
        stopRTT = time()

        # Convert bytes object to bytearray to make it mutable
        ack = bytearray(ack)

        # Check msg checksum
        if checkRDT22(ack, seq):

            # Calculate the roundtrip return time
            RTT = stopRTT - startRTT

            # Update the expected timeout timer for the next packet
            timeoutUpdate(RTT)

            print('Valid ACK received for packet')
            break
            
        else:

            print('Invalid ACK received for packet. RESENDING**')
 








