#if 0 /*
# -----------------------------------------------------------------------
# ExtendedMenu_Image.py - Image Browser
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif


# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys
import os
import copy
import re

# Various utilities
import util


# The OSD class, used to communicate with the OSD daemon
import osd
import gui
import skin
import ExtendedMenu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

import config

rc   = rc.get_singleton()   # Create the remote control object
osd  = osd.get_singleton()  # Create the OSD object
skin = skin.get_singleton() # Create the Skin object


DEBUG = config.DEBUG


class ExtendedMenu_Image(ExtendedMenu.ExtendedMenu):
    """
    Handles the 3-view menu 'ExtendedMenu_Image' with the following areas:
       * View: shows the image preview
       * Info: shows info about the image/dir/playlist
       * Listing: shows the list of files in the current dir and handles navigation
    """
    
    def refresh(self):
        """
        refreshes the ExtendedMenu_Image screen
        """
        skin.DrawImage()
        self.view.refresh()
        self.info.refresh()
        self.listing.refresh()
        osd.update()


    def clear(self):
        """
        clear the ExtendedMenu_Image screen
        """
        skin.DrawImage()
        

    def eventhandler(self, event):
        """
        handles the events that concerns the ExtendedMenu_Image
        They are:
           * DISPLAY: toggle normal/expanded display mode
           * REFRESH_SCREEN: refreshes the screen
           * others: all but the IDENTIFY_MEDIA will be passed to the ExtendedMenuListing_Image
        """
        if event == rc.DISPLAY:
            if self.view.getVisible() == 1:
                self.view.setVisible(0)
            else:
                self.view.setVisible(1)

            if self.info.getVisible() == 1:
                self.info.setVisible(0)
            else:
                self.info.setVisible(1)

            if skin.DrawImage_getExpand() == 1:
                skin.DrawImage_setExpand(0)
            else:
                skin.DrawImage_setExpand(1)

            self.refresh()
        elif event == rc.REFRESH_SCREEN:
            self.refresh()
        elif event != rc.IDENTIFY_MEDIA:
            self.clear()
            t = self.listing.eventhandler(event)
            if t and isinstance(t,tuple) and len(t) == 2:
                to_view, to_info = t
                self.view.ToView(to_view)
                self.info.ToInfo(to_info)
                osd.update()
            else:
                if t == 2: # refresh
                    self.refresh()
                return t
        return 0
    



class ExtendedMenuView_Image(ExtendedMenu.ExtendedMenuView):
    """
    Handles the View area from this ExtendedMenu_Image
    """
    last_to_view = None
    
    # Parameters:
    #    - ToView: string with cmd to view
    def ToView(self, to_view):
        """
        Displays the 'to_view' in the View area
        """
        self.last_to_view = to_view
        if self.getVisible() == 1:
            skin.DrawImage_View(to_view)

    def refresh(self):
        """
        refreshes the View area
        """
        self.ToView(self.last_to_view)


class ExtendedMenuInfo_Image(ExtendedMenu.ExtendedMenuInfo):
    """
    Handles the Info area from this ExtendedMenu_Image
    """
    last_to_info = None
    
    # Parameters:
    #    - ToInfo: string with cmd to info
    def ToInfo(self, to_info):
        """
        Displays the 'to_info' in the Info area
        """
        self.last_to_info = to_info
        if self.getVisible() == 1:
            skin.DrawImage_Info(to_info)
                             

    def refresh(self):
        """
        refreshes the View area
        """
        self.ToInfo(self.last_to_info)



