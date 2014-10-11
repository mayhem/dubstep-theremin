#!/usr/bin/env python

import socket
from time import sleep

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.10.15.158", 8888))

steps = list(range(-10, 22, 2))
bsteps = list(range(-10, 22, 2))
bsteps.reverse()

s.send("volume .5;")
s.send("speed0 1;")
s.send("speed1 1;")

while 0:
    for i in steps:
       s.send("speed0 %.8f;" % (i / 10.0))
       sleep(1)
    for i in bsteps:
       s.send("speed0 %.8f;" % (i / 10.0))
       sleep(1)

while True:
    for i in range(0, 11):
       s.send("crossfade %.8f;" % (i / 10.0))
       sleep(1)
