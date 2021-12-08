#! /usr/bin/env python3

# Go Back N (GBN) functions

from socket import *
from checksum import *
from time import time
from random import seed, random
from copy import copy
from math import ceil
from packet import binaryFromPackets, getHeaderParts

# Probability of data corruption as a percentage
CORRUPT_PROB = 0

# Loss Probability
LOSS_PROB = 0

# Declare size of header in bytes
HEADER_SIZE = 13

# Seed the random number generator function with the current time in sec
seed(time())

# Randomly corrupt the checksum of the given packet by flipping the bits
def randomCorrupt(pkt):

    out = copy(pkt)

    if random()*100 < CORRUPT_PROB:
        out[0] = 0
        out[1] = 0

    return out

# Make a 4 byte (32bit) sequence number
def make_seq(seqNum):
    
    seqBytes = seqNum.to_bytes(4,'big')

    seqBytes = bytearray(seqBytes)

    return seqBytes

# Generates a one byte bytearray with each bit representing an option flag
def make_options(syn = False, fin = False, finAck = False):

    # Create a bytearray with one Null byte
    options = 0

    # Set the option bits based on the function arguments
    if syn is not False:
        options += 1
    if fin is not False:
        options += 2
    if finAck is not False:
        options += 4

    # Convert options to an array of bytes
    options = options.to_bytes(1, 'big')

    options = bytearray(options)

    return options

# Checks the checksum and options of the packet, returns None is either don't match or the seq number otherwise
def check_tcp(pkt, syn = False, fin = False, finAck = False):

    # Artificially corrupt the packet for testing purposes
    randomCorrupt(pkt)
    
    if compareChecksum(pkt):

        # Generate the desired options byte for comparison
        desiredOptions = make_options(syn, fin, finAck)

        #print('Desired Options: ' + str(desiredOptions))

        # Pop options byte from pkt
        includedOptions = pkt.pop(0)

        #print('Included Options: ' + str(includedOptions))

        # Check that the included options match the expected options
        if desiredOptions[0] == includedOptions:

            # Pop the sequence number from the list as a bytearray
            seqBytes = [pkt.pop(0) for i in range(4)]

            # Convert sequence number to int
            seqNum = int.from_bytes(seqBytes, 'big')

            # Pop the ack sequence number from the list as a bytearray
            ackBytes = [pkt.pop(0) for i in range(4)]

            # Convert ack sequence number to int
            ackNum = int.from_bytes(ackBytes, 'big')

            # Pop the flow bytes from the packet
            flow = [pkt.pop(0) for i in range(2)]

            # Convert flow sequence number to int
            flow = int.from_bytes(flow, 'big')

            return (seqNum, ackNum, flow)

        else:
            #print('Options byte does not match what was expected. Packet dropped.')
            return (None, None, None)

    else:
        print('Received corrupted packet. Packet dropped.')
        return (None, None, None)

 # Find the first packet that hasnt been received and return that as the nextSeqNum
def find_next_seq(pktList, nextSeqNum, index, start, size):

    nextSeqNumNew = nextSeqNum
    
    for i in range(index, len(pktList)):
        if pktList[i] == None:
            nextSeqNumNew = index * size + start + size

    # If none of the existing entries are None
    if nextSeqNum == nextSeqNumNew:
        nextSeqNumNew += size
        
    return nextSeqNumNew

# Check if the received msg matches the nextSeqNum and if it does set the new nextSeqNum
def check_seq(seqNum, nextSeqNum, pktList, index, start, size, msg):

    if seqNum != None:

        # In case a packet with a sequence number larger than the length of the pktList is received increase length by appending None entries
        for i in range(index + 1 - len(pktList)):
            pktList.append(None)

        # If the sequence number is valid and it hasn't been stored previously, store
        if seqNum > 0:

            if pktList[index] == None:

                pktList[index] = copy(msg)

                print('Packet with sequence ' + str(seqNum) + ' received intact and stored.')

            else:
                print('Packet with sequence ' + str(seqNum) + ' received as duplicate.')

    # If the seqNum is the same as the desired next seq num then update nextseqnum to the next empty spot on the pktList
    if seqNum == nextSeqNum:
        nextSeqNum = find_next_seq(pktList, nextSeqNum, index, start, size)

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

# Generate a 2 byte flow value as a bytearray
def make_flow(flow):

    out = flow.to_bytes(2,'big')

    out = bytearray(out)

    return out

