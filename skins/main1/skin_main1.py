#
# skin_main1.py
#
# This is the Freevo main skin no 1
#
# $Id$

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

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# XML support
from xml.utils import qp_xml


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


###############################################################################
# XML file parse for the skin
###############################################################################


OSD_FONT_DIR = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/SF Arborcrest Medium.ttf'
#
# data structures
#

class XML_data:
    color = 0
    x = y = height = width = length = size = 0
    visible = 1
    text = None
    font = OSD_DEFAULT_FONT
    
    
class XML_menu:
    bgbitmap = ''
    title = XML_data()
    items = XML_data()
    item_selection = XML_data()
    cover_movie = XML_data()
    cover_music = XML_data()
    cover_image = XML_data()
    submenu = XML_data()
    submenu_selection = XML_data()
    
class XML_mp3:
    bgbitmap = ''

class XMLSkin:


    menu = XML_menu()
    mp3  = XML_mp3()


    #
    # Help functions
    #
    def attr_int(self, node, attr, default):
        try:
            if node.attrs.has_key(('', attr)):
                return int(node.attrs[('', attr)])
        except ValueError:
            pass
        return default

    def attr_hex(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            return int(node.attrs[('', attr)], 16)
        return default

    def attr_bool(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            if node.attrs[('', attr)] == "yes":
                return 1
            elif node.attrs[('', attr)] == "no":
                return 0
        return default

    def attr_font(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] + '.ttf').encode()
            if not os.path.isfile(font):
                font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] + '.TTF')
            if not font:
                print "can find font >%s<" % font
                font = OSD_DEFAULT_FONT
            return font
        return default



    def parse_node(self, node, data):
        data.color = self.attr_hex(node, "color", data.color)
        data.x = self.attr_int(node, "x", data.x)
        data.y = self.attr_int(node, "y", data.y)
        data.length = self.attr_int(node, "length", data.length)
        data.height = self.attr_int(node, "height", data.height)
        data.width = self.attr_int(node, "width", data.width)
        data.size = self.attr_int(node, "size", data.size)
        data.font = self.attr_font(node, "font", data.font)
        data.visible = self.attr_bool(node, "visible", data.visible)
        if node.textof():
            data.text = node.textof()

    #
    # read the skin informations for menu
    #
    def read_menu(self, file, menu_node, copy_content):
        if copy_content: self.menu = copy.copy(self.menu)
        for node in menu_node.children:

            if node.name == u'bgbitmap':
                self.menu.bgbitmap = os.path.join(os.path.dirname(file), node.textof())

            elif node.name == u'title':
                if copy_content: self.menu.title = copy.copy(self.menu.title)
                self.parse_node(node, self.menu.title)

            elif node.name == u'items':
                if copy_content: self.menu.items = copy.copy(self.menu.items)
                self.parse_node(node, self.menu.items)
                for subnode in node.children:
                    if subnode.name == u'selection':
                        if copy_content:
                            self.menu.item_selection = copy.copy(self.menu.item_selection)
                        self.parse_node(subnode, self.menu.item_selection)

            elif node.name == u'cover':
                for subnode in node.children:
                    if subnode.name == u'movie':
                        if copy_content:
                            self.menu.cover_movie = copy.copy(self.menu.cover_movie)
                        self.parse_node(subnode, self.menu.cover_movie)
                    if subnode.name == u'music':
                        if copy_content:
                            self.menu.cover_music = copy.copy(self.menu.cover_music)
                        self.parse_node(subnode, self.menu.cover_music)
                    if subnode.name == u'image':
                        if copy_content:
                            self.menu.cover_image = copy.copy(self.menu.cover_image)
                        self.parse_node(subnode, self.menu.cover_image)

            elif node.name == u'submenu':
                if copy_content: self.menu.submenu = copy.copy(self.menu.submenu)
                self.parse_node(node, self.menu.submenu)
                for subnode in node.children:
                    if subnode.name == u'selection':
                        if copy_content:
                            self.menu.submenu_selection = copy.\
                                                          copy(self.menu.submenu_selection)
                        self.parse_node(subnode, self.menu.submenu_selection)



    #
    # read the skin informations for the mp3 player
    #
    def read_mp3(self, file, menu_node, copy_content):
        if copy_content: self.mp3 = copy.copy(self.mp3)
        for node in menu_node.children:
            if node.name == u'bgbitmap':
                self.mp3.bgbitmap = os.path.join(os.path.dirname(file), node.textof())


    #
    # parse the skin file
    #
    def load(self, file, copy_content = 0):
        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            if box.children[0].name == 'skin':
                for node in box.children[0].children:
                    if node.name == u'menu':
                        self.read_menu(file, node, copy_content)
                    if node.name == u'mp3':
                        self.read_mp3(file, node, copy_content)
        except:
            print "ERROR: XML file corrupt"
            
###############################################################################
# Skin main functions
###############################################################################

