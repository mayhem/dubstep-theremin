#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simpleOSC import initOSCClient, initOSCServer, setOSCHandler, sendOSCMsg, closeOSC, \
     createOSCBundle, sendOSCBundle, startOSCServer

def server():
    initOSCServer("0.0.0.0", 7777, 0)
    setOSCHandler('/volume', volume)
    setOSCHandler('/speed0', speed0)
    setOSCHandler('/speed1', speed1)
    startOSCServer()
        
def volume(addr, tags, data, source):
    print "volume:", data

def speed0(addr, tags, data, source):
    print "speed:", data

def speed1(addr, tags, data, source):
    print "speed:", data

if __name__ == '__main__': 
    server()