# Returns handshake or closed connection packet with the options set by the passed arguments
def make_tcp_pkt(sequence, ackSeq = None, syn = False, fin = False, finAck = False, flow = None, data = bytearray()):

    # If an ack number was passed make it into a bytearray otherwise make it a blank bytearray
    if ackSeq is not None:
        ackBytes = make_seq(ackSeq)
    else:
        ackBytes = bytearray()

    # Convert sequence number into a bytearray
    seqBytes = make_seq(sequence)

    # Generate the options byte
    options = make_options(syn, fin, finAck)

    # Generate the 2 bytes for flow control
    if flow is not None:
        flow = make_flow(flow)
    else:
        flow = make_flow(0)

    # Join all the components into one bytearray
    pkt = options + seqBytes + ackBytes + flow + data

    # Add checksum
    addChecksum(pkt)

    return pkt


def handshake_client(socket, addr, timeOut, headerPkt):

    # Set socket to non-blocking in case it wasn't yet
    socket.setblocking(0)

    # Initialize start time to 0 so it sends on the first iteration
    startTime = 0

    # Initialize timeout counter
    timeOutCount = 0

    # Random start sequence from 0 to 1000
    startSeq = int(random()*1000)

    # Make initial handshake packet
    pkt = make_tcp_pkt(startSeq, ackSeq = 0, syn = True, fin = False, finAck = False)

    # Loop until syn received
    while True:

        try:
            synAck = socket.recv(2048)

        except OSError as e:

            currentTime = time()
            
            # If timeout send the initial tcp packet and reset startTime
            if currentTime - startTime > timeOut:

                socket.sendto(pkt, addr)

                print('\nFirst handshake message with SYN option sent.\n')

                startTime = time()

        # If a packet is received check that its not corrupted and that its options match
        else:

            # Convert to byte array
            synAck = bytearray(synAck)

            seq, ackSeq, flow = check_tcp(synAck, syn = True)

            if ackSeq == startSeq:

                print('Second handshake message received with SYN option.\n')

                break

    # Create third handshake pkt 
    pkt = make_tcp_pkt(startSeq, seq, syn = False, fin = False, finAck = False, data = headerPkt)

    expectedSeq = startSeq + len(headerPkt)

    # Reset startTime
    startTime = 0

    # Loop until syn received
    while True:

        try:
            synAck = socket.recv(2048)

        except OSError as e:

            currentTime = time()
            
            # If timeout send the initial tcp packet and reset startTime
            if currentTime - startTime > timeOut:

                socket.sendto(pkt, addr)

                print('Third handshake message without SYN option sent including the first data packet (header).\n')

                startTime = time()

                # Set a timeout limit in case the ack message from the receiver got lost
                timeOutCount += 1

                if timeOutCount > 10:
                    break

        # If a packet is received check that its not corrupted and that its options match
        else:

            # Convert to byte array
            synAck = bytearray(synAck)

            seq, ackSeq, flow = check_tcp(synAck)

            if ackSeq == expectedSeq:

                print('Ack for third handshake message and header received.\n')

                break

    # Return the starting sequence for the client and the starting ackSeq for the receiver
    return expectedSeq, seq
    

def handshake_server(socket):

    print('\nAwaiting Connection...\n')

    # Random start sequence
    startSeq = int(random()*1000)

    # Loop until a valid message has been received
    while True:

        # Wait until message received
        recvPkt, addr = socket.recvfrom(2048)

        # Convert to byte array
        recvPkt = bytearray(recvPkt)

        # Check the integrity of the message
        seq, ackSeq, flow = check_tcp(recvPkt, syn = True)

        # If message is valid generate 2nd handshake message and send
        if seq != None:

            print('First handshake message received with SYN option.\n')

            sendPkt = make_tcp_pkt(startSeq, seq, syn = True, fin = False, finAck = False)

            socket.sendto(sendPkt, addr)

            print('Second handshake message sent with SYN option.\n')

            break

    # Loop until a valid message has been received
    while True:

        # Wait until message received
        recvPkt = socket.recv(2048)

        # Convert to byte array
        recvPkt = bytearray(recvPkt)

        # Check the integrity of the message
        seq, ackSeq, flow = check_tcp(recvPkt)

        # If message is valid generate 2nd handshake message and send
        if seq != None:

            print('Third handshake message received without SYN option and with header data packet.\n')

            # Unpack header
            numPkts, name, pktSize = getHeaderParts(recvPkt)

            # Calculate the ack seq for the received packet
            ackSeq = seq + len(recvPkt)

            # Generate ack message
            sendPkt = make_tcp_pkt(startSeq, ackSeq, syn = False, fin = False, finAck = False)

            # Send ack
            socket.sendto(sendPkt, addr)

            print('Ack sent for third handshake message with header.\n')

            break

    return startSeq, ackSeq, numPkts, pktSize, name 

