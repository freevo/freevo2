#
# skin_main1.py
#
# This is the Freevo main skin no 1
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

    # OSD fonts
    OSD_FONTNAME = 'skins/fonts/Cultstup.ttf'
    OSD_FONTSIZE = 14
    OSD_FONTNAME_HDR = 'skins/fonts/Cultstup.ttf'
    OSD_FONTSIZE_HDR = 22
    OSD_FONTNAME_ITEMS = 'skins/fonts/SF Arborcrest Medium.ttf'
    OSD_FONTSIZE_ITEMS = 15
    OSD_FONTNAME_BTNS = 'skins/fonts/RUBTTS__.TTF'
    OSD_FONTSIZE_BTNS = 18

    # OSD background bitmap. Must be PNG.
    # Format: (filename, x, y)  x=y=-1 means integer tiling

    OSD_BGBITMAP = ('skins/test2/mainbg3.png', -1, -1)

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
        
        if menu.background != None:
            osd.drawbitmap(util.resize(menu.background, 768, 405), 0, 85)
            
        # Menu heading
        osd.drawstring(menu.heading, 160, 50,
                       font=self.OSD_FONTNAME_HDR,
                       ptsize=self.OSD_FONTSIZE_HDR)

        # Draw the menu choices for the main selection
        x0 = 60
        y0 = 100
        selection_height = 390
        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / min(4, max(len(menuw.menu_items),1))

        # image to display
        image = None
        
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
                if y0 > 450:
                    y0 = 100
                    x0 = 384
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = self.OSD_FONTSIZE_ITEMS*ptscale
	    w = 0
	    h = 0
	    if choice.icon != None: 
 		if choice.scale == 1:
			w,h = util.pngsize(util.resize(choice.icon))
			osd.drawbitmap(util.resize(choice.icon), x0, y0)
		else:
			w,h = util.pngsize(choice.icon)	
			osd.drawbitmap(choice.icon,x0,y0)
		# Align the logo based on image size
	

            osd.drawstring(choice.name, (x0+w+10), y0,
                           font=self.OSD_FONTNAME_ITEMS,
                           ptsize=fontsize)
	    if menu.selected == choice:
                if len(menuw.menustack) == 1:
                    osd.drawbox(x0 + w, y0 - 3, x0 + 300, y0 + fontsize*1.5, width=-1,
                                color=((160 << 24) | osd.COL_BLUE))
                else:
                    osd.drawbox(x0 - 8 + w, y0 - 3, 705, y0 + fontsize*1.5, width=-1,
                                color=((160 << 24) | osd.COL_BLUE))

                if choice.image != None:
                    (type, image) = choice.image
                    if type == 'photo':
                        image = util.getExifThumbnail(image, 200, 150)
                    else:
                        if image != None: image = util.resize(image, 200, 280)

		if choice.icon != None and choice.popup:
			(w, h) = util.pngsize(choice.icon)
			# Calculate best image placement
			logox = int(osd.width) - int(w) - 55
			# Draw border for image
			osd.drawbox(int(logox), 100, (int(logox) + int(w)), 100 + int(h),
            			    width=6, color=0x000000)
			osd.drawbitmap(choice.icon, logox, 100)

            y0 += spacing

        # draw the image
        if image != None:
            (w, h) = util.pngsize(image)
            logox = int(osd.width) - int(w) - 30
            osd.drawbitmap(image, logox, 100)

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
                            color=((160 << 24) | osd.COL_BLUE))
	    x0 += 190

        osd.update()
        

    def DrawMP3(self, info):

        left = 170

        osd.clearscreen()

        if self.bgbitmap[0]:
            apply(osd.drawbitmap, self.bgbitmap)
            

        # Display the cover image file if it is present
        if info.image:
            # Check size to adjust image placement 
            (w, h) = util.pngsize(info.image)
            
            # Calculate best image placement
            logox = int(osd.width) - int(w) - 55
            
            # Draw border for image
            osd.drawbox(int(logox), 100, (int(logox) + int(w)), 100 + int(h),
                        width=6, color=0x000000)
            osd.drawbitmap(info.image, logox, 100)

        osd.drawstring(info.filename, 30, 520)

        osd.drawstring('Title:', 30, 100)
        osd.drawstring('%s ' % info.id3.title, left, 100)
        
        osd.drawstring('Artist:', 30, 130)
        osd.drawstring('%s ' % info.id3.artist, left, 130)
        
        osd.drawstring('Album:', 30, 160)
        osd.drawstring('%s ' % info.id3.album, left, 160)
        
        osd.drawstring('Year:', 30, 190)
        osd.drawstring('%s ' % info.id3.year, left, 190)
        
        osd.drawstring('Track:', 30, 220)
        osd.drawstring('%s ' % info.id3.track, left, 220)
        
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
        osd.drawbox(34, 441, 34 + pixels, 459, width = -1, color = osd.COL_BLUE)

        osd.update()
    
