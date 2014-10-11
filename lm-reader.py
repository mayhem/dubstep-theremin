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
        self.speed1 = 1
        self.cross_fade = 100
        #self.vol_track0 = 100
        #self.vol_track1 = 0

        #Defining the track selection grid
        self.CONST_GRID_COL_NUMBER = 3
        self.CONST_GRID_LINE_NUMBER = 3
        self.instrumentnumber = self.CONST_GRID_COL_NUMBER * self.CONST_GRID_LINE_NUMBER

        #Defining tracks and if they're selected or not
        self.track1 = 0
        self.track2 = 0
        self.track0_selected = False
        self.track1_selected = False
        self.selected_track = 0
        self.PlayModeTrack0 = True
        self.PlayModeTrack1 = True

        #controlling names
        self.track_selectionmode_enabled = False
        self.controlling_enabled = False

        #DebugMode
        self.DebugMode = True
        

        #Setting OSC
        #Rob's IP
        self.dest = "10.10.15.158"
        #Cedric's IP
        #self.dest = "localhost"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.dest, 8888))
        



    def on_connect(self, controller):
        print "Connected  -  Swipe to start"



    def select_track(self, st_position):
        track_selection_x = 0
        track_selection_y = 0
        track_x = 0
        track_y = 0

        track_selection_x = min(100, max(0,(st_position.x + 150)/3.5 ))
        track_selection_y = min(100, max(0,(st_position.y - 40)/3.6 ))
        track_x = floor(track_selection_x / (100 / self.CONST_GRID_COL_NUMBER)) 
        track_y = floor(track_selection_y / (100 / self.CONST_GRID_LINE_NUMBER)) 
        return track_x + (track_y * self.CONST_GRID_COL_NUMBER)
        


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
                if not self.DebugMode:
                    self.s.send("Start;")
                    print "Start"
                return
            '''
            if gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SWIPE and gesture.state == Leap.Gesture.STATE_STOP and self.enabled:
                self.enabled = False
                print "Control mode disactivated"
                if not self.DebugMode:
                    self.s.send("Stop;")
                    print "Stop"
                return
            '''

            #Track selection entering    
            if (gesture.is_valid and gesture.type == Leap.Gesture.TYPE_CIRCLE and gesture.state == Leap.Gesture.STATE_STOP and self.enabled 
                and not self.track_selectionmode_enabled):
                self.track0_selected = False
                self.track1_selected = False
                self.track_selectionmode_enabled = True
                print "Please select the 1st track"
                return

            #Track1 selection
            if (gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and gesture.state == Leap.Gesture.STATE_STOP 
                and self.enabled and self.track_selectionmode_enabled and not self.track0_selected):
                self.track1 = self.select_track(Leap.ScreenTapGesture(gesture).position)
                self.track0_selected = True
                print "track 1 selected :" + str(self.track1)
                print ""
                print "--------------------------------------"
                print "Please select the 2nd track now"
                return
        
            #Track2 selection
            if (gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and gesture.state == Leap.Gesture.STATE_STOP 
                and self.enabled and self.track_selectionmode_enabled and self.track0_selected and not self.track1_selected):
                self.track2 = self.select_track(Leap.ScreenTapGesture(gesture).position)
                self.track1_selected = True
                self.track_selectionmode_enabled = False
                self.controlling_enabled = True
                print "track 2 selected :" + str(self.track2)
                print ""
                print "--------------------------------------"
                return

            
            #Switching from a track to the other
            if (gesture.is_valid and gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and self.enabled and self.track0_selected and
                self.track1_selected and not self.track_selectionmode_enabled):
                if self.selected_track == 0:
                    self.selected_track = 1
                    print "Track 1 selected"
                    return
                else:
                    self.selected_track = 0
                    print "Track 0 selected"
                    return

            
            #Do play/pause on the track
            if (gesture.is_valid and gesture.type == Leap.Gesture.TYPE_KEY_TAP and self.enabled and self.track0_selected and
                self.track1_selected and not self.track_selectionmode_enabled):
                #Q : what do i do? Only send a message like Play/Pause, or do i send Play and Pause separately?
                if self.selected_track == 0:
                    if self.PlayModeTrack0 == False:
                        print "Play track 0"
                        #self.s.send("Play " + str(self.selected_track) + ";")
                    else:
                        print "Pause track 0"
                        #self.s.send("Pause " + str(self.selected_track) + ";")
                    self.PlayModeTrack0 = not self.PlayModeTrack0
                else:
                    if self.PlayModeTrack1 == False:
                        print "Play track 1"
                        #self.s.send("Play " + str(self.selected_track) + ";")
                    else:
                        print "Pause track 1"
                        #self.s.send("Pause " + str(self.selected_track) + ";")
                    self.PlayModeTrack1 = not self.PlayModeTrack1

                return
            

        handlist = frame.hands
        for hand in handlist:
            if hand.is_valid and self.controlling_enabled:
                if hand.is_right:
                    self.rp_normal = hand.palm_normal
                    self.rp_pos = hand.palm_position
                    #print self.rp_normal
                    
                    #Master Volume setting
                    if self.rp_normal.z < -0.8:
                        self.volume = min(100, max(0, (self.rp_pos.y - 40)/3.6))
                        print "volume: " + str(self.volume)
                        if not self.DebugMode:
                            self.s.send("volume " + str(self.volume) + ";")
                            
                        

                    #Tracks volume relative settings
                    if self.rp_normal.x < -0.8:
                        self.cross_fade = min(1, max(0, (self.rp_pos.x + 200)/400))
                        #self.vol_track0 = min(100, max(0, (self.rp_pos.x + 200)/4))
                        #self.vol_track1 = 100 - self.vol_track1
                        print "cross_fade " + str(self.cross_fade)
                        if not self.DebugMode:
                            self.s.send("crossfade " + str(self.cross_fade) + ";")
                        
                            


                    # track 1 speed setting
                    if self.rp_normal.y < -0.8:
                        self.speed0 = min(2, max(-2, (self.rp_pos.z * (-1) + 120)/40 - 2))
                        print "speed0: " + str(self.speed0)
                        if not self.DebugMode:
                            self.s.send("speed0 " + str(self.speed0) + ";")


                if hand.is_left:
                    self.lp_normal = hand.palm_normal
                    self.lp_pos = hand.palm_position

                    # track 2 speed setting
                    if self.lp_normal.y < -0.8:
                        self.speed1 = min(2, max(-2, (self.lp_pos.z * (-1) + 120)/40 - 2))
                        print "speed1: " + str(self.speed1)
                        if not self.DebugMode:
                            self.s.send("speed1 " + str(self.speed1) + ";")
                            
                            
                        
        

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