def close_connection_client(socket, addr, seq, ackSeq, timeOut):

    # Set socket to non-blocking in case it wasn't yet
    socket.setblocking(0)

    # Initialize start time to 0 so it sends on the first iteration
    startTime = 0

    # Generate FIN packet
    pkt = make_tcp_pkt(seq, ackSeq, syn = False, fin = True, finAck = False)

    # Loop until syn received
    while True:

        currentTime = time()

        try:
            finAck = socket.recv(2048)

        except OSError as e:
            
            # If timeout send the initial tcp packet and reset startTime
            if currentTime - startTime > timeOut:

                socket.sendto(pkt, addr)

                print('Close connection first message with FIN option sent.\n')

                startTime = time()

        # If a packet is received check that its not corrupted and that its options match
        else:

            # Convert to byte array
            finAck = bytearray(finAck)

            receiverSeq, ackSeq, flow = check_tcp(finAck, finAck = True)

            if ackSeq == seq:
                print('Close connection second message with FINACK option received.\n')
                break

    startTime = time()

    # Loop until a valid message has been received
    while True:

        try:
            # Wait until message received
            fin = socket.recv(2048)

        except OSError as e:

            currentTime = time()

            if currentTime - startTime > 5:
                break

        else:

            # Convert to byte array
            fin = bytearray(fin)

            # Check the integrity of the message
            receiverSeq, ackSeq, flow = check_tcp(fin, fin = True)

            # If message is valid generate finack message and send
            if ackSeq == seq:

                print('Close connection third message with FIN option received.\n')

                pkt = make_tcp_pkt(seq, ackSeq, syn = False, fin = False, finAck = True)

                socket.sendto(pkt, addr)

                print('Close connection fourth message with FINACK option sent.\n')

                break


def close_connection_server(socket, seq, timeOut):

    # Set socket to non-blocking in case it wasn't yet
    socket.setblocking(0)

    finFlag = False

    # Initialize the counter at -1 to account for the first timeout period before the fin msg is sent
    timeoutCounter = -1

    # Loop until a valid message has been received
    while True:

        try:
            fin, addr = socket.recvfrom(2048)

        except OSError as e:

            currentTime = time()

            # If the fin message has already been sent 10 times assume that the client exited or the connection died and exit
            if timeoutCounter > 10:
                break

            # If a Fin message has been received from the client then the sender sends a fin message every timeOut interval until it is aknowledged by the client
            if finFlag is True and currentTime - startTime > timeOut:

                pkt = make_tcp_pkt(seq, senderSeq, syn = False, fin = True, finAck = False)

                socket.sendto(pkt, addr)

                print('Close connection third message with FIN option sent.\n')

                timeoutCounter += 1

                startTime = time()

        else:

            # Convert to byte array
            fin = bytearray(fin)

            # Check if the message is fin
            senderSeq, ackSeq, flow = check_tcp(copy(fin), fin = True)

            # If message is valid generate finack message and send
            if ackSeq == seq:

                print('Close connection first message with FIN option received.\n')

                pkt = make_tcp_pkt(seq, senderSeq, syn = False, fin = False, finAck = True)

                socket.sendto(pkt, addr)

                print('Close connection second message with FINACK option sent.\n')

                finFlag = True

                # Start timer so that after one timeout interval a fin message is sent
                startTime = time()

            else:
                # Check if the message is finack
                senderSeq, ackSeq, flow = check_tcp(copy(fin), finAck = True)


                # If message is valid generate fin message and send
                if ackSeq == seq:

                    print('Close connection fourth message with FINACK option received.\n')

                    break

    # Return socket to blocking mode
    socket.setblocking(1)

# Used in case of timeout. Check state and update values accordingly
def update_state_timeout(N, ssthresh, state, timers):

    # Check the current state and take the appropriate actions
    # Make ssthresh half of N (round down) and if it ends up at 0, make it 1
    ssthresh = int(N/2)

    if ssthresh < 1:
        ssthresh = 1

    # Return N to 1
    N = 1

    # Remove unnecessary timers
    timers = timers[0:1]

    timers[0] = None

    if state == 'congestion avoidance':
        
        state = 'slow start'

    return (N, ssthresh, state, timers)

