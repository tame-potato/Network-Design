from socket import *
from GBN_functions import *

serverName = gethostname()
serverPort = 12001

receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind((serverName, serverPort))
# receiverSocket.settimeout()

receivedFile = input("Enter the name of the saved file: ")

data = []
nextSeq = 0
seqZero = True
ACK_checksum = findChecksum(b'ACK')

while True:
    message, clientAddress = receiverSocket.recvfrom(2048)
    message = bytearray(message)
    if message == b'FIN':
        # print("File receive complete")
        break

    if not lossPacket():
        # Artificially corrupt packets for testing purposes
        message = corruptPacket(message)
        # print("Received data seq: " + str(has_seq(message)))

        if not corrupted(message):

            if has_seq(message) == nextSeq:
                data.append(message[4:])
                ACK_pkt = makePacket(ACK_checksum, nextSeq, b'ACK')
                receiverSocket.sendto(ACK_pkt, clientAddress)
                nextSeq += 1

            else:
                ACK_pkt = makePacket(ACK_checksum, has_seq(message), b'ACK')
                receiverSocket.sendto(ACK_pkt, clientAddress)


fileData = binaryFromPackets(data)
data.clear()

newFile = open(receivedFile, 'wb')
newFile.write(fileData)
receiverSocket.close()
