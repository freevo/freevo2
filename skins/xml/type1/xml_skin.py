#if 0
# -----------------------------------------------------------------------
# xml_skin.py - XML reader for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2002/10/16 04:58:16  krister
# Changed the main1 skin to use Gustavos new extended menu for TV guide, and Dischis new XML code. grey1 is now the default skin, I've tested all resolutions. I have not touched the blue skins yet, only copied from skin_dischi1 to skins/xml/type1.
#
# Revision 1.7  2002/10/15 21:38:42  dischi
# more cleanups
#
# Revision 1.6  2002/10/15 21:25:16  dischi
# use copy.deepcopy instead of copy.copy. Saves lots of
# if copy-content: xxx = copy.copy(xxx)
#
# Revision 1.5  2002/10/15 19:57:57  dischi
# Added extended menu support
#
# Revision 1.4  2002/10/14 18:47:00  dischi
# o added scale support, you can define a scale value for the import
#   grey640x480 and grey768x576 are very simple now
# o renamed the xml files
#
# Revision 1.3  2002/10/14 17:10:26  dischi
# One skin can inherit from another. Example 800x600.xml defines everything,
# 768x576 only the differences.
#
# Revision 1.2  2002/10/13 14:16:55  dischi
# Popup box and mp3 player are now working, too. This skin can look
# like main1 and aubin1. I droped the support for the gui classes
# because there are not powerfull enough
#
# Revision 1.1  2002/10/12 18:45:25  dischi
# New skin, Work in progress
#
# Revision 1.11  2002/10/05 18:10:57  dischi
# Added support for a local_skin.xml file. See Docs/documentation.html
# section 4.1 for details. An example is also included.
#
# Revision 1.10  2002/09/25 18:54:32  dischi
# Changed the <cover> style to <covers> and <cover type=""/>. Added
# border_size and border_color to cover
#
# Revision 1.9  2002/09/23 18:59:00  dischi
# Added alignment to font, some cleanups in xml_skin.py
#
# Revision 1.8  2002/09/23 18:18:52  dischi
# remove shadow_mode stuff
#
# Revision 1.7  2002/09/22 11:49:18  dischi
# Bugfix
#
# Revision 1.6  2002/09/22 09:54:31  dischi
# XML cleanup. Please take a look at the new skin files to see the new
# structure. The 640x480 skin is also workin now, only one small bug
# in the submenu (seems there is something hardcoded).
#
# Revision 1.5  2002/09/15 12:32:01  dischi
# The DVD/VCD/SCVD/CD description file for the automounter can now also
# contain skin informations. An announcement will follow. For this the
# paramter dir in menu.py is renamed to xml_file since the only use
# was to find the xml file. All other modules are adapted (dir -> xml_file)
#
# Revision 1.4  2002/09/01 21:07:20  krister
# Made sure unicode encodes to latin-1.
#
# Revision 1.3  2002/09/01 04:15:52  krister
# Fixed skin crashes by returning regular strings instead of Unicode from the XML parsing. I do not know why this matters so much.
#
# Revision 1.2  2002/08/19 05:52:08  krister
# Changed to Gustavos new XML code for more settings in the skin. Uses columns for the TV guide.
#
# Revision 1.2  2002/08/18 06:12:57  krister
# Added load font with extension.
#
# Revision 1.1  2002/08/17 02:55:45  krister
# Submitted by Gustavo Barbieri.
#
# Revision 1.1  2002/08/11 08:11:03  dischi
# moved the XML parsing to an extra file and the file 768x576.xml
# to the directory skins/xml
#
#
#
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
# -----------------------------------------------------------------------
#endif



# some python stuff
import sys
import socket
import random
import time
import os
import copy
import re
import traceback

# XML support
from xml.utils import qp_xml


# XXX Shouldn't this be moved to the config file?

OSD_FONT_DIR = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/arialbd.ttf'



# ======================================================================

#
# data structures
#


# This contains all the stuff a node can have, if it makes sence with
# this special node or not
class XML_data:
    def __init__(self):
        self.color = 0
        self.bgcolor = 0
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.size = 0
        self.length = 0
        self.visible = 1
        self.text = None
        self.font = OSD_DEFAULT_FONT
        self.mode=''
        self.shadow_visible = 0
        self.shadow_color = 0
        self.shadow_pad_x = 1
        self.shadow_pad_y = 1
        self.border_color = 0
        self.border_size = 0
        self.align = 'left'
        self.valign = 'top'
        self.image = ''
        self.mask = ''
    
class XML_menuitem(XML_data):
    def __init__(self):
        XML_data.__init__(self)
        self.selection = XML_data()

