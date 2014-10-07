#!/usr/bin/env python
    
import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class SampleListener(Leap.Listener):
    def __init__(self):
        super(SampleListener, self).__init__()
        self.enabled = False
        self.rp_normal = None
        self.lp_normal = None
        self.rp_pos = None
        self.lp_pos = None

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()
        gestures = frame.gestures()
        for gesture in gestures:
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and gesture.state == Leap.Gesture.STATE_STOP:
                self.enabled = not self.enabled
                return

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

        print self.rp_pos

#        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#            frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

listener = SampleListener()
controller = Leap.Controller()
controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
controller.add_listener(listener)

controller.config.set("Gesture.Swipe.MinLength", 100.0)  # in mm
controller.config.set("Gesture.Swipe.MinVelocity", 750)  # in mm/s
controller.config.save()

try:
    sys.stdin.readline()
except KeyboardInterrupt:
    pass
