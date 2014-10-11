#!/usr/bin/env python

import socket
from time import sleep

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.10.15.158", 8888))

steps = list(range(-20, 22, 2))
bsteps = list(range(-20, 22, 2))
bsteps.reverse()

while True:
    for i in steps:
       s.send("speed0 %.8f;" % (i / 10.0))
       sleep(.5)
    for i in bsteps:
       s.send("speed0 %.8f;" % (i / 10.0))
       sleep(.5)
