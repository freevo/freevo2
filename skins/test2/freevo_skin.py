#
# freevo_skin.py
#
# This is the Freevo test1 skin
#
# $Id$

# All the usual imports etc are in the base skin.py

# OSD background bitmap. Must be PNG.
# Format: (filename, x, y)  x=y=-1 means integer tiling

#OSD_BGBITMAP = ('skins/test1/mainbg.png', 128, 48)
OSD_BGBITMAP = ('skins/test2/mainbg3.png',0 ,0)

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

OSD_ICONS = ('skins/test2/movies.png','skins/test2/movies.png','skins/test2/movies.png','skins/test2/movies.png','skins/test2/movies.png')



class Skin(SkinBase):

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
                       font=OSD_FONTNAME_HDR,
                       ptsize=OSD_FONTSIZE_HDR)
       


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
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = OSD_FONTSIZE_ITEMS*ptscale
            osd.drawstring(choice.name, (x0+115), y0,
                           font=OSD_FONTNAME_ITEMS,
                           ptsize=fontsize)
	    if choice.icon != None: 
	    	osd.drawbitmap(choice.icon, x0, y0)
		#print type(choice.icon)
		#print choice.icon
            if menu.selected == choice:
                osd.drawbox(x0 - 8, y0 - 3, 705, y0 + fontsize*1.5, width=-1,
                            color=((160 << 24) | osd.COL_BLUE))
            y0 += spacing

        # Draw the menu choices for the meta selection
        x0 = 40
        y0 = 505
        for item in menuw.nav_items:
            fontsize = OSD_FONTSIZE_BTNS
            osd.drawstring(item.name, x0, y0,
                           font=OSD_FONTNAME_BTNS,
                           ptsize=fontsize)
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + 150, y0 + fontsize*1.5,
                            width=-1,
                            color=((160 << 24) | osd.COL_BLUE))
            x0 += 190

        osd.update()
        

    def DrawMP3(self, info):

        el_min = int(round(info.elapsed / 60))
        el_sec = int(round(info.elapsed % 60))
        rem_min = int(round(info.remain / 60))
        rem_sec = int(round(info.remain % 60))

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
        
        osd.drawstring(info.filename, 30, 490)

        left = 170
        
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
        
        osd.drawstring('Elapsed:', 30, 250, osd.default_fg_color)
        osd.drawstring('%s:%02d   ' % (el_min, el_sec), left, 250,
                       osd.default_fg_color)
        
        osd.drawstring('Remain:', 30, 290, osd.default_fg_color)
        osd.drawstring('%s:%02d   ' % (rem_min,rem_sec), left, 290,
                       osd.default_fg_color)
        
        osd.drawstring('Done:', 30, 330, osd.default_fg_color)
        osd.drawstring('%5.1f%%   ' % info.done, left, 330,
                       osd.default_fg_color)

        # Draw the progress bar
        osd.drawbox(33, 370, 635, 390, width = 3)
        osd.drawbox(34, 371, 634, 389, width = -1, color = osd.default_bg_color)
        pixels = int(round((info.done) * 6.0))
        osd.drawbox(34, 371, 34 + pixels, 389, width = -1, color = 0x038D11)

        osd.update()
    
