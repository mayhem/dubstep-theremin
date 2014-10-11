#!/usr/bin/env python
    
import os, sys, inspect, thread, time, math, socket
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from math import floor
from time import sleep

class SampleListener(Leap.Listener):
    def __init__(self):
        super(SampleListener, self).__init__()
        self.enabled = False
        self.rp_normal = None
        self.lp_normal = None
        self.rp_pos = None
        self.lp_pos = None
        self.lastFrameID = 0

        #DJing names
        self.volume = 0
        self.speed0 = 1

        #Defining the track selection grid
        self.CONST_GRID_COL_NUMBER = 3
        self.CONST_GRID_LINE_NUMBER = 3
        self.instrumentnumber = self.CONST_GRID_COL_NUMBER * self.CONST_GRID_LINE_NUMBER

        #Defining tracks and if they're selected or not
        self.track1 = 0
        self.track2 = 0
        self.track1_selected = False
        self.track2_selected = False
        self.selected_track = 1
        self.track_selectionmode_enabled = False
        

        #Setting OSC
        #Rob's IP
        self.dest = "10.10.15.158"
        #Cedric's IP
        #self.dest = "10.10.15.159"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.dest, 8888))
        



    def on_connect(self, controller):
        print "Connected  -  Swipe to start"



    def select_track1(self, st_position):
        track_selection_x = 0
        track_selection_y = 0
        track_x = 0
        track_y = 0

        track_selection_x = min(100, max(0,(st_position.x + 150)/3.5 ))
        track_selection_y = min(100, max(0,(st_position.y - 40)/3.6 ))
        track_x = floor(track_selection_x / (100 / self.CONST_GRID_COL_NUMBER)) 
        track_y = floor(track_selection_y / (100 / self.CONST_GRID_LINE_NUMBER)) 
        self.track1 = track_x + (track_y * self.CONST_GRID_COL_NUMBER)
        self.track1_selected = True

        print "track 1 selected :" + str(self.track1)
        print ""
        print" --------------------------------------"
        print "Please select the 2nd track now"


    def select_track2(self, st_position):
        track_selection_x = 0
        track_selection_y = 0
        track_x = 0
        track_y = 0

        track_selection_x = min(100, max(0,(st_position.x + 150)/3.5 ))
        track_selection_y = min(100, max(0,(st_position.y - 40)/3.6 ))
        track_x = floor(track_selection_x / (100 / self.CONST_GRID_COL_NUMBER)) 
        track_y = floor(track_selection_y / (100 / self.CONST_GRID_LINE_NUMBER)) 
        self.track2 = track_x + (track_y * self.CONST_GRID_COL_NUMBER)
        self.track2_selected = True

        self.track_selectionmode_enabled = False
    
        print "track 2 selected :" + str(self.track2)
        print ""
        print" --------------------------------------"


    def on_frame(self, controller):

        frame = controller.frame()
        if frame.id == self.lastFrameID:
            return

        
        gestures = frame.gestures()
        for gesture in gestures:
            #Controller activation
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and gesture.state == Leap.Gesture.STATE_STOP and not self.enabled:
                self.enabled = True
                print "Welcome!"
                print ""
                print "--------------------------------------"
                print "Enter track selection mode => make a circle with a finger"
                print "Control volume             => use your right hand open over the controller, go up & down"
                print "Control speed              => use your left hand open over the controller, go forward & backward"
                print "desactivate                => swipe again"
                print "--------------------------------------"
                return

            #if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and gesture.state == Leap.Gesture.STATE_STOP and self.enabled:
             #   self.enabled = False
             #   print "Control mode disactivated"
             #   return

            #Track selection entering    
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_CIRCLE and gesture.state == Leap.Gesture.STATE_STOP and self.enabled and not self.track_selectionmode_enabled:
                self.track1_selected = False
                self.track2_selected = False
                self.track_selectionmode_enabled = True
                print "Please select the 1st track"
                return

            #Track1 selection
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and gesture.state == Leap.Gesture.STATE_STOP and self.enabled and self.track_selectionmode_enabled and not self.track1_selected:
                self.select_track1(Leap.ScreenTapGesture(gesture).position)
                return
        
            #Track2 selection
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and gesture.state == Leap.Gesture.STATE_STOP and self.enabled and self.track_selectionmode_enabled and self.track1_selected and not self.track2_selected:
                self.select_track2(Leap.ScreenTapGesture(gesture).position)
                return
            '''
            #Switching from a track to the other
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and self.enabled and self.track1_selected and self.track2_selected:
                if self.selected_track == 1:
                    self.selected_track = 2
                    print "Track 2 selected"
                    return
                else:
                    self.selected_track = 1
                    print "Track 1 selected"
                    return

            '''
            #Do play/pause on the track

            

        handlist = frame.hands
        for hand in handlist:
            if hand.is_valid:
                if hand.is_right:
                    self.rp_normal = hand.palm_normal
                    self.rp_pos = hand.palm_position
                    #Volume setting
                    self.volume = min(100, max(0, (self.rp_pos.y - 40)/3.6))
                    #print "volume: " + str(self.volume)
                    self.s.send("volume " + str(self.volume) + ";")

                if hand.is_left:
                    self.lp_normal = hand.palm_normal
                    self.lp_pos = hand.palm_position
                    #Speed setting
                    self.speed0 = min(2, max(-2, (self.lp_pos.z * (-1) + 120)/40 - 2))
                    #print "speed0: " + str(self.speed0)
                    self.s.send("speed0 " + str(self.speed0) + ";")
        
        self.lastFrameID = frame.id
        


        if not self.enabled:
            return

#        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#            frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

listener = SampleListener()
controller = Leap.Controller()
controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
controller.add_listener(listener)

controller.config.set("Gesture.Swipe.MinLength", 100.0)  # in mm
controller.config.set("Gesture.Swipe.MinVelocity", 750)  # in mm/s
controller.config.set("Gesture.ScreenTap.MinForwardVelocity", 20.0) # in mm/s
controller.config.save()

try:
    sys.stdin.readline()
except KeyboardInterrupt:
    pass
