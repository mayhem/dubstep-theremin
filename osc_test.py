#!/usr/bin/env python

import OSC

dest = '127.0.0.1', 7777

c = OSC.OSCClient()
c.connect(dest)

# single message
msg = OSC.OSCMessage()
msg.setAddress("/volume") 
msg.append(50)
c.send(msg)
