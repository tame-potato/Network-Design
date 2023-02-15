import random
import copy

# Corruption probability 0-100
ACK_CORRUPT = 30
DATA_CORRUPT = 0
# Loss probability
ACK_LOSS = 0
DATA_LOSS = 0


def findChecksum(data):
    # Dividing data packets of 2 bytes (16 bits) and Calculating the sum of packets
    Sum = 0
    for i in range(0, len(data), 2):
        Sum += int.from_bytes(data[i:i + 2], 'big')

    Sum = bin(Sum)[2:]  # converting to binary

    # Adding the overflow bits
    while len(Sum) > 16:
        x = len(Sum) - 16
        Sum = bin(int(Sum[0:x], 2) + int(Sum[x:], 2))[2:]

    if len(Sum) < 16:
        Sum = '0' * (16 - len(Sum)) + Sum

    # Calculating the complement of sum
    Checksum = ''
    for i in Sum:
        if i == '1':
            Checksum += '0'
        else:
            Checksum += '1'

    Checksum = bytes(int(Checksum[i: i + 8], 2) for i in range(0, len(Checksum), 8))
    return Checksum


def makePacket(Checksum, seq, data):
    packet = bytearray()
    packet.append(Checksum[0])
    packet.append(Checksum[1])
    seq_byte = abs(seq).to_bytes(2, byteorder='big')
    packet.append(seq_byte[0])
    packet.append(seq_byte[1])
    for i in range(len(data)):
        packet.append(data[i])

    return packet


def corruptPacket(packet):
    packet = bytearray(packet)
    if random.randint(0, 100) < ACK_CORRUPT:
        # this ensures corruption if first two bytes (checksum) both be 0
        packet[0] = 0
        packet[1] = 0
    if random.randint(0, 100) < DATA_CORRUPT:
        # this ensures corruption if first two bytes (checksum) both be 0
        packet[0] = 0
        packet[1] = 0
    return packet


def lossPacket():
    if random.randint(0, 100) < ACK_LOSS:
        return True
    elif random.randint(0, 100) < DATA_LOSS:
        return True
    return False


def corrupted(packet):
    received_Checksum = packet[0:2]
    msg_Checksum = findChecksum(packet[4:])
    if received_Checksum != msg_Checksum:
        return True
    else:
        return False


def has_seq(packet):
    received_seq = packet[2:4]
    received_seq = int.from_bytes(received_seq, byteorder='big')
    return received_seq


def binaryFromPackets(packetList):
    data = bytearray()
    for i in packetList:
        data.extend(i)
    return data
