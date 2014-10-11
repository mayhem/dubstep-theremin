#!/usr/bin/env python
    
import os, sys, inspect, thread, time, math, OSC
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from math import floor

class SampleListener(Leap.Listener):
    def __init__(self):
        super(SampleListener, self).__init__()
        self.enabled = False
        self.rp_normal = None
        self.lp_normal = None
        self.rp_pos = None
        self.lp_pos = None
        self.volume = 0

        #Defining the instrument selection grid
        self.CONST_GRID_COL_NUMBER = 2
        self.CONST_GRID_LINE_NUMBER = 2
        self.instrumentnumber = self.CONST_GRID_COL_NUMBER * self.CONST_GRID_LINE_NUMBER
        self.st_position = None
        self.instrument_selection_x = 0
        self.instrument_selection_y = 0
        self.instrument_x = 0
        self.instrument_y = 0
        self.instrument = 0

        #Setting OSC
        #Rob's IP
        self.dest = "10.10.15.158", 57120
        #Cedric's IP
        #self.dest = "10.10.15.159", 7777
        self.c = OSC.OSCClient()
        self.c.connect(self.dest)
        
        #self.instrumentlist = List[i for i in range(self.instrumentnumber)]

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()
        gestures = frame.gestures()
        for gesture in gestures:
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and gesture.state == Leap.Gesture.STATE_STOP:
                self.enabled = not self.enabled
                return
            #Instrument selection    
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and gesture.state == Leap.Gesture.STATE_STOP:
                self.st_position = Leap.ScreenTapGesture(gesture).position
                self.instrument_selection_x = min(100, max(0,(self.st_position.x + 150)/3.5 ))
                self.instrument_selection_y = min(100, max(0,(self.st_position.y - 40)/3.6 ))
                self.instrument_x = floor(self.instrument_selection_x / (100 / self.CONST_GRID_COL_NUMBER)) + 1
                self.instrument_y = floor(self.instrument_selection_y / (100 / self.CONST_GRID_LINE_NUMBER)) + 1
                self.instrument = self.instrument_x * self.instrument_y
                print "instrmuent selected :" + str(self.instrument)



        if not self.enabled:
            return
        

        handlist = frame.hands
        for hand in handlist:
            if hand.is_valid:
                if hand.is_right:
                    self.rp_normal = hand.palm_normal
                    self.rp_pos = hand.palm_position
                if hand.is_left:
                    self.lp_normal = hand.palm_normal
                    self.hp_pos = hand.palm_position
        
        volume = min(100, max(0, (self.rp_pos.y - 40)/3.6))
        print volume
        self.msg = OSC.OSCMessage()
        self.msg.setAddress("/volume")
        self.msg.append(volume)
        self.c.send(self.msg)


#        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#            frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

listener = SampleListener()
controller = Leap.Controller()
controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
controller.add_listener(listener)

controller.config.set("Gesture.Swipe.MinLength", 100.0)  # in mm
controller.config.set("Gesture.Swipe.MinVelocity", 750)  # in mm/s
controller.config.set("Gesture.ScreenTap.MinForwardVelocity", 20.0) # in mm/s
controller.config.save()

try:
    sys.stdin.readline()
except KeyboardInterrupt:
    pass
