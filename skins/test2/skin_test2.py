#
# skin_test2.py
#
# This is the Freevo test2 skin
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

# Another skin that this one inherits some functions from
sys.path += ['skins/test1']
import skin_test1

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


class Skin(skin_test1.Skin):

    # OSD background bitmap. Must be PNG.
    # Format: (filename, x, y)  x=y=-1 means integer tiling

    OSD_BGBITMAP = ('skins/test2/mainbg3.png', -1, -1)

    bgbitmap = OSD_BGBITMAP
    items_per_page = 13


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
            #osd.drawbitmap(util.resize(menu.background, 768, 576), 0, 0)
            
        # Menu heading
        osd.drawstring(menu.heading, 160, 50,
                       font=self.OSD_FONTNAME_HDR,
                       ptsize=self.OSD_FONTSIZE_HDR)


	#osd.drawbitmap('skins/test2/movies.png',80,80)

        # Draw a box around the selection area
        #osd.drawbox(40, 85, 720, 490, width=3,
        #            color=osd.COL_BLACK)
        
        # Draw the menu choices for the main selection
        x0 = 60
        y0 = 100
        selection_height = 390
        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
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
                osd.drawbox(x0 - 8 + w, y0 - 3, 705, y0 + fontsize*1.5, width=-1,
                            color=((160 << 24) | osd.COL_BLUE))

                if choice.image != None:
                    image = util.resize(choice.image, 200, 280)

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
        
