# ----------------------------------------------------------------------
# skin_malt1.py - This is the Freevo malt skin no 1
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.5  2002/08/18 22:18:47  tfmalt
# o Started transformation to new gui code. Still WIP.
#
# Revision 1.4  2002/08/18 09:52:08  tfmalt
# o Small changes nothing major.
#
# ----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
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
# -----------------------------------------------------------------------
"""
"""
__version__ = "$Revision$"
__date__    = "$Date$"
__author__  = "Thomas Malt <thomas@malt.no>"


import config
import sys
import socket
import random
import time
import os

import util  # Various utilities
import mixer # The mixer class.
import osd   # The OSD class, used to communicate with the OSD daemon
import rc    # The RemoteControl class
import gui   # Gui library.

from xml.utils import qp_xml # XML support

# Set to 1 for debug output
DEBUG = 1


if not 'OSD_SDL' in dir(config): # XXX kludge
    raise 'SDL OSD Server required for this skin!'

# ======================================================================

mixer = mixer.get_singleton()
rc    = rc.get_singleton()
osd   = osd.get_singleton()

# XXX Shouldn't this be moved to the config file?
OSD_FONT_DIR     = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/SF Arborcrest Medium.ttf'

#
# data structures
#

class XML_data:
    """
    """
    color      = 0
    sel_color  = 0
    x          = 0
    y          = 0
    height     = 0
    width      = 0
    size       = 0
    sel_length = 0
    visible    = 1
    text       = None
    font       = OSD_DEFAULT_FONT
    
    
class XML_menu:
    """
    """
    bgbitmap    = ''
    title       = XML_data()
    items       = XML_data()
    cover_movie = XML_data()
    cover_music = XML_data()
    cover_image = XML_data()
    submenu     = XML_data()
    
class XML_audio:
    """
    """
    bgbitmap = ''

class XMLSkin:
    """
    """
    menu = XML_menu()
    mp3  = XML_audio()


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
            font = os.path.join(OSD_FONT_DIR,
                                node.attrs[('', attr)] + '.ttf').encode()
            if not os.path.isfile(font):
                font = os.path.join(OSD_FONT_DIR,
                                    node.attrs[('', attr)] + '.TTF')
            if not font:
                print "can find font >%s<" % font
                font = OSD_DEFAULT_FONT
            return font
        return default



    def parse_node(self, node, data):
        data.x = self.attr_int(node, "x", data.x)
        data.y = self.attr_int(node, "y", data.y)
        data.height = self.attr_int(node, "height", data.height)
        data.width = self.attr_int(node, "width", data.width)
        data.visible = self.attr_bool(node, "visible", data.visible)

        for subnode in node.children:
            if subnode.name == u'font':
                data.color = self.attr_hex(subnode, "color", data.color)
                data.size = self.attr_int(subnode, "size", data.size)
                data.font = self.attr_font(subnode, "name", data.font)
            if subnode.name == u'selection':
                data.sel_color = self.attr_hex(subnode, "color", data.sel_color)
                data.sel_length = self.attr_int(subnode, "length", data.sel_length)
            if subnode.name == u'text':
                data.text = subnode.textof()


    def read_menu(self, file, menu_node, copy_content):
        """
        Read the skin information for menu.
        """
        if copy_content: self.menu = copy.copy(self.menu)
        for node in menu_node.children:

            if node.name == u'bgbitmap':
                self.menu.bgbitmap = os.path.join(os.path.dirname(file),
                                                  node.textof())

            elif node.name == u'title':
                if copy_content: self.menu.title = copy.copy(self.menu.title)
                self.parse_node(node, self.menu.title)

            elif node.name == u'items':
                if copy_content: self.menu.items = copy.copy(self.menu.items)
                self.parse_node(node, self.menu.items)

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



    def read_mp3(self, file, menu_node, copy_content):
        """
        Read skin information for the audio player
        """
        if copy_content: self.mp3 = copy.copy(self.mp3)
        for node in menu_node.children:
            if node.name == u'bgbitmap':
                self.mp3.bgbitmap = os.path.join(os.path.dirname(file),
                                                 node.textof())


    #
    # 
    #
    def load(self, file, copy_content=0):
        """
        file          String. Filename of the XML config file.
        copy_content  ???
        
        Opens the skin config file and parses it.
        """
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
            