class ExtendedMenuListing_Image(ExtendedMenu.ExtendedMenuListing):
    """
    Handles the Listing area from this ExtendedMenu_Image
    """    
    base_listing = None # to hold the listing from config file
    last_to_listing = [ None, None, None ]


    # Parameters:
    #    - to_listing: (images, start_image, selected_image_pos, parent) to listing
    def ToListing(self, to_listing):
        """
        Displays the 'to_listing' in the Listing area        
        """
        self.last_to_listing = to_listing

        n_cols = skin.DrawImage_getCols()
        n_rows = skin.DrawImage_getRows()

        if not to_listing[0]:
            if self.getVisible() == 1:
                skin.DrawImage_Listing(None)
            return

        # this is the base listing?
        # We should know 'cause this dir is 'fake' and we must remember this listing
        if self.base_listing == None and to_listing[0][0].parent.parent == None:
            self.base_listing = to_listing[0]

        sel_pos = to_listing[2]
        if sel_pos != None:
            selected_image = to_listing[0][sel_pos]
        else:
            selected_image = None

        # we will communicate with the skin via a listing like this:
        #    table = [ selected_image, items_to_display , [ up, down] ]
        # where:
        #    selected_image: is the selected item (DirItem,ImageItem, ...)
        #    items_to_display: is the array with the items we want to display
        #    up|dow: booleans to indicate the listing can go up/down
        table = [ ]
        table += [ selected_image ]

        items_to_display = [ [ ] ]
        nr = 0
        nc = 0
        starter = to_listing[1]

        for i in range(starter, len(to_listing[0])):
            if nc >= n_cols:
                nc = 0
                nr += 1
                if nr < n_rows:
                    items_to_display += [ [ ] ]
                else:
                    break
            items_to_display[nr] += [ to_listing[0][i] ]
            nc += 1

        up = 0            
        if starter > 0:
            up = 1

        down = 0
        if starter + n_cols * n_rows < len(to_listing[0]):
            down = 1

        table += [ items_to_display ]
        table += [  [ up, down ] ]

        if self.getVisible() == 1:
            skin.DrawImage_Listing(table)


    
    def refresh(self):
        self.ToListing(self.last_to_listing)
    

    def eventhandler(self, event):
        """
        handles the events that concerns the ExtendedMenu_Image
        They are:
           * RIGHT|LEFT|UP|DOWN: move
           * SELECT: show options for the selected menu item
           * PLAY: play(or view or enter) the selected menu item
           * EXIT|MENU: back to the previous menu listing
        """
        if event == rc.RIGHT:
            return self.event_ItemRight()
        if event == rc.LEFT:
            return self.event_ItemLeft()
        if event == rc.DOWN:
            return self.event_ItemDown()
        if event == rc.UP:
            return self.event_ItemUp()
        elif event == rc.SELECT or event == rc.PLAY:
            sel_pos = self.last_to_listing[2]
            if self.last_to_listing[0]:
                sel_item = self.last_to_listing[0][ sel_pos ]
                if sel_item.type == 'dir':
                    items = sel_item.cwd()
                    self.ToListing([ items, 0, 0, sel_item])
                    if items and len(items) > 0:
                        return self.fix_return_tuple(items[0])
                    else:
                        return 2
                if sel_item.type == 'image':
                    sel_item.view()
                    return 0
                if sel_item.type == 'playlist':
                    sel_item.play()
                    return 0

        elif event == rc.EXIT or event == rc.MENU:
            parent = self.last_to_listing[3] # the parent dir

            if parent and parent.parent:
                if parent.parent.dir == '':
                    items = self.base_listing # the initial fake listing (from config)
                else:
                    items = parent.parent.cwd() # the parent listing, from the parent.parent dir
            else:
                return 1 # exit

            self.ToListing([ items, 0, 0 , items[0].parent])
            return self.fix_return_tuple(items[0])
        else:
            print 'No action defined to event: "%s"' % (event)
            return None


    def fix_return_tuple(self, image):
        info = None
        view = None
        if image.type == 'image':
            info = [ 'image', image.name, image.filename, image.binsdesc, image.binsexif ]
            orientation = None
            if 'Orientation' in image.binsexif:
                orientation = image.binsexif['Orientation']
            view = [ 'image', image.filename, orientation ]
        elif image.type == 'dir':
            info = [ 'dir', image.name, image.dir ]
            view = [ 'dir' ]
        elif image.type == 'playlist':
            info = [ 'playlist', image.name, image.filename, image.playlist ]
            view = [ 'playlist' ]

        return view, info

    

    def event_ItemRight(self):
        if not self.last_to_listing[0]: return
        images = self.last_to_listing[0]
        start = self.last_to_listing[1]
        pos = self.last_to_listing[2]
        n_cols = skin.DrawImage_getCols()
        n_rows = skin.DrawImage_getRows()

        if images and pos != None and len(images) > pos:
            if (pos+1) < len(images):
                pos += 1
                self.last_to_listing[2] = pos

            while start + n_cols*n_rows <= pos:
                start += n_cols
            if start > len(images): start = len(images) - n_cols - 1
            self.last_to_listing[1] = start

        self.ToListing(self.last_to_listing)
        return  self.fix_return_tuple(images[pos])

    
    def event_ItemLeft(self):
        if not self.last_to_listing[0]: return
        images = self.last_to_listing[0]
        start = self.last_to_listing[1]
        pos = self.last_to_listing[2]
        n_cols = skin.DrawImage_getCols()

        if images and pos != None and len(images) > pos:
            if (pos-1) >= 0:
                pos -= 1
                self.last_to_listing[2] = pos

            while start > pos:
                start -= n_cols
            if start < 0: start = 0
            self.last_to_listing[1] = start

        self.ToListing(self.last_to_listing)
        return  self.fix_return_tuple(images[pos])


    def event_ItemDown(self):
        if not self.last_to_listing[0]: return
        images = self.last_to_listing[0]
        start = self.last_to_listing[1]
        pos = self.last_to_listing[2]
        n_cols = skin.DrawImage_getCols()
        n_rows = skin.DrawImage_getRows()
        
        if images and pos != None and len(images) > pos:
            n = n_cols
            while n > 0:
                if pos+n < len(images):
                    pos += n
                    break
                else:
                    n -= 1            
                    
            self.last_to_listing[2] = pos
            
            while start + n_cols*n_rows <= pos:
                start += n_cols
            if start > len(images): start = len(images) - n_cols - 1
            self.last_to_listing[1] = start
            
        self.ToListing(self.last_to_listing)
        return  self.fix_return_tuple(images[pos])


    def event_ItemUp(self):
        if not self.last_to_listing[0]: return
        images = self.last_to_listing[0]
        start = self.last_to_listing[1]
        pos = self.last_to_listing[2]
        n_cols = skin.DrawImage_getCols()

        if images and pos != None and len(images) > pos:
            n = n_cols
            while n_cols > 0:
                if pos-n >= 0:
                    pos -= n
                    break
                else:
                    n -= 1            

            while start > pos:
                start -= n_cols
            if start < 0: start = 0
            self.last_to_listing[1] = start

            self.last_to_listing[2] = pos

        self.ToListing(self.last_to_listing)
        return  self.fix_return_tuple(images[pos])
