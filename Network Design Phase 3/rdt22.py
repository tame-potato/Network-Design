#! /usr/bin/env python3

from checksum import *

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

    if n == int.from_bytes(pkt[2], 'big'):
        return compareChecksum()
    else:
        return False

