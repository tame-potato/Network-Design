#! /usr/bin/env python3

from checksum import *
from random import *
from time import *
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
    if random()*100 < CORRUPT_PROB:
        pkt[0] = abs(~pkt[0]-1)
        pkt[1] = abs(~pkt[1]-1)



# Generate a randomly corrupted ack packet
def randomCorruptAck(seq):

    ack = AckRDT22(seq)

    out = randomCorrupt(ack)

    return out


# Timeout threshold realtime update calculation
def timeoutUpdate(sampleRTT):

    alpha = 1/8

    beta = 2 * alpha

    estimatedRTT = (1-alpha) * estimatedRTTPrev + alpha * sampleRTT

    devRTT = (1-beta) * devRTTPrev + beta * abs(sampleRTT – estimatedRTT)

    safetyFactor = 4 * devRTT

    timeoutInterval = estimatedRTT + safetyFactor

    estimatedRTTPrev = estimatedRTT

    devRTTPrev = devRTT



# Check a packet for its sequence and checksum
def checkRDT22(pkt, n):

    if n == pkt.pop(2):
        print('Sequence numbers match')
        if compareChecksum(pkt):
            print('Checksum matches')
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

        msg = bytearray(msg)

        if position is None:
            print('\nMessage Header Received')
        else:
            print('\nPacket ' + str(position[0]) + '/' + str(position[1]) + ' Received')

        # Check msg checksum
        if checkRDT22(msg, seq):

            response = randomCorruptAck(seq) 
            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq ' + str(seq))
            return msg

        else:

            response = randomCorruptAck(0 if seq else 1)
            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq ' + str(0 if seq else 1))

def sendRDT(socket, seq, pkt, addr, position = None):

    msg = bytearray()
                
    while True:

        # Set timeout value for the socket operations
        socket.settimeout(timeoutInterval)

        # Randomly corrupt the checksum of some packages
        out = randomCorrupt(copy(pkt))

        # Send out the packet
        socket.sendto(out, addr) 

        # Start RTT timer
        startRTT = time()

        if position is None:
            print('\nPacket Sent')
        else:
            print('\nPacket ' + str(position[0]) + '/' + str(position[1]) + ' Sent')

        # Receive an ack and store the received datagram and the address of the sender (tuple)
        try:
            ack = socket.recv(2048)
        except timeout:
            print('No response received within Timeout window. Assuming pkt loss. RESENDING.')
            continue

        # Stop RTT timer
        stopRTT = time()

        # Check msg checksum
        if checkRDT22(ack, seq):

            # Calculate the roundtrip return time
            RTT = stopRTT - startRTT

            # Update the expected timeout timer for the next packet
            timeoutUpdate(RTT)

            print('Valid ACK received for packet')
            break
            
        else:

            print('Invalid ACK received for packet ' + str(i) + ' RESENDING')
 








