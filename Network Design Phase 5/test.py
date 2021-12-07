#! /usr/bin/env python3

import socket

s1, s2 = socket.socketpair()

s1.send(b'Mary had a little lamb')
s1.send(b'This is number 2')

b1 = bytearray(50)

s2.recv_into(b1, 22)

print(b1)

