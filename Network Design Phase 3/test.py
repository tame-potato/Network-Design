#! /usr/bin/env python3

def add_byte(array):
    x = 0
    array.insert(0,x)

seq = 1

seq = seq.to_bytes(1,'big')

array = bytearray()

print(array)

add_byte(array)

print(array)