def send_gbn(clientSocket, addr, pktList, pktLength, sr=False):

    # Set initial window size
    N = 1

    # Generate timer array
    timers = [None] * N

    # Base timeout counter
    timeOutCount = 0

    # Set timeout calculation variables starting values
    timeOut = 0.5
    estimatedRTTPrev = 1
    devRTTPrev = 0

    # Set socket to non-blocking
    clientSocket.setblocking(0)

    # Perform three way handshake and send header on the third message
    startSeq, recvSeq = handshake_client(clientSocket, addr, timeOut, pktList.pop(0))

    print('Sender random initial sequence number is: ' + str(startSeq) + '\n')

    # Set initial base to the starting sequence number
    base = startSeq

    # Set final base to the base number after receipt of the last packet
    finalBase = startSeq
    for i in range(len(pktList)):
        finalBase += len(pktList[i])

    # Set starting number of packet to be sent
    nextSeqNum = base

    # Set initial state
    state = 'slow start'

    # Set initial ssthresh
    ssthresh = None

    # Set initial flow value to a number equal to 10 times the pkt length to start
    flow = 10 * pktLength

    while base < finalBase:

        try:
            ack = clientSocket.recv(2048)

        except OSError as e:

            if nextSeqNum <= base+(int(N)-1)*pktLength and nextSeqNum < finalBase and flow >= pktLength:

                index = ceil((nextSeqNum-startSeq)/pktLength)

                #print('current index is: ' + str(index) + '\n')

                # Make the next packet into tcp format
                pkt = make_tcp_pkt(nextSeqNum, recvSeq, data = pktList[index])

                # Send out the packet
                clientSocket.sendto(pkt, addr) 
 
                print('Packet with sequence number ' + str(nextSeqNum) + ' sent')
                print('Currently in ' + state + ' mode')
                print('Window size is: ' + str(int(N)) + '\n')
                print('Current Timeout is: ' + str(timeOut) + '\n')

                timers[ceil((nextSeqNum - base)/pktLength)] = time()

                nextSeqNum += pktLength

                flow -= pktLength

            currentTime = time()

            # Check if SR is enabled
            if sr is True:

                # Check timers for any timeouts using SR
                for i in range(int(N)):

                    if timers[i] == None:
                        pass

                    elif currentTime - timers[i] > timeOut:

                        if i == 0:
                            timeOutCount += 1

                        print('\n**TIMEOUT OCURRED IN SR MODE, RESENDING PACKET WITH SEQ ' + str(base+i*pktLength) + '\n')

                        # Make the repeated packet into tcp format
                        pkt = make_tcp_pkt(base+i*pktLength, recvSeq, data = pktList[(base+i*pktLength-startSeq)/pktLength])

                        # Resend the timed out packet
                        clientSocket.sendto(pkt, addr)

                        # Reset the timer for that base
                        timers[i] = time()

                        # Update state and values
                        N, ssthresh, state, timers = update_state_timeout(N, ssthresh, state, timers)

                        print('Currently in ' + state + ' mode')
                        print('Window size is: ' + str(int(N)) + '\n')

                        # Check nextSeqNum and if it is larger than the last packet in the window update it to that packet
                        if nextSeqNum > base + N*pktLength:
                            nextSeqNum = base + N*pktLength


            # GBN Timeout
            elif timers[0] is not None:
                if currentTime - timers[0] > timeOut:

                    timeOutCount += 1

                    nextSeqNum = base + pktLength

                    print('\n**TIMEOUT OCURRED IN GBN MODE, RESETTING NEXTSEQNUM TO BASE: ' + str(nextSeqNum) + '\n')

                    # Make the repeated packet into tcp format
                    pkt = make_tcp_pkt(base, recvSeq, data = pktList[int((base-startSeq)/pktLength)])

                    # Resend the timed out packet
                    clientSocket.sendto(pkt, addr)

                    # Update state and values
                    N, ssthresh, state, timers = update_state_timeout(N, ssthresh, state, timers)

                    # Reset the timer:
                    timers[0] = time()

                    print('Currently in ' + state + ' mode')
                    print('Window size is: ' + str(int(N)) + '\n')


                if base >= finalBase and timeOutCount > 5:
                    print('\nLast packet sent 6 times, ASSUMING RECEIVED, EXITING!')
                    break

        else:

            # Update current time
            currentTime = time()

            # Artificially drop the ack packet for testing purposes
            if random()*100 < LOSS_PROB:
                continue
            else:
                # Convert the bytes type object to a bytearray to make it mutable
                ack = bytearray(ack)

                # Check integrity of the packet
                recvSeq, seqNum, flow = check_tcp(ack)

                # If the packet is intact and the acked packet is equal to or larger than the packet before the current base, its relevant
                if seqNum != None and seqNum > base:

                    print('Ack received for packet with sequence number: ' + str(seqNum - pktLength))

                    # Calculate the difference between the new requested base and the old base
                    delta = seqNum - base

                    # Make the base equal to the next seq number to be sent if the seq. number is larger than the base
                    base = seqNum

                    # In case the nextSeqNum has fallen behind (possibly due to it being reset by a timeout or lost packets) update it if necessary
                    if nextSeqNum < base:
                        nextSeqNum = base

                    print('New Base is ' + str(base) + ' and Next Sequence to Send is ' + str(nextSeqNum))

                    if delta/pktLength <= int(N):
                        if timers[int((delta/pktLength)-1)] is not None:
                            # Recalculate timeout value
                            timeOut, estimatedRTTPrev, devRTTPrev = time_out_update(currentTime - timers[int((delta/pktLength)-1)], estimatedRTTPrev, devRTTPrev)

                    # Reorganize the timers for the packets in the window
                    for i in range(ceil(delta/pktLength)):
                        timers.pop(0)
                        timers.append(None)

                    # Restart the time out counter
                    timeOutCount = 0

                    # Check state and proceed accordingly
                    if state == 'slow start':
                        # Increase window size by 1
                        N += 1 * delta/pktLength

                        # Update the size of the timers array to match the window size
                        timers.append(None)

                        # Check if it meets the requirement to change state
                        if ssthresh is not None:

                            if N >= ssthresh:

                                state = 'congestion avoidance'

                    elif state == 'congestion avoidance':
                        # Increase window size by 1/N
                        N += (1/N) * delta/pktLength

                        # Check if the window size has become larger than the number of available timers and increase accordingly
                        for i in range(int(N) - len(timers)):
                            timers.append(None)

                    print('Currently in ' + state + ' mode')
                    print('Window size is: ' + str(int(N)) + '\n')

    close_connection_client(clientSocket, addr, base, seqNum, timeOut)
        
