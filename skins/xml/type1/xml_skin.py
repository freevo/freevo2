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
# Revision 1.15  2002/10/19 17:09:32  dischi
# Lot of restructuring. Every object now has a function parse to fill
# the internal variables from the xml file. I also fixed scaling when
# you inherit from an already inherit xml file
#
# Revision 1.14  2002/10/19 15:09:19  dischi
# Added support for roundboxes. The file extreme_round_768x576.xml is an
# example of round box usage. blue2_768x576.xml also looks a little bit
# different now, all other skins should still look like before.
#
# You can now add <mask>-tags. All these masks and the selection are drawn
# on the same layer. With that it is possible to undo the alpha changes in
# a selection. So the alpha values in colors are changes to the background
# image, not the current background (image+alpha mask)
#
# Revision 1.13  2002/10/16 19:38:56  dischi
# o Removed older xml files
# o changed to structure in the xml files. In listings is now a section
#   table (that's what the tv menu is) with label (ex-head) and content
# o support in xml_skin.py for that, changed also skin_main1
#
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

def attr_visible(node, attr, default):
    if node.attrs.has_key(('', attr)):
        if node.attrs[('', attr)] == "no":
            return ''
        return node.attrs[('', attr)].encode('latin-1')
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
        self.visible = 'yes'
        self.text = None
        self.font = OSD_DEFAULT_FONT
        self.mode=''
        self.shadow_visible = ''
        self.shadow_color = 0
        self.shadow_pad_x = 1
        self.shadow_pad_y = 1
        self.border_color = 0
        self.border_size = 0
        self.align = 'left'
        self.valign = 'top'
        self.image = ''
        self.mask = ''
        self.radius = 0
        self.spacing = 10
        
        
    def parse(self, node, scale = 0.0, c_dir=''):
        self.x = attr_int(node, "x", self.x, scale)
        self.y = attr_int(node, "y", self.y, scale)
        self.height = attr_int(node, "height", self.height, scale)
        self.width = attr_int(node, "width", self.width, scale)
        self.length = attr_int(node, "length", self.length, scale)
        self.radius = attr_int(node, "radius", self.radius, scale)
        self.spacing = attr_int(node, "spacing", self.spacing, scale)

        self.visible = attr_visible(node, "visible", self.visible)
        self.bgcolor = attr_hex(node, "bgcolor", self.bgcolor)
        self.color = attr_hex(node, "color", self.color) # will be overrided by font
        self.border_color = attr_hex(node, "border_color", self.border_color)
        self.border_size = attr_int(node, "border_size", self.border_size)
        self.image = attr_file(node, "image", self.image, c_dir)
        self.mask = attr_file(node, "mask", self.mask, c_dir)

        for subnode in node.children:
            if subnode.name == u'font':
                self.color = attr_hex(subnode, "color", self.color)
                self.size = attr_int(subnode, "size", self.size, scale)
                self.font = attr_font(subnode, "name", self.font)
                self.align = attr_str(subnode, "align", self.align)
                self.valign = attr_str(subnode, "valign", self.valign)
            if subnode.name == u'selection':
                self.selection.parse(subnode, scale)
            if subnode.name == u'text':
                self.text = subnode.textof()
            if subnode.name == u'shadow':
                self.shadow_visible = attr_visible(subnode, "visible", self.shadow_visible)
                self.shadow_color = attr_hex(subnode, "color", self.shadow_color)
                self.shadow_pad_x = attr_int(subnode, "x", self.shadow_pad_x)
                self.shadow_pad_y = attr_int(subnode, "y", self.shadow_pad_y)
            if subnode.name == u'background':
                self.bgcolor = attr_hex(subnode, "color", self.bgcolor)                
                self.radius = attr_int(subnode, "radius", self.radius)                
            if subnode.name == u'geometry':
                self.x = attr_int(subnode, "x", self.x, scale)
                self.y = attr_int(subnode, "y", self.y, scale)
                self.width = attr_int(subnode, "width", self.width, scale)
                self.height = attr_int(subnode, "height", self.height, scale)



# ======================================================================

class XML_menuitem(XML_data):
    def __init__(self):
        XML_data.__init__(self)
        self.selection = XML_data()

    def parse(self, node, scale = 0.0, c_dir=''):
        XML_data.parse(self, node, scale, c_dir)
        

# ======================================================================

class XML_cover(XML_data):
    def __init__(self):
        XML_data.__init__(self)
        self.mask = None

    def parse(self, node, scale = 0.0, c_dir=''):
        XML_data.parse(self, node, scale, c_dir)
        for subnode in node.children:
            if subnode.name == u'mask':
                self.mask = []
                for masknode in subnode.children:
                    if masknode.name == u'rectangle':
                        rect = XML_data()
                        rect.parse(masknode, scale)
                        self.mask += [ rect ]
        

# ======================================================================