class XML_menuitems:
    def __init__(self):
        self.x = self.y = self.height = self.width = 0
        self.default = XML_menuitem()
        self.dir = XML_menuitem()
        self.pl = XML_menuitem()
    
class XML_menu:
    def __init__(self):
        self.background = XML_data()
        self.logo = XML_data()
        self.title = XML_data()
        self.items = XML_menuitems()
        self.cover_movie = XML_data()
        self.cover_music = XML_data()
        self.cover_image = XML_data()
        self.submenu = XML_menuitem()

    
class XML_mp3:
    def __init__(self):
        self.background = XML_data()
        self.progressbar = XML_data()
        self.title = XML_data()    
        self.cover = XML_data()    
        self.info  = XML_data()
        self.logo  = XML_data()

class XML_popup(XML_data):
    def __init__(self):
        XML_data.__init__(self)
        self.message = XML_data()    


# compatibilty mode, remove later
class XML_mainmenuitem:
    def __init__(self):
        self.name = ''
        self.visible = 1
        self.icon = ''
        self.pos = 0
        self.action = None
        self.arg = None

class XML_mainmenu:
    def __init__(self):
        self.items = {}

class XML_listingmenuitem(XML_menuitem):
    def __init__(self):
        XML_menuitem.__init__(self)
        self.head = XML_data()
        self.expand = XML_data()
        self.border_color = 0
        self.border_size = 1
        self.spacing = 2
        self.channel_width = 100
        self.left_arrow = None
        self.right_arrow = None
        self.up_arrow = None
        self.down_arrow = None

class XML_extendedmenu:
    def __init__(self):
        self.background = XML_data()
        self.logo = XML_data()
        self.header = XML_data()
        self.view = XML_data()
        self.info = XML_data()
        self.listing = XML_listingmenuitem()




# ======================================================================

#
# Help functions
#
def attr_int(node, attr, default, scale=0.0):
    try:
        if node.attrs.has_key(('', attr)):
            val = int(node.attrs[('', attr)])
            if scale:
                val = scale*val
            return int(val)
    except ValueError:
        pass
    return default

def attr_float(node, attr, default):
    try:
        if node.attrs.has_key(('', attr)):
            return float(node.attrs[('', attr)])
    except ValueError:
        pass
    return default

def attr_hex(node, attr, default):
    try:
        if node.attrs.has_key(('', attr)):
            return long(node.attrs[('', attr)], 16)
    except ValueError:
        pass
    return default

def attr_bool(node, attr, default):
    if node.attrs.has_key(('', attr)):
        if node.attrs[('', attr)] == "yes":
            return 1
        elif node.attrs[('', attr)] == "no":
            return 0
    return default

def attr_str(node, attr, default):
    if node.attrs.has_key(('', attr)):
        return node.attrs[('', attr)].encode('latin-1')
    return default

def attr_file(node, attr, default, c_dir):
    if node.attrs.has_key(('', attr)):
        file = node.attrs[('', attr)].encode('latin-1')
        if file:
            return os.path.join(c_dir, file)
        return ""
    return default

def attr_font(node, attr, default):
    if node.attrs.has_key(('', attr)):
        fontext = os.path.splitext(node.attrs[('', attr)])[1]
        if fontext:
            # There is an extension (e.g. '.pfb'), use the full name
            font = os.path.join(OSD_FONT_DIR,
                                node.attrs[('', attr)]).encode('latin-1')
        else:
            # '.ttf' is the default extension
            font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] +
                                '.ttf').encode('latin-1')
            if not os.path.isfile(font):
                font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] +
                                    '.TTF').encode('latin-1')
        if not font:
            print "can find font >%s<" % font
            font = OSD_DEFAULT_FONT
        return font
    return default


# ======================================================================

