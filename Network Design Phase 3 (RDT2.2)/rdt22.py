#! /usr/bin/env python3

from checksum import *
from random import *
from time import *
from copy import copy

# Probability of data corruption as a percentage
CORRUPT_PROB = 0

# Seed the random number generator function with the current time in sec
seed(time())

# Receives packet as bytearray and sequence number and inserts the sequence number at the front
def addSequence(pkt, n):

    pkt.insert(0, n)


# Receives packet as a bytearray and adds a sequence number and checksum
def makeRDT22(pkt, n):

    addSequence(pkt, n)

    addChecksum(pkt)

# Receives a sequence number (one byte) and generates an ACK message from it including a checksum
def AckRDT22(n):

    ack = bytearray()

    makeRDT22(ack, n)

    return ack


# Check a packet for its sequence and checksum
def checkRDT22(pkt, n):

    pkt = bytearray(pkt)

    if n == pkt[2]:
        print('Sequence numbers match')
        if compareChecksum(pkt):
            print('Checksum matches')
            return True
        else:
            print('Checksum does not match')
    else:
        print('Sequence number does not match')

    return False

# Remove the leading 3 bytes (checksum and sequence) of a packet
def removeHeader(pkt):
    return pkt[3:]


# Waits for the correct packet and sends the sender an ack with the number of the expected sequence
def validatePkt(socket, seq, numPkt = None, totPkt = None):

    while True:
        # Receive a message from the client and store the received datagram and the address of the sender (tuple)
        message, clientAddress = socket.recvfrom(2048)

        if numPkt == None and totPkt == None:
            print('Message Header Received')
        else:
            print('\nPacket ' + str(numPkt) + '/' + str(totPkt) + ' Received')

        # Check message checksum
        if checkRDT22(message, seq):
            ack = randomCorruptAck(seq)

            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq '+str(seq)+'\n')
            break
        else:
            ack = randomCorruptAck(0 if seq else 1)

            socket.sendto(ack, clientAddress)
            print('Sending Ack with Seq '+str(0 if seq else 1)+'\n')

    # Remove header fields
    data = removeHeader(message)

    return data

# Randomly corrupt the checksum of the given packet by flipping the bits
def randomCorrupt(pkt):

    if random()*100 < CORRUPT_PROB:
        pkt[0] = abs(abs(~pkt[0]) - 10)
        pkt[1] = abs(abs(~pkt[1]) - 10)

    return pkt

# Generate a randomly corrupted ack packet
def randomCorruptAck(seq):

    ack = AckRDT22(seq)

    out = randomCorrupt(ack)

    return out