class XML_menuitems:
    def __init__(self):
        self.x = self.y = self.height = self.width = 0
        self.default = XML_menuitem()
        self.dir = XML_menuitem()
        self.pl = XML_menuitem()

    def parse(self, node, scale = 0.0, c_dir=''):
        self.x = attr_int(node, "x", self.x, scale)
        self.y = attr_int(node, "y", self.y, scale)
        self.height = attr_int(node, "height", self.height, scale)
        self.width  = attr_int(node, "width", self.width, scale)

        for subnode in node.children:
            if subnode.name == u'item':
                type = attr_str(subnode, "type", "all")

                if type == "all":
                    # default content, override all settings for pl and dir:
                    self.default.parse(subnode, scale)
                    self.dir.parse(subnode, scale)
                    self.pl.parse(subnode, scale)

                elif type == 'dir':
                    self.dir.parse(subnode, scale)

                elif type == 'playlist':
                    self.pl.parse(subnode, scale)


# ======================================================================

class XML_background:
    def __init__(self):
        self.image     = ''
        self.mask      = None

    def parse(self, node, scale = 0.0, c_dir=''):
        self.image = attr_file(node, "image", self.image, c_dir)
        tmp = attr_file(node, "mask", None, c_dir)
        if not tmp == None:
            self.mask = tmp
        for subnode in node.children:
            if subnode.name == u'mask':
                for masknode in subnode.children:
                    if masknode.name == u'rectangle':
                        rect = XML_data()
                        rect.parse(masknode, scale)
                        try:
                            self.mask += [ rect ]
                        except TypeError:
                            self.mask = [ rect ]


# ======================================================================

class XML_menu:
    def __init__(self):
        self.background = XML_background()
        self.logo = XML_data()
        self.title = XML_data()
        self.items = XML_menuitems()
        self.cover_movie = XML_cover()
        self.cover_music = XML_cover()
        self.cover_image = XML_cover()
        self.submenu = XML_menuitem()

    def parse(self, menu_node, scale = 0.0, c_dir=''):
        for node in menu_node.children:
            if node.name == u'background':
                self.background.parse(node, scale, c_dir)

            if node.name == u'logo':
                self.logo.parse(node, scale, c_dir)

            elif node.name == u'title':
                self.title.parse(node, scale)

            elif node.name == u'items':
                self.items.parse(node, scale, c_dir)
                
            elif node.name == u'covers':
                for subnode in node.children:
                    type = attr_str(subnode, "type", "")

                    if type == u'all':
                        self.cover_movie.parse(subnode, scale)
                        self.cover_music.parse(subnode, scale)
                        self.cover_image.parse(subnode, scale)

                    if type == u'movie':
                        self.cover_movie.parse(subnode, scale)
                    if type == u'music':
                        self.cover_music.parse(subnode, scale)
                    if type == u'image':
                        self.cover_image.parse(subnode, scale)

            elif node.name == u'submenu':
                self.submenu.parse(node, scale)


# ======================================================================

class XML_mp3:
    def __init__(self):
        self.background = XML_background()
        self.progressbar = XML_data()
        self.title = XML_data()    
        self.cover = XML_cover()    
        self.info  = XML_data()
        self.logo  = XML_data()

    def parse(self, menu_node, scale = 0.0, c_dir=''):
        for node in menu_node.children:
            if node.name == u'background':
                self.background.parse(node, scale, c_dir)

            elif node.name == u'title':
                self.title.parse(node, scale)

            elif node.name == u'cover':
                self.cover.parse(node, scale)

            elif node.name == u'progressbar':
                self.progressbar.parse(node, scale)

            elif node.name == u'fileinfo':
                self.info.parse(node, scale)

            elif node.name == u'logo':
                self.logo.parse(node, scale, c_dir)


# ======================================================================

class XML_popup(XML_data):
    def __init__(self):
        XML_data.__init__(self)
        self.message = XML_data()    

    def parse(self, node, scale = 0.0, c_dir=''):
        XML_data.parse(self, node, scale, c_dir)

        for subnode in node.children:
            if subnode.name == u'message':
                self.message.parse(subnode, scale, c_dir)



# ======================================================================

class XML_mainmenuitem:
    def __init__(self):
        self.name = ''
        self.visible = 'yes'
        self.icon = ''
        self.pos = 0
        self.action = None
        self.arg = None

    def parse(self, node, scale = 0.0, c_dir=''):
        self.name = attr_str(node, "name", self.name)
        self.visible = attr_visible(node, "visible", self.visible)
        self.icon = attr_str(node, "icon", self.icon)
        self.pos = attr_int(node, "pos", self.pos)
        self.action = attr_str(node,"action", self.action)
        self.arg = attr_str(node,"arg", self.arg)


# ======================================================================

class XML_mainmenu:
    def __init__(self):
        self.items = {}

    def parse(self, menu_node, scale = 0.0, c_dir=''):
        for node in menu_node.children:
            if node.name == u'item':
                item = XML_mainmenuitem()
                item.parse(node, scale, c_dir)
                self.items[item.pos] = item                

