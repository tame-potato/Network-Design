#! /usr/bin/env python3

# Go Back N (GBN) functions

from socket import *
from checksum import *
from time import time
from random import seed, random
from copy import copy
from packet import binaryFromPackets, getHeaderParts

# Probability of data corruption as a percentage
CORRUPT_PROB = 0

# Loss Probability
LOSS_PROB = 0

# Seed the random number generator function with the current time in sec
seed(time())

# Randomly corrupt the checksum of the given packet by flipping the bits
def randomCorrupt(pkt):

    out = copy(pkt)

    if random()*100 < CORRUPT_PROB:
        out[0] = abs(~pkt[0]-1)
        out[1] = abs(~pkt[1]-1)

    return out

# Make a 4 byte (32bit) sequence number
def make_seq(seqNum):
    
        seqBytes = seqNum.to_bytes(4,'big')

        seqBytes = bytearray(seqBytes)

        return seqBytes

def make_gbn_list(pktList):
    
    seqNum = 0

    for i, pkt in enumerate(pktList):

        # Add the sequence number to the beginning of the packet
        pktList[i] = make_seq(seqNum) + pkt

        # Include Checksum
        addChecksum(pktList[i])

        seqNum += 1


def check_gbn(pkt):

    # Artificially corrupt the packet for testing purposes
    randomCorrupt(pkt)
    
    if compareChecksum(pkt):

        # Pop the sequence number from the list as a bytearray
        seqBytes = [pkt.pop(0) for i in range(4)]

        # Convert sequence number to int
        seqNum = int.from_bytes(seqBytes, 'big')

        return seqNum

    else:
        print('Received corrupted packet. Packet dropped.')
        return None

def send_ack(socket, addr, seqNum):

    # Add the sequence number to the beginning of the packet
    pkt = make_seq(seqNum)

    # Generate and include Checksum
    addChecksum(pkt)

    # Send ack
    socket.sendto(pkt, addr)

 # Find the first packet that hasnt been received and return that as the nextSeqNum
def find_next_seq(pktList, nextSeqNum):

    nextSeqNumNew = nextSeqNum
    
    for i in range(nextSeqNum, len(pktList)):
        if pktList[i] == None:
            nextSeqNumNew = i+1

    # If none of the existing entries are None
    if nextSeqNum == nextSeqNumNew:
        nextSeqNumNew += 1
        
    return nextSeqNumNew

# Check if the received msg matches the nextSeqNum and send the appropriate ack
def check_seq(seqNum, nextSeqNum, pktList, msg):

    if seqNum != None:

        # In case a packet with a sequence number larger than the length of the pktList is received increase length by appending None entries
        for i in range(seqNum - len(pktList)):
            pktList.append(None)

        # If the sequence number is valid and it hasn't been stored previously, store
        if seqNum > 0:

            if pktList[seqNum-1] == None:

                pktList[seqNum-1] = copy(msg)

                print('Packet ' + str(seqNum) + ' received intact and stored.')

            else:

                print('Packet ' + str(seqNum) + ' received as duplicate.')

    # If the seqNum is the same as the desired next sseq num then update nextseqnum to the next empty spot on the pktList
    if seqNum == nextSeqNum:
        nextSeqNum = find_next_seq(pktList, nextSeqNum)

    return nextSeqNum

# Timeout threshold realtime update calculation
def time_out_update(sampleRTT, estimatedRTTPrev, devRTTPrev):

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

    return (timeoutInterval, estimatedRTT, devRTT)

