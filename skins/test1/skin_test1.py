#
# skin_test1.py
#
# This is the Freevo test1 skin
#
# $Id$

# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()


class Skin:

    # OSD background bitmap. Must be PNG.
    # Format: (filename, x, y)  x=y=-1 means integer tiling

    OSD_BGBITMAP = ('skins/test1/mainbg2.png', -1, -1)

    # OSD fonts
    OSD_FONTNAME = 'skins/fonts/Cultstup.ttf'
    OSD_FONTSIZE = 14
    OSD_FONTNAME_HDR = 'skins/fonts/Cultstup.ttf'
    OSD_FONTSIZE_HDR = 22
    OSD_FONTNAME_ITEMS = 'skins/fonts/SF Arborcrest Medium.ttf'
    OSD_FONTSIZE_ITEMS = 15
    OSD_FONTNAME_BTNS = 'skins/fonts/RUBTTS__.TTF'
    OSD_FONTSIZE_BTNS = 18

    OSD_DEFAULT_FONTNAME = OSD_FONTNAME
    OSD_DEFAULT_FONTSIZE = OSD_FONTSIZE
    
    bgbitmap = OSD_BGBITMAP
    items_per_page = 13

    
    def __init__(self):
        # Push main menu items
        pass


    # This function is called from the rc module and other places
    def HandleEvent(self, ev):
        # Handle event (remote control, timer, msg display...)
        # Some events are handled directly (volume control),
        # RC cmds are handled using the menu lib, and events
        # might be passed directly to a foreground application
        # that handles its' own graphics
        pass


    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        osd.clearscreen(osd.COL_WHITE)

        menu = menuw.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        if self.bgbitmap[0]:
            apply(osd.drawbitmap, self.bgbitmap)
            
        # Menu heading
        osd.drawstring(menu.heading, 160, 50,
                       font=self.OSD_FONTNAME_HDR,
                       ptsize=self.OSD_FONTSIZE_HDR)
        
        # Draw a box around the selection area
        osd.drawbox(40, 85, 720, 490, width=3,
                    color=osd.COL_BLACK)
        
        # Draw the menu choices for the main selection
        x0 = 60
        y0 = 100
        selection_height = 390
        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = self.OSD_FONTSIZE_ITEMS*ptscale
            osd.drawstring(choice.name, x0, y0,
                           font=self.OSD_FONTNAME_ITEMS,
                           ptsize=fontsize)
            if menu.selected == choice:
                osd.drawbox(x0 - 8, y0 - 3, 705, y0 + fontsize*1.5, width=-1,
                            color=((160 << 24) | osd.COL_ORANGE))
            y0 += spacing

        # Draw the menu choices for the meta selection
        x0 = 40
        y0 = 505
        for item in menuw.nav_items:
            fontsize = self.OSD_FONTSIZE_BTNS
            osd.drawstring(item.name, x0, y0,
                           font=self.OSD_FONTNAME_BTNS,
                           ptsize=fontsize)
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + 150, y0 + fontsize*1.5,
                            width=-1,
                            color=((160 << 24) | osd.COL_ORANGE))
            x0 += 190

        osd.update()
        

    def DrawMP3(self, info):

        left = 170

        if info.drawall:
            osd.clearscreen()

            # Display the cover image file if it is present
            if info.image:
                # Check size to adjust image placement 
                (w, h) = util.pngsize(info.image)

                # Calculate best image placement
                logox = int(osd.width) - int(w) - 55

                # Draw border for image
                osd.drawbox(int(logox), 80, (int(logox) + int(w)), 80 + int(h),
                            width=6, color=0x000000)
                osd.drawbitmap(info.image, logox, 80)

            osd.drawstring(info.filename, 30, 520)

            osd.drawstring('Title:', 30, 80)
            osd.drawstring('%s ' % info.id3.title, left, 80)

            osd.drawstring('Artist:', 30, 110)
            osd.drawstring('%s ' % info.id3.artist, left, 110)

            osd.drawstring('Album:', 30, 140)
            osd.drawstring('%s ' % info.id3.album, left, 140)

            osd.drawstring('Year:', 30, 170)
            osd.drawstring('%s ' % info.id3.year, left, 170)

            osd.drawstring('Track:', 30, 200)
            osd.drawstring('%s ' % info.id3.track, left, 200)
        else:
            # Erase the portion that will be redrawn
            osd.drawbox(0, 300, 767, 500, width = -1, color = osd.default_bg_color)
        
        el_min = int(round(info.elapsed / 60))
        el_sec = int(round(info.elapsed % 60))
        rem_min = int(round(info.remain / 60))
        rem_sec = int(round(info.remain % 60))

        osd.drawstring('Elapsed:', 30, 300, osd.default_fg_color)
        osd.drawstring('%s:%02d   ' % (el_min, el_sec), left, 300,
                       osd.default_fg_color)
        
        osd.drawstring('Remain:', 30, 340, osd.default_fg_color)
        osd.drawstring('%s:%02d   ' % (rem_min,rem_sec), left, 340,
                       osd.default_fg_color)
        
        osd.drawstring('Done:', 30, 380, osd.default_fg_color)
        osd.drawstring('%0.1f%%   ' % info.done, left, 380,
                       osd.default_fg_color)

        # Draw the progress bar
        osd.drawbox(33, 440, 635, 460, width = 3)
        pixels = int(round((info.done) * 6.0))
        osd.drawbox(34, 441, 34 + pixels, 459, width = -1, color = 0x038D11)

        osd.update()
    