def receive_gbn(socket):

    # Initialize timeout
    timeOut = 0.5

    # Initialize packet list
    pktList = []

    # Wait for handshake and header
    recvSeq, startSenderSeq, numPkts, pktSize, name = handshake_server(socket)

    print('Sender random initial sequence number is: ' + str(startSenderSeq) + '\n')

    # Initialize a buffer
    buffer = bytearray((pktSize + HEADER_SIZE) * 10)

    # Initialize the expected next sequence number to the starting sequence for the sender
    nextSeqNum = startSenderSeq

    # Start transmission timer
    start = time()

    # Current buffer position
    buffIndex = 0

    # Set socket to non-blocking
    socket.setblocking(0)
    
    while nextSeqNum < numPkts*pktSize+startSenderSeq:

        try:

            # Receive a msg from the client and store the received datagram
            numRead, clientAddress = socket.recvfrom_into(memoryview(buffer)[buffIndex:])

        except OSError as e:

            if buffIndex >= pktSize + HEADER_SIZE or nextSeqNum + pktSize == numPkts*pktSize+startSenderSeq:

                # Grab first message within buffer
                msg = [buffer.pop(0) for i in range(pktSize + HEADER_SIZE)]
                [buffer.append(0) for i in range(pktSize + HEADER_SIZE)]
                buffIndex -= pktSize + HEADER_SIZE
                buffSpace = len(buffer) - buffIndex

                # Convert the bytes type object to a bytearray to make it mutable
                msg = bytearray(msg)

                # Check integrity of msg
                senderSeq, recvSeq, flow = check_tcp(msg)

                # Calculate received packet index
                if senderSeq != None:

                    # Generate an index for the storage list with base 0
                    index = ceil((senderSeq-startSenderSeq)/pktSize)

                    # Check the sequence of message and add to the pktList if first time message is received
                    nextSeqNum = check_seq(senderSeq, nextSeqNum, pktList, index, startSenderSeq, pktSize, msg)

                    # Send ack for the pkt before nextSeqNum as the last pkt received intact
                    socket.sendto(make_tcp_pkt(recvSeq, nextSeqNum, syn = False, fin = False, finAck = False, flow = buffSpace, data = bytearray()), clientAddress)

                    print('Ack sent acknowledging packet with sequence: ' + str(nextSeqNum-pktSize))
                    print('Current free buffer space: ' + str(buffSpace) + '\n')
            
        else:

            # Artificially drop the ack packet for testing purposes
            if random()*100 < LOSS_PROB:
                # Drop the read data
                for i in range(buffIndex, numRead):
                    buffer[i] = 0
                continue
            else:
                buffIndex += numRead
        

    close_connection_server(socket, nextSeqNum, timeOut)

    # Stop transmission timer
    stop = time()

    return (name, binaryFromPackets(pktList), stop-start)