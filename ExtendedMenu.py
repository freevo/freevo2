# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os, copy, re

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd
import gui

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# XML parser for skin informations
sys.path.append('skins/xml/type1')
import xml_skin

rc   = rc.get_singleton()   # Create the remote control object
osd  = osd.get_singleton()  # Create the OSD object


class ExtendedMenu:
    view    = None
    info    = None
    listing = None
    
    # Parameters:
    #    - view: should be a class that inherits ExtendedMenuView
    #    - info: should be a class that inherits ExtendedMenuInfo
    #    - listing: should be a class that inherits ExtendedMenuListing
    def __init__(self, view, info, listing):
        self.view    = view
        self.info    = info
        self.listing = listing


    def refresh(self):
        self.clear()

        self.view.refresh()            
        self.info.refresh()
        self.listing.refresh()        
        osd.update()

    def clear(self):
        pass

    def eventhandler(self, event):
        if event == rc.MENU:
            if self.view.getVisible() == 1:
                self.view.setVisible(0)
            else:
                self.view.setVisible(1)

            if self.info.getVisible() == 1:
                self.info.setVisible(0)
            else:
                self.info.setVisible(1)

            self.refresh()
        elif event == rc.REFRESH_SCREEN:
            self.refresh()
        else:
            self.clear()
            t = self.listing.eventhandler(event)
            if t and len(t) == 2:
                to_view, to_info = t
            self.view.ToView(to_view)
            self.info.ToInfo(to_info)
            osd.update()
        return 0
    
    
class ExtendedMenuView:
    visible = 1
    
    def __init__(self, x=-1, y=-1, w=-1, h=-1):
        if x > -1:
            self.x = x
        if y > -1:
            self.y = y
        if w > -1:
            self.w = w
        if h > -1:
            self.h = h

    def setVisible(self, visible=1):
        self.visible = visible

    def getVisible(self):
        return self.visible

    # This should be implemented by the inherited class
    # Parameters:
    #    - ToView: string with cmd to view
    def ToView(self, to_view):
        pass

    # This should be implemented by the inherited class
    def refresh(self):
        pass

    
    


class ExtendedMenuInfo:
    visible = 1
    
    def __init__(self, x=-1, y=-1, w=-1, h=-1):
        if x > -1:
            self.x = x
        if y > -1:
            self.y = y
        if w > -1:
            self.w = w
        if h > -1:
            self.h = h

    def setVisible(self, visible=1):
        self.visible = visible

    def getVisible(self):
        return self.visible

    # This should be implemented by the inherited class
    # Parameters:
    #    - ToInfo: string with info to show
    def ToInfo(self, to_info):
        pass

    # This should be implemented by the inherited class
    def refresh(self):
        pass


    


class ExtendedMenuListing:
    visible = 1
    
    def __init__(self, x=-1, y=-1, w=-1, h=-1):
        if x > -1:
            self.x = x
        if y > -1:
            self.y = y
        if w > -1:
            self.w = w
        if h > -1:
            self.h = h

    def setVisible(self, visible=1):
        self.visible = visible

    def getVisible(self):
        return self.visible

    # This should be implemented by the inherited class
    # Parameters:
    #    - ToListing: string with listing to show
    def ToListing(self, to_listing):
        pass

    # This should be implemented by the inherited class
    # Parameters:
    #    - event: event to be parsed
    def eventhandler(self, event):
        pass
    

    # This should be implemented by the inherited class
    def refresh(self):
        pass

