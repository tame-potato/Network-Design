#! /usr/bin/env python3

SIZE_OF_WORD = 2

# Receive two lists containing 2 bytes each and perform a sum returning the result in the same format as the input
def bitwiseSum(a, b):

    bits = '0000000000000000'
    overflow = '0'

    aBits = [int2bitString(i) for i in a]
    bBits = [int2bitString(i) for i in b]

    for i in range(SIZE_OF_WORD):
        of = '0'

        for j in range(8):

            if of == '1':
                bit, of = charXOR(aBits[i][j], i)

            bit, of = charXOR(aBits[i][j],bBits[i][j])



# Receives a bytearray and divides it into an array of arrays of length SIZE_OF_WORD
# If not divisible by SIZE_OF_WORD, does not include remainder elements
def groupChecksum(pkt):

    groupList = [pkt[i:i+SIZE_OF_WORD] for i in range(0, len(pkt), SIZE_OF_WORD)]

    return groupList


# Receives a packet as a bytearray and generates a checksum which is then added to the back of the bytearray
def addChecksum(pkt):

    wordList = groupChecksum(pkt)

    for i in range(len(pkt) / 4):


# Receives a packet as a bytearray, extracts its checksum, generates a checksum from the remainder, compares the checksums, and returns a bool 
def compareChecksum(pkt):

    checksum = [pkt.pop(0) for i in range(2)]

