#! /usr/bin/env python3

from socket import *

# Obtain the name of the local host 
serverName = gethostname()

# Declare the port number of the server that the client will be communicating with
serverPort = 12000

# Assign a socket to the client using the arguments for a IPV4 address (AF_INET) and UDP protocol (SOCK_DGRAM) 
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Request a message to send from the user through terminal
message = input('Input Message: ')

# Encode the message into a datagram and send it to the server 
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Receive a reply from the server and store the received datagram and the address of the sender (tuple)
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

# Decode the received message back into a string and print it to terminal
print (modifiedMessage.decode())

# Close the client's socket
clientSocket.close()

