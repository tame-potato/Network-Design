from socket import *
from GBN_functions import *
import time


serverName = gethostname()
serverPort = 12001
senderSocket = socket(AF_INET, SOCK_DGRAM)
senderSocket.setblocking(0)

dataSize = 1024   # checkSum [0:2], Sequence [2:4], Data [4:]
base = 0
nextSeq = 0
windowSize = 5
window = []
set_timeout = .05

filename = input("Enter the filename to be sent: ")
fileSent = False
openFile = open(filename, 'rb')

data = openFile.read(dataSize)
initializeTimer = True
timer = time.time()
while True:

    while nextSeq < base + windowSize and not fileSent:
        # print("packet sending")
        data = bytearray(data)
        sndpkt = makePacket(findChecksum(data), nextSeq, data)
        senderSocket.sendto(sndpkt, (serverName, serverPort))
        nextSeq += 1
        window.append(sndpkt)
        data = openFile.read(dataSize)
        if not data:
            fileSent = True

    if initializeTimer:
        startTimer = time.time()
        initializeTimer = False

    try:
        ACK_pkt = senderSocket.recv(2048)
        ACK_pkt = bytearray(ACK_pkt)
        if not lossPacket():
            ACK_pkt = corruptPacket(ACK_pkt)
            if not corrupted(ACK_pkt) and has_seq(ACK_pkt) == base:
                startTimer = time.time()
                # print("Receive ACK seq: " + str(base))
                base = has_seq(ACK_pkt) + 1
                del window[0]

    except:

        if time.time() - startTimer > set_timeout:
            # print("Timer timeout, Resending Seq: " + str(base) + '-' + str(nextSeq - 1))

            for i in window:
                senderSocket.sendto(i, (serverName, serverPort))

            startTimer = time.time()

    if not window and fileSent:
        senderSocket.sendto(b'FIN', (serverName, serverPort))
        # print("File sent complete")
        break
timer = time.time() - timer

print(timer)

openFile.close()

senderSocket.close()