#
# Main XML skin class
#
class XMLSkin:
    def __init__(self):
        self.menu_default = XML_menu()
        self.menu_main    = XML_menu()
        self.menu_tv      = XML_menu()
        self.mp3          = XML_mp3()
        self.popup        = XML_popup()

        self.mainmenu = XML_mainmenu()
        self.e_menu = { }

        self.scale = 0.0

        
    #
    # parse one node
    #
    def parse_node(self, node, data, c_dir=''):
        data.x = attr_int(node, "x", data.x, self.scale)
        data.y = attr_int(node, "y", data.y, self.scale)
        data.height = attr_int(node, "height", data.height, self.scale)
        data.width = attr_int(node, "width", data.width, self.scale)
        data.length = attr_int(node, "length", data.length, self.scale)

        data.visible = attr_bool(node, "visible", data.visible)
        data.bgcolor = attr_hex(node, "bgcolor", data.bgcolor)
        data.color = attr_hex(node, "color", data.color) # will be overrided by font
        data.border_color = attr_hex(node, "border_color", data.border_color)
        data.border_size = attr_int(node, "border_size", data.border_size)
        data.image = attr_file(node, "image", data.image, c_dir)
        data.mask = attr_file(node, "mask", data.mask, c_dir)

        for subnode in node.children:
            if subnode.name == u'font':
                data.color = attr_hex(subnode, "color", data.color)
                data.size = attr_int(subnode, "size", data.size, self.scale)
                data.font = attr_font(subnode, "name", data.font)
                data.align = attr_str(subnode, "align", data.align)
                data.valign = attr_str(subnode, "valign", data.valign)
            if subnode.name == u'selection':
                data.selection = copy.copy(data.selection)
                self.parse_node(subnode, data.selection)
            if subnode.name == u'text':
                data.text = subnode.textof()
            if subnode.name == u'shadow':
                data.shadow_visible = attr_bool(subnode, "visible", data.shadow_visible)
                data.shadow_color = attr_hex(subnode, "color", data.shadow_color)
                data.shadow_pad_x = attr_int(subnode, "x", data.shadow_pad_x)
                data.shadow_pad_y = attr_int(subnode, "y", data.shadow_pad_y)
            if subnode.name == u'background':
                data.bgcolor = attr_hex(subnode, "color", data.bgcolor)                
            if subnode.name == u'geometry':
                data.x = attr_int(subnode, "x", data.x, self.scale)
                data.y = attr_int(subnode, "y", data.y, self.scale)
                data.width = attr_int(subnode, "width", data.width, self.scale)
                data.height = attr_int(subnode, "height", data.height, self.scale)
                

    #
    # parse <items>
    #
    def parseItems(self, node, data):
        data.x = attr_int(node, "x", data.x, self.scale)
        data.y = attr_int(node, "y", data.y, self.scale)
        data.height = attr_int(node, "height", data.height, self.scale)
        data.width  = attr_int(node, "width", data.width, self.scale)

        for subnode in node.children:
            if subnode.name == u'item':
                type = attr_str(subnode, "type", "all")

                if type == "all":
                    # default content, override all settings for pl and dir:
                    self.parse_node(subnode, data.default)
                    self.parse_node(subnode, data.dir)
                    self.parse_node(subnode, data.pl)

                elif type == 'dir':
                    self.parse_node(subnode, data.dir)

                elif type == 'playlist':
                    self.parse_node(subnode, data.pl)
        

    #
    # read the skin informations for menu
    #
    def read_menu(self, file, menu_node, menu):
        for node in menu_node.children:
            if node.name == u'background':
                self.parse_node(node, menu.background, os.path.dirname(file))

            if node.name == u'logo':
                self.parse_node(node, menu.logo, os.path.dirname(file))

            elif node.name == u'title':
                self.parse_node(node, menu.title)

            elif node.name == u'items':
                self.parseItems(node, menu.items)
                
            elif node.name == u'covers':
                for subnode in node.children:
                    type = attr_str(subnode, "type", "")

                    if type == u'all':
                        self.parse_node(subnode, menu.cover_movie)
                        self.parse_node(subnode, menu.cover_music)
                        self.parse_node(subnode, menu.cover_image)

                    if type == u'movie':
                        self.parse_node(subnode, menu.cover_movie)
                    if type == u'music':
                        self.parse_node(subnode, menu.cover_music)
                    if type == u'image':
                        self.parse_node(subnode, menu.cover_image)

            elif node.name == u'submenu':
                self.parse_node(node, menu.submenu)


    #
    # read the skin informations for the mp3 player
    #
    def read_mp3(self, file, menu_node, copy_content):
        if copy_content: self.mp3 = copy.deepcopy(self.mp3)

        for node in menu_node.children:
            if node.name == u'background':
                self.parse_node(node, self.mp3.background, os.path.dirname(file))

            elif node.name == u'title':
                self.parse_node(node, self.mp3.title)

            elif node.name == u'cover':
                self.parse_node(node, self.mp3.cover)

            elif node.name == u'progressbar':
                self.parse_node(node, self.mp3.progressbar)

            elif node.name == u'fileinfo':
                self.parse_node(node, self.mp3.info)

            elif node.name == u'logo':
                self.parse_node(node, self.mp3.logo, os.path.dirname(file))

    #
    # read the skin informations for a popup
    #
    def read_popup(self, file, popup_node, copy_content):
        if copy_content: self.popup = copy.deepcopy(self.popup)
        self.parse_node(popup_node, self.popup, os.path.dirname(file))

        for node in popup_node.children:
            if node.name == u'message':
                self.parse_node(node, self.popup.message)


    #
    # parse one main menu node
    #
    def parse_mainmenunode(self, node, data):
        data.name = attr_str(node, "name", data.name)
        data.visible = attr_bool(node, "visible", data.visible)
        data.icon = attr_str(node, "icon", data.icon)
        data.pos = attr_int(node, "pos", data.pos)
        data.action = attr_str(node,"action", data.action)
        data.arg = attr_str(node,"arg", data.arg)

    #
    # read the main menu
    #
    def read_mainmenu(self, file, menu_node):
        for node in menu_node.children:
            if node.name == u'item':
                item = XML_mainmenuitem()
                self.parse_mainmenunode(node, item)
                self.mainmenu.items[item.pos] = item                


    # parse listing conf from extendedmenu
    def parse_listingnode(self, node, data):
        self.parse_node(node, data)
        for subnode in node.children:
            if subnode.name == u'expand':
                self.parse_node(subnode, data.expand)
            elif subnode.name == u'head':
                self.parse_node(subnode, data.head)
            elif subnode.name == u'border':
                data.border_size = attr_int(subnode,'size', data.border_size)
                data.border_color = attr_hex(subnode,'color', data.border_color)
            elif subnode.name == u'spacing':
                data.spacing = attr_int(subnode,'value', data.spacing, self.scale)
            elif subnode.name == u'channel_width':
                data.channel_width = attr_int(subnode,'value', data.channel_width, self.scale)
            elif subnode.name == u'indicator':
                for sub_subnode in subnode.children:
                    if sub_subnode.name == u'left':
                        data.left_arrow = attr_str(sub_subnode,'image', data.left_arrow)
                    if sub_subnode.name == u'right':
                        data.right_arrow = attr_str(sub_subnode,'image', data.right_arrow)
                    if sub_subnode.name == u'down':
                        data.down_arrow = attr_str(sub_subnode,'image', data.down_arrow)
                    if sub_subnode.name == u'up':
                        data.up_arrow = attr_str(sub_subnode,'image', data.up_arrow)
                        

    #
    # read the skin informations for extendedmenu
    #
    def read_extendedmenu(self, file, menu_node, copy_content):
        emn = attr_str(menu_node, "type", None)
        if not emn:
            return

        if not 'tv' in self.e_menu:
            self.e_menu[emn] = XML_extendedmenu() 
        else:
            if copy_content: self.e_menu = copy.deepcopy(self.e_menu)

        for node in menu_node.children:
            if node.name == u'background':
                self.parse_node(node, self.e_menu[emn].background, os.path.dirname(file))
            elif node.name == u'logo':
                self.parse_node(node, self.e_menu[emn].logo, os.path.dirname(file))
            elif node.name == u'header':
                self.parse_node(node, self.e_menu[emn].header)
            elif node.name == u'view':
                self.parse_node(node, self.e_menu[emn].view)
            elif node.name == u'info':
                self.parse_node(node, self.e_menu[emn].info)
            elif node.name == u'listing':
                self.parse_listingnode(node, self.e_menu[emn].listing)


    #
    # parse the skin file
    #
    def load(self, file, copy_content = 0):
        if not os.path.isfile(file):
            return 0
        
        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            for freevo_type in box.children:
                if freevo_type.name == 'skin':

                    scale = attr_float(freevo_type, "scale", 0.0)
                    include = attr_file(freevo_type, "include", "", \
                                             os.path.dirname(file))
                    if include:
                        self.scale = scale
                        print "load %s" % include
                        self.load(include + ".xml")
                        self.scale = 0.0
                    
                    for node in freevo_type.children:
                        if node.name == u'menu':
                            type = attr_str(node, "type", "all")
                            if type == "all":
                                if copy_content:
                                    self.menu_default = copy.deepcopy(self.menu_default)
                                    self.menu_main = copy.deepcopy(self.menu_main)
                                    self.menu_tv = copy.deepcopy(self.menu_tv)
                                self.read_menu(file, node, self.menu_default)
                                self.read_menu(file, node, self.menu_main)
                                self.read_menu(file, node, self.menu_tv)

                            if type == "main":
                                self.read_menu(file, node, self.menu_main)

                            if type == "tv":
                                self.read_menu(file, node, self.menu_tv)

                        if node.name == u'mp3':
                            self.read_mp3(file, node, copy_content)
                        if node.name == u'popup':
                            self.read_popup(file, node, copy_content)
                        if node.name == u'main':
                            self.read_mainmenu(file, node)
                        if node.name == u'extendedmenu':
                            self.read_extendedmenu(file, node, copy_content)
                        
        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

        return 1