# ======================================================================
# Skin main class
# ======================================================================

class Skin:
    """
    Skin
    """
    
    OSD_XML_DEFINITIONS = 'skins/malt1/768x576.xml'

    def __init__(self):
        if DEBUG: print "Loading Malt 1 skin!"
        # Push main menu items

        self.settings = XMLSkin()
        self.settings.load(self.OSD_XML_DEFINITIONS)
        self.items_per_page = 13 # XXX Sigh! tm.

        if DEBUG: print self.settings.menu.bgbitmap
        self.bg_image = self.settings.menu.bgbitmap
    

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



    def draw_shutdown(self, text=None):
        """
        text  String, text to display.
        
        Draw a shutdown message on shutdown.
        """
        if DEBUG: print "skin.message: Text: ", text

        left   = (osd.width/2)-280
        top    = (osd.height/2)-60
        width  = 560
        height = 120
        icn    = 'icons/shutdown2.png'
        bd_w   = 2
        bg_c   = gui.Color(osd.default_bg_color)
        fg_c   = gui.Color(osd.default_fg_color)

        bg_c.set_alpha(192)

        # osd.drawbitmap(self.bg_image)
        mb = gui.PopupBox(left, top, width, height, icon=icn,
                          bg_color=bg_c, fg_color=fg_c,
                          border='flat', bd_width=bd_w)
        mb.set_text(text)
        mb.set_h_align(gui.Label.LEFT)
        mb.set_font(config.OSD_DEFAULT_FONTNAME, 36)
        mb.show()
        osd.update()


    def popup_box(self, text=None, icon=None):
        """
        text  STring to display

        Draw a popupbox with an optional icon and a text.
        
        Notes: Should maybe be named print_message or show_message.
               Maybe I should use one common box item.
        """
        left   = (osd.width/2)-180
        top    = (osd.height/2)-30
        width  = 360
        height = 60
        icn    = icon
        bd_w   = 2
        bg_c   = gui.Color(osd.default_bg_color)
        fg_c   = gui.Color(osd.default_fg_color)

        bg_c.set_alpha(192)

        pb = gui.PopupBox(left, top, width, height, icon=icn, bg_color=bg_c,
                          fg_color=fg_c, border='flat', bd_width=bd_w)

        pb.set_text(text)
        pb.set_h_align(gui.Label.LEFT)
        pb.set_font('skins/fonts/Arial_Bold.ttf', 24)
        pb.show()
        
        osd.update()
    


    def draw_menu(self, menuw):
        """
        Called from the MenuWidget class to draw a menu page on the
        screen

        Note: This is really messy... I don't know what to make of it.
        """
        if DEBUG: print "Inside draw_menu..."
        
        # XXX Why are we getting the last item , but not popping...
        menu = menuw.menustack[-1]

        if not menu:
            # osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            raise StandardError, 'Internal error, no menu.'

        # get the settings
        if menu.skin_settings:
            val = menu.skin_settings.menu
        else:
            val = self.settings.menu

        if val.bgbitmap[0]:
            apply(osd.drawbitmap, (val.bgbitmap, -1, -1))
    
        # Menu heading
        if val.title.visible:
            if val.title.text: menu.heading = val.title.text
            mh = gui.Label(menu.heading)
            mh.set_parent(osd)
            mh.set_h_align(gui.Label.CENTER)
            mh.set_v_align(gui.Label.TOP)
            mh.set_font(val.title.font, (val.title.size))
            mh.set_v_margin( val.title.y ) 
            mh.show()


        # Draw the menu choices for the main selection
        if len(menuw.menustack) == 1:
            is_main = 1 # Is main menu, kludge
        else:
            is_main = 0

        if is_main:
            # Main menu items
            ptscale = 2.0
            dx = 150 # Extra x indent, kludge
            icon_size = 75

            if len(menuw.menu_items) == 5:
                icon_size = 64
        else:
            # Sub menus
            ptscale = 1.0
            dx = 0
            icon_size = 25

        x0 = val.items.x + dx
        y0 = val.items.y
        selection_height = val.items.height

        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        fontsize = val.items.size*ptscale
        
        # Handle multiple columns in the menu widget.
        # Only the first column is highlighted, and all columns have
        # their left edges vertically aligned
        rows = []
        maxcols = 0  # Largest number of columns in any row
        for item in menuw.menu_items:
            row = item.name.split('\t')
            rows += [row]
            maxcols = max(maxcols, len(row))
            
        # Determine the width of the widest column string
        maxwidth = 0
        for row in rows:
            w, h = osd.stringsize(row[0], font=val.items.font,
                                  ptsize=fontsize)
            maxwidth = max(maxwidth, w)
            
        # Draw the menu items, with icons if any
        row = 0
        for choice in menuw.menu_items:
            if choice.icon != None:
                icon_x = x0 - icon_size - 10 - 25*is_main
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size),
                               icon_x, y0)

            # Draw the selection
            osd.drawstring(rows[row][0], x0, y0, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
            
            if menu.selected == choice:
                osd.drawbox(x0 - 3 - 5*is_main, y0 - 3,
                            x0 + maxwidth + 3 + 5*is_main,
                            y0 + fontsize*1.5 + 1 + 2*is_main, width=-1,
                            color=((160 << 24) | val.items.sel_color))

                image = choice.image

            y0 += spacing
            row += 1

        x0 += maxwidth + 8
        
        # Draw the additional text columns with vertical alignment
        for col in range(1, maxcols):

            y0 = val.items.y  # Start over from the top
            
            # Determine the width of the widest column string
            maxwidth = 0
            for row in rows:
                if col >= len(row): continue # Not all rows are same length
                
                w, h = osd.stringsize(row[col], font=val.items.font,
                                      ptsize=fontsize)
                maxwidth = max(maxwidth, w)

            # Draw the column strings for all rows
            for row in rows:
                if col < len(row): 
                    osd.drawstring(row[col], x0, y0, val.items.color,
                                   font=val.items.font,
                                   ptsize=fontsize)
                y0 += spacing

            # Update x for the next column
            x0 += maxwidth + 8


        # draw the image
        if image:
            (type, image) = image
        if image:
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
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.sel_length, \
                            y0 + val.submenu.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu.sel_color))
            x0 += 190

        osd.update()
        


    def draw_audio_gui(self, ai, val=None):
        """
        Draw the audio GUI main function.

        Arguments: val - settings.mp3: this is the settings from the
                         skin xml-file.
                   ai  - Audioinfo object.           
        """

        left_margin  = 30
        right_margin = 30
        top_margin   = 100
        
        if ai.drawall:
            self.clearscreen()
            
            if val.bgbitmap[0]: self.drawbitmap( val.bgbitmap, -1, -1 )
            if ai.image: self.draw_audio_cover(ai, right_margin)
            self.draw_audio_info(ai, left_margin, top_margin)

        self.draw_audio_timer(ai, val, left_margin, right_margin)
        # self.drawstring(ai.filename, 30, 520) # Draws filename on bottom.
        self.update()    

    def draw_audio_info(self, ai, left=30, top=100):
        """
        Draw the box with ID3-info.

        Arguments: ai          - audioinfo object.
                   left_margin - offset from the left edge.
        Returns:   None
        Todo:      At some point: get_text i8n.
                   We should have some way of determinate length of text
                   string in pixels.
                   Should probably do some sanity check of data from
                   audioinfo.
        """
        
        tabpos    = 170
        linespace = 30
        
        self.drawstring('Title', left, top)
        self.drawstring('%s' % ai.title, tabpos, top)

        self.drawstring('Artist:', left, top+(linespace*1))
        self.drawstring('%s ' % ai.artist, tabpos, top+(linespace*1))
        
        self.drawstring('Album:', left, top+(linespace*2))
        self.drawstring('%s ' % ai.album, tabpos, top+(linespace*2))
        
        self.drawstring('Year:', left, top+(linespace*3))
        self.drawstring('%s ' % ai.year, tabpos, top+(linespace*3))
        
        self.drawstring('Track:', left, top+(linespace*4))
        self.drawstring('%s ' % ai.track, tabpos, top+(linespace*4))
        return 1


    def draw_audio_timer(self, ai, val=None, left=30, right=30, top=360):
        """
        Draws the box with time and stuff. on the bottom.

        Arguments: ai    - Audioinfo object.
                   left  - Offset to the left
                   right - offset to the right
                   top   - Offset from top
                   val   - Settings from the skin configfile.
        """
        linespace = 40
        tab_x    = 170
        
        self.drawstring('Elapsed:', left, top, self.default_fg_color)
        self.drawstring('Remain:', left, top+int(linespace),
                        self.default_fg_color)
        self.drawstring('Done:', left, top+int(linespace*2),
                        self.default_fg_color)

        el_min  = int(ai.elapsed)/60
        el_sec  = int(ai.elapsed)%60
        rem_min = int(ai.remain)/60
        rem_sec = int(ai.remain)%60


        # Draw the progress bar
        bar_thickness = 22
        bar_width     = self.width-right-(tab_x)-100
        bar_top       = top+(linespace*2)
        bar_bottom    = bar_top+bar_thickness
        done_x        = tab_x+bar_width+left
        done_y        = bar_top
        sv = 5 # dropshadow vertical. :/
        sh = 5 # dropshadow horisontal.
        
        # This only draws to the section needing to be redrawn for the timer.
        if val.bgbitmap[0]:
            self.drawbitmap(val.bgbitmap, tab_x, top, None,
                            tab_x, top, 100, 100)
            # for end of bar.
            self.drawbitmap(val.bgbitmap, done_x, done_y, None,
                            done_x, done_y, 100, 40)

        # Draw the progress bar
        # XXX oh.. no. I can't help myself: dropshadow.
        self.draw_3D_border(tab_x, bar_top, tab_x+bar_width, bar_bottom,
                            fg_color=self.default_fg_color, bg_color=None,
                            width=1)
        self.drawbox(tab_x, bar_top, tab_x+bar_width, bar_bottom,
                     width=-1, color=self.default_bg_color)

        done_width = int(round(((ai.done*bar_width)/100)))
        # XXX We just have to make this a gradient at some point. :)
        self.drawbox(tab_x, bar_top, tab_x+done_width, bar_bottom,
                     width=-1, color=self.COL_BLUE)

        self.drawstring('%s:%02d   ' % (el_min, el_sec), tab_x,
                        top, self.default_fg_color)
        self.drawstring('%s:%02d   ' % (rem_min,rem_sec), tab_x,
                        top+linespace, self.default_fg_color)
        self.drawstring('%0.1f%%   ' % ai.done, done_x, done_y,
                        self.default_fg_color)
        


    def draw_audio_cover(self, ai, right=30):
        """
        Draw the CD cover if it exist on the audio GUI.
        Lots of things here should be configurable from the outside.
        """
        if not ai.image:
            return 0

        top_offset   = 100   # How far from the top to draw.
        (iw, ih)     = util.pngsize(ai.image)
        start_x      = self.width-iw-right

        self.draw_3D_border(start_x, top_offset, start_x+iw, top_offset+ih,
                            fg_color=self.default_fg_color, bg_color=None,
                            width=1)
        self.drawbitmap(ai.image, start_x, top_offset)
        return 1