def send_gbn(clientSocket, addr, pktList):

    # Set window size
    N = 10 

    # Generate timer array
    timers = [None] * N

    # Base timeout counter
    timeOutCount = 0
    
    # Set starting beginning of window
    base = 0

    # Set starting number of packet to be sent
    nextSeqNum = 0

    # Set timeout calculation variables starting values
    timeOut = 0.5
    estimatedRTTPrev = 1
    devRTTPrev = 0

    # Set socket to non-blocking
    clientSocket.setblocking(0)

    # Generate the list of gbn packets
    make_gbn_list(pktList)

    while base < len(pktList):

        try:
            ack = clientSocket.recv(2048)

        except OSError as e:

            if nextSeqNum < base+N and nextSeqNum < len(pktList):

                # Send out the packet
                clientSocket.sendto(pktList[nextSeqNum], addr) 
 
                print('Packet with sequence number ' + str(nextSeqNum) + ' sent\n')

                timers[nextSeqNum - base] = time()

                nextSeqNum += 1

            currentTime = time()

            # Check timers for any timeouts
            for i in range(N):

                if timers[i] == None:
                    pass

                elif currentTime - timers[i] > timeOut:

                    if i == 0:
                        timeOutCount += 1

                    print('\n**TIMEOUT OCURRED RESENDING PACKET ' + str(base+i) + '/' + str(len(pktList)-1) + '\n')

                    # Resend the timed out packet
                    clientSocket.sendto(pktList[base+i], addr)

                    # Reset the timer for that base
                    timers[i] = time()

            if base >= len(pktList)-N and timeOutCount > 5:
                print('\nLast packet sent 6 times, ASSUMING RECEIVED, EXITING!')
                break

        else:

            # Artificially drop the ack packet for testing purposes
            if random()*100 < LOSS_PROB:
                continue
            else:
                # Convert the bytes type object to a bytearray to make it mutable
                ack = bytearray(ack)

                # Check integrity of the packet
                seqNum = check_gbn(ack)

                # If the packet is intact and the acked packet is equal to or larger than the packet before the current base, its relevant
                if seqNum != None and seqNum >= base:

                    print('Ack received for packet with sequence number: ' + str(seqNum))

                    # Calculate the difference between the new requested base and the old base
                    delta = seqNum - base

                    # Make the base equal to the next seq number to be sent if the seq. number is larger than the base
                    base = seqNum + 1

                    # In case the nextSeqNum has fallen behind (possibly due to it being reset by a timeout or lost packets) update it if necessary
                    if nextSeqNum < base:
                        nextSeqNum = base

                    print('New Base is ' + str(base) + ' and Next Sequence to Send is ' + str(nextSeqNum) + '\n')

                    # Recalculate timeout value
                    currentTime = time()
                    timeOut, estimatedRTTPrev, devRTTPrev = time_out_update(currentTime - timers[delta], estimatedRTTPrev, devRTTPrev)

                    # Reorganize the timers for the packets in the window
                    for i in range(delta+1):
                        timers.pop(0)
                        timers.append(None)

                    # Restart the time out counter
                    timeOutCount = 0

        
def receive_gbn(socket):

    # Initialize the current sequence number to None
    seqNum = None

    # Initialize the expected next sequence number to 1
    nextSeqNum = 0

    # Initialize packet list
    pktList = []

    print('\nAwaiting Connection...\n')

    while seqNum != 0:

        # Wait until header received
        msg, clientAddress = socket.recvfrom(2048)

        # Artificially drop the ack packet for testing purposes
        if random()*100 < LOSS_PROB:
            continue
        else:

            # Start transmission time timer
            start = time()

            # Convert the bytes type object to a bytearray to make it mutable
            msg = bytearray(msg)

            # Check integrity of msg
            seqNum = check_gbn(msg)

            # Check the sequence of message, add to the pktList if first time message is received, and set nextSeqNum to the next missing packet
            nextSeqNum = check_seq(seqNum, nextSeqNum, pktList, msg)

            if nextSeqNum != 0:

                # Unpack header
                numPkts, name = getHeaderParts(msg)

                print('Connection Established\nReceived file name is: ' + name + '\nFile is divided into: ' + str(numPkts) + ' packets')

                # Send ack acknowledging the header has been received
                send_ack(socket, clientAddress, 0)

                print('Ack sent acknowledging packet: 0/' + str(numPkts) + '\n')

    
    while seqNum < numPkts:

        # Receive a msg from the client and store the received datagram
        msg = socket.recv(2048)

        # Artificially drop the ack packet for testing purposes
        if random()*100 < LOSS_PROB:
            continue
        else:
            # Convert the bytes type object to a bytearray to make it mutable
            msg = bytearray(msg)

            # Check integrity of msg
            seqNum = check_gbn(msg)

            # Check the sequence of message and add to the pktList if first time message is received
            nextSeqNum = check_seq(seqNum, nextSeqNum, pktList, msg)

            # Send ack for the pkt before nextSeqNum as the last pkt received intact
            send_ack(socket, clientAddress, nextSeqNum - 1)

            print('Ack sent acknowledging packet: ' + str(nextSeqNum-1) + '/' + str(numPkts) + '\n')

    # STop transmission timer
    stop = time()

    return (name, binaryFromPackets(pktList), stop-start)