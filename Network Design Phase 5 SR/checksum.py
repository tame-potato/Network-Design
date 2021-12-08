#! /usr/bin/env python3

# Size of each word used for checksum calculations
SIZE_OF_WORD = 2

# Receives two lists containing 2 bytes each and perform a sum returning the result in the same format as the input
def bitwiseSum(a, b):

    c = []
    of = 0

    for i in range(SIZE_OF_WORD):

        c.insert(0, a[i]+b[i]+of)

        while c[0] > 255:

            c[0] -= 256
            of = 1

            if i < SIZE_OF_WORD-1:
                break
            else:
                c = bitwiseSum(c, [0,of])

    return c
                

# Receives a bytearray and divides it into an array of arrays of length SIZE_OF_WORD
# If not divisible by SIZE_OF_WORD, pads last element with null byte at the back
def groupChecksum(pkt):

    groupList = [pkt[i:i+SIZE_OF_WORD] for i in range(0, len(pkt), SIZE_OF_WORD)]

    if len(pkt)%2 != 0:
        groupList[-1].append(0)

    return groupList


# Receive a packet and generate a checksum which is returned
def makeChecksum(pkt):

    wordList = groupChecksum(pkt)

    if len(wordList) > 1:

        result = bitwiseSum(wordList[0], wordList[1])

        for i in range(2, len(wordList)):

            result = bitwiseSum(result, wordList[i])

    else:
        result = []
        result.extend(wordList[0])

    return result


# Receives a packet without a checksum and inserts a 2 byte checksum at the front
def addChecksum(pkt):

    checksum = makeChecksum(pkt)

    for i in range(SIZE_OF_WORD):
        pkt.insert(0,checksum[i])


# Receives a packet as a bytearray, extracts its checksum, generates a checksum from the remainder, compares the checksums, and returns a bool 
def compareChecksum(pkt):

    includedChecksum = [pkt.pop(1-i) for i in range(2)]

    generatedChecksum = makeChecksum(pkt)

    #print('Generated Checksum ' + str(generatedChecksum))
    #print('Included Checksum ' + str(includedChecksum))

    return includedChecksum == generatedChecksum

    