class Skin:

    # OSD XML specifiaction
    OSD_XML_DEFINITIONS = 'skins/main1/768x576.xml'

    settings = XMLSkin()
    settings.load(OSD_XML_DEFINITIONS)

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



    # Parse XML files with additional settings
    # TODO: parse also parent directories
    def LoadSettings(self, dir):
        if dir and os.path.isfile(os.path.join(dir, "skin.xml")):
            settings = copy.copy(self.settings)
            settings.load(os.path.join(dir, "skin.xml"), 1)
            return settings
        return None



    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        osd.clearscreen(osd.COL_WHITE)

        menu = menuw.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        # get the settings
        if menu.skin_settings:
            val = menu.skin_settings.menu
        else:
            val = self.settings.menu

        print val.bgbitmap
        if val.bgbitmap[0]:
            apply(osd.drawbitmap, (val.bgbitmap, -1, -1))
        
        # Menu heading
        if val.title.visible:
            if val.title.text: menu.heading = val.title.text
            osd.drawstring(menu.heading, val.title.x, val.title.y, val.title.color,
                           font=val.title.font,
                           ptsize=val.title.size)

        # Draw the menu choices for the main selection
        x0 = val.items.x
        y0 = val.items.y
        selection_height = val.items.height
        
        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / min(4, max(len(menuw.menu_items),1))

        # image to display
        image = None
        
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
                if y0 > 450:
                    y0 = 100   ## XXX Hardcoded
                    x0 = 384
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = val.items.size*ptscale
	    w = 0
	    h = 0
	    if choice.icon != None: 
 		if choice.scale == 1:
			w,h = util.pngsize(util.resize(choice.icon))
			osd.drawbitmap(util.resize(choice.icon), x0, y0)
		else:
			w,h = util.pngsize(choice.icon)	
			osd.drawbitmap(choice.icon,x0,y0)
	

            osd.drawstring(choice.name, (x0+w+10), y0, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
	    if menu.selected == choice:
                if len(menuw.menustack) == 1:
                    osd.drawbox(x0 + w, y0 - 3, x0 + 300, y0 + fontsize*1.5, width=-1,
                                color=((160 << 24) | val.item_selection.color))
                else:
                    osd.drawbox(x0 - 8 + w, y0 - 3, x0 - 8 + val.item_selection.length,\
                                y0 + fontsize*1.5, width=-1,
                                color=((160 << 24) | val.item_selection.color))

                image = choice.image


            y0 += spacing

        # draw the image
        if image != None:
            (type, image) = image
        if image != None:
            if type == 'photo' and val.cover_image.visible:
                thumb = util.getExifThumbnail(image, val.cover_image.width, \
                                              val.cover_image.height)
                if thumb:
                    osd.drawbitmap(thumb, val.cover_image.x, val.cover_image.y)
            elif type == 'movie' and val.cover_movie.visible:
                osd.drawbitmap(\
                        util.resize(image, val.cover_movie.width, \
                                    val.cover_movie.height),\
                        val.cover_movie.x, val.cover_movie.y)
            elif type == 'music' and val.cover_music.visible:
                osd.drawbitmap(\
                        util.resize(image, val.cover_music.width, \
                                    val.cover_music.height),\
                        val.cover_music.x, val.cover_music.y)
            

        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y
        
        for item in menuw.nav_items:
            osd.drawstring(item.name, x0, y0, val.submenu.color,
                           font=val.submenu.font,
                           ptsize=val.submenu.size)
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu_selection.length, \
                            y0 + val.submenu.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu_selection.color))
	    x0 += 190

        osd.update()
        



    def DrawMP3(self, info):

        val = self.settings.mp3

        left = 170

        if info.drawall:
            osd.clearscreen()

            if val.bgbitmap[0]:
                apply(osd.drawbitmap, (val.bgbitmap, -1, -1))


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


            osd.drawstring('Elapsed:', 30, 300, osd.default_fg_color)
            osd.drawstring('Remain:', 30, 340, osd.default_fg_color)
            osd.drawstring('Done:', 30, 380, osd.default_fg_color)

        else:
            # Erase the portion that will be redrawn
            if val.bgbitmap[0]:
                osd.drawbitmap(val.bgbitmap, left, 300, None, left, 300, 100, 100)

        
        el_min = int(round(info.elapsed / 60))
        el_sec = int(round(info.elapsed % 60))
        rem_min = int(round(info.remain / 60))
        rem_sec = int(round(info.remain % 60))

        osd.drawstring('%s:%02d   ' % (el_min, el_sec), left, 300,
                       osd.default_fg_color)
        
        osd.drawstring('%s:%02d   ' % (rem_min,rem_sec), left, 340,
                       osd.default_fg_color)
        
        osd.drawstring('%0.1f%%   ' % info.done, left, 380,
                       osd.default_fg_color)

        # Draw the progress bar
        osd.drawbox(33, 440, 635, 460, width = 3)
        osd.drawbox(34, 441, 634, 459, width = -1, color = osd.default_bg_color)
        pixels = int(round((info.done) * 6.0))
        osd.drawbox(34, 441, 34 + pixels, 459, width = -1, color = osd.COL_BLUE)

        osd.update()
    