# ======================================================================

class XML_listingmenuitem(XML_menuitem):
    def __init__(self):
        XML_menuitem.__init__(self)
        self.label = XML_data()
        self.expand = XML_data()
        self.border_color = 0
        self.border_size = 1
        self.spacing = 0
        self.left_arrow = None
        self.right_arrow = None
        self.up_arrow = None
        self.down_arrow = None


    def parse_content(self, node, scale):
        self.parse(node, scale)
        for subnode in node.children:
            if subnode.name == u'indicator':
                type = attr_str(subnode, 'type', 'None')
                if type == 'left':
                    self.left_arrow = attr_str(subnode,'image', self.left_arrow)
                if type == 'right':
                    self.right_arrow = attr_str(subnode,'image', self.right_arrow)
                if type == 'down':
                    self.down_arrow = attr_str(subnode,'image', self.down_arrow)
                if type == 'up':
                    self.up_arrow = attr_str(subnode,'image', self.up_arrow)


    def parse(self, node, scale = 0.0, c_dir=''):
        XML_menuitem.parse(self, node, scale, c_dir)
        for subnode in node.children:
            if subnode.name == u'expand':
                self.expand.parse(subnode, scale)

            elif subnode.name == u'table':
                self.spacing = attr_int(subnode,'spacing', self.spacing, scale)
                self.parse(subnode, scale)

                for subsubnode in subnode.children:
                    if subsubnode.name == u'label':
                        self.label.parse(subsubnode, scale)
                    elif subsubnode.name == u'content':
                        self.parse_content(subsubnode, scale)


# ======================================================================

class XML_extendedmenu:
    def __init__(self):
        self.background = XML_background()
        self.logo = XML_data()
        self.header = XML_data()
        self.view = XML_data()
        self.info = XML_data()
        self.listing = XML_listingmenuitem()

    def parse(self, menu_node, scale = 0.0, c_dir=''):
        for node in menu_node.children:
            if node.name == u'background':
                self.background.parse(node, scale, c_dir)
            elif node.name == u'logo':
                self.logo.parse(node, scale, c_dir)
            elif node.name == u'header':
                self.header.parse(node, scale)
            elif node.name == u'view':
                self.view.parse(node, scale)
            elif node.name == u'info':
                self.info.parse(node, scale)
            elif node.name == u'listing':
                self.listing.parse(node, scale)




# ======================================================================
# ======================================================================


#
# Main XML skin class
#
class XMLSkin:
    def __init__(self):
        self.menu_default = XML_menu()
        self.menu_main    = XML_menu()
        self.mp3          = XML_mp3()
        self.popup        = XML_popup()

        self.mainmenu = XML_mainmenu()
        self.e_menu = { }

        
    def parse(self, freevo_type, scale, c_dir, copy_content):
        for node in freevo_type.children:
            if node.name == u'menu':
                type = attr_str(node, "type", "all")
                if type == "all":
                    if copy_content:
                        self.menu_default = copy.deepcopy(self.menu_default)
                        self.menu_main = copy.deepcopy(self.menu_main)
                    self.menu_default.parse(node, scale, c_dir)
                    self.menu_main.parse(node, scale, c_dir)

                if type == "main":
                    self.menu_main.parse(node, scale, c_dir)

            if node.name == u'mp3':
                if copy_content:
                    self.mp3 = copy.deepcopy(self.mp3)
                self.mp3.parse(node, scale, c_dir)

            if node.name == u'popup':
                if copy_content:
                    self.popup = copy.deepcopy(self.popup)
                self.popup.parse(node, scale, c_dir)

            if node.name == u'main':
                self.mainmenu.parse(node, scale, c_dir)

            if node.name == u'extendedmenu':
                emn = attr_str(node, "type", None)
                if emn:
                    if not emn in self.e_menu:
                        self.e_menu[emn] = XML_extendedmenu() 
                    else:
                        if copy_content: self.e_menu[emn] = copy.deepcopy(self.e_menu[emn])
                    self.e_menu[emn].parse(node, scale, c_dir)

        


    #
    # parse the skin file
    #
    def load(self, file, copy_content = 0, scale=0.0):
        if not os.path.isfile(file):
            return 0
        
        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            for freevo_type in box.children:
                if freevo_type.name == 'skin':

                    new_scale = attr_float(freevo_type, "scale", 0.0)
                    include = attr_file(freevo_type, "include", "", \
                                             os.path.dirname(file))

                    if scale and new_scale:
                        new_scale = scale * new_scale
                    elif scale:
                        new_scale = scale
                        
                    if include:
                        print "load %s with scale %s" % (include, new_scale)
                        self.load(include + ".xml", copy_content, new_scale)

                    self.parse(freevo_type, scale, os.path.dirname(file), copy_content)

        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

        return 1
