#if 0
# -----------------------------------------------------------------------
# xml_skin.py - XML reader for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.31  2003/03/23 21:40:32  dischi
# small bugfixes for loading a new skin
#
# Revision 1.30  2003/03/23 20:50:07  dischi
# bugfix
#
# Revision 1.29  2003/03/23 19:57:11  dischi
# Moved skin xml files to skins/xml/type1 and all stuff for blue_round2 to
# skins/xml/blue_round2
#
# Revision 1.28  2003/03/22 20:08:31  dischi
# Lots of changes:
# o blue2_big and blue2_small are gone, it's only blue2 now
# o Support for up/down arrows in the listing area
# o a sutitle area for additional title information (see video menu in
#   blue2 for an example)
# o some layout changes in blue2 (experimenting with the skin)
# o the skin searches for images in current dir, skins/images and icon dir
# o bugfixes
#
# Revision 1.27  2003/03/21 19:50:54  dischi
# moved some main menu settings from skin to freevo_config.py
#
# Revision 1.26  2003/03/16 19:32:05  dischi
# function prepaire to resolve all the references
# color can be a reference to a <color> tag
#
# Revision 1.25  2003/03/14 19:38:03  dischi
# Support the new <menu> and <menuset> structure. See the blue2 skins
# for example
#
# Revision 1.24  2003/03/13 21:01:15  dischi
# docs update
#
# Revision 1.23  2003/03/08 17:36:47  dischi
# integration of the tv guide
#
# Revision 1.22  2003/03/07 22:54:12  dischi
# First version of the extended menu with image support. Try the music menu
# and press DISPLAY
#
# Revision 1.21  2003/03/07 17:28:40  dischi
# added support for extended menus
#
# Revision 1.20  2003/03/06 21:42:57  dischi
# Added text as content
#
# Revision 1.19  2003/03/05 21:57:15  dischi
# Added audio player. The info area is empty right now, but this skin
# can player audio files
#
# Revision 1.18  2003/03/02 21:48:34  dischi
# Support for skin changing in the main menu
#
# Revision 1.17  2003/03/02 11:46:32  dischi
# Added GetPopupBoxStyle to return popup box styles to the gui
#
# Revision 1.16  2003/03/01 00:12:20  dischi
# Some bug fixes, some speed-ups. blue_round2 has a correct main menu,
# but on the main menu the idle bar still flickers (stupid watermarks),
# on other menus it's ok.
#
# Revision 1.15  2003/02/27 22:39:50  dischi
# The view area is working, still no extended menu/info area. The
# blue_round1 skin looks like with the old skin, blue_round2 is the
# beginning of recreating aubin_round1. tv and music player aren't
# implemented yet.
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
import config

import osd

# XML support
from xml.utils import qp_xml

TRUE  = 1
FALSE = 0

osd = osd.get_singleton()

# XXX Shouldn't this be moved to the config file?

OSD_FONT_DIR = 'skins/fonts/'

geometry = (config.CONF.width, config.CONF.height)

#
# Help functions
#


def attr_int(node, attr, default, scale=0.0):
    """
    return the attribute as integer
    """
    try:
        if node.attrs.has_key(('', attr)):
            max = FALSE
            val = node.attrs[('', attr)]
            if val[:3] == 'max':
                max = TRUE
                val = val[3:]
            if not val:
                val = 0
            
            # scale, but not small values, they may be 0 after scaling
            if scale and int(val) > 4:
                val = scale*int(val)
            if max:
                if int(val) < 0:
                    return 'MAX%d' % int(val)
                else:
                    return 'MAX+%d' % int(val)
            else:
                return int(val)

    except ValueError:
        pass
    return default


def attr_col(node, attr, default):
    """
    return the attribute in hex as integer or str for color name
    """
    try:
        if node.attrs.has_key(('', attr)):
            if node.attrs[('', attr)][:2] == '0x':
                return long(node.attrs[('', attr)], 16)
            else:
                return node.attrs[('', attr)].encode('latin-1')
    except ValueError:
        pass
    return default


def attr_visible(node, attr, default):
    """
    return TRUE or FALSE based in the attribute values 'yes' or 'no'
    """
    if node.attrs.has_key(('', attr)):
        if node.attrs[('', attr)] == "no":
            return ''
        return node.attrs[('', attr)].encode('latin-1')
    return default


def attr_str(node, attr, default):
    """
    return the attribute as string
    """
    if node.attrs.has_key(('', attr)):
        return node.attrs[('', attr)].encode('latin-1')
    return default


def attr_font(node, attr, default):
    """
    return the attribute as font (with full path)
    """
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
            font = config.OSD_DEFAULT_FONTNAME
        return font
    return default


def search_file(file, search_dirs):
    for s_dir in search_dirs:
        dfile=os.path.join(s_dir, file)

        if os.path.isfile(dfile):
            return dfile
        if os.path.isfile("%s_%sx%s.png" % (dfile, config.CONF.width,
                                            config.CONF.height)):
            return "%s_%sx%s.png" % (dfile, config.CONF.width, config.CONF.height)
        if os.path.isfile("%s_%sx%s.jpg" % (dfile, config.CONF.width,
                                            config.CONF.height)):
            return "%s_%sx%s.jpg" % (dfile, config.CONF.width, config.CONF.height)
        if config.CONF.width == 720 and os.path.isfile("%s_768x576.png" % dfile):
            return "%s_768x576.png" % dfile
        if config.CONF.width == 720 and os.path.isfile("%s_768x576.jpg" % dfile):
            return "%s_768x576.jpg" % dfile
        if os.path.isfile("%s.png" % dfile):
            return "%s.png" % dfile
        if os.path.isfile("%s.jpg" % dfile):
            return "%s.jpg" % dfile

    print 'can\'t find image %s' % file
    return ''



# ======================================================================

#
# data structures
#


# ======================================================================

class XML_mainmenuitem:
    def __init__(self):
        self.label = ''
        self.name  = ''
        self.icon  = ''
        self.image = ''

    def parse(self, node, scale, c_dir=''):
        self.label = attr_str(node, "label", self.label)
        self.name  = attr_str(node, "name",  self.name)
        self.icon  = attr_str(node, "icon",  self.icon)
        self.image = attr_str(node, "image", self.image)

    def prepaire(self, search_dirs):
        if self.image:
            self.image = search_file(self.image, search_dirs)
            

# ======================================================================

class XML_mainmenu:
    def __init__(self):
        self.items = {}

    def parse(self, menu_node, scale, c_dir=''):
        for node in menu_node.children:
            if node.name == u'item':
                item = XML_mainmenuitem()
                item.parse(node, scale, c_dir)
                self.items[item.label] = item                

    def prepare(self, search_dirs):
        for i in self.items:
            self.items[i].prepaire(search_dirs)
    
# ======================================================================
# ======================================================================

XML_types = {
    'x'        : ('int',  1),
    'y'        : ('int',  2),
    'width'    : ('int',  1),
    'height'   : ('int',  2),
    'spacing'  : ('int',  3),
    'color'    : ('col',  0),
    'bgcolor'  : ('col',  0),
    'size'     : ('int',  3),
    'radius'   : ('int',  3),
    'label'    : ('str',  0),
    'font'     : ('str',  0),
    'layout'   : ('str',  0),
    'type'     : ('str',  0),
    'align'    : ('str',  0),
    'valign'   : ('str',  0),
    'filename' : ('str', 0),
    'name'     : ('font',  0),
    'visible'  : ('visible', 0)
}

class XML_data:
    """
    a basic data element for parsing the attributes
    """

    def __init__(self, content):
        """
        create all object variables for this type
        """
        self.content = content
        for c in content:
            if XML_types[c][0] in ('str', 'file', 'font'):
                setattr(self, c, '')
            elif XML_types[c][0] in ('visible',):
                setattr(self, c, 'yes')
            else:
                setattr(self, c, 0)

    
    def parse(self, node, scale, current_dir):
        """
        parse the node
        """
        for attr in node.attrs:
            c = attr[1].encode('latin-1')

            if c in self.content:
                this_scale = 0
                if XML_types[c][1] == 1: this_scale = scale[0]
                if XML_types[c][1] == 2: this_scale = scale[1]
                if XML_types[c][1] == 3: this_scale = min(scale[0], scale[1])

                if this_scale:
                    e = 'attr_int(node, "%s", self.%s, %s)' % (c, c, this_scale)
                else:
                    e = 'attr_%s(node, "%s", self.%s)' % (XML_types[c][0], c, c)
                setattr(self, c, eval(e))


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        for c in self.content:
            if eval("self.%s != other.%s" % (c, c)):
                return 1
        return 0
    

# ======================================================================


class XML_menu:
    """
    the menu style definitions
    """
    def __init__(self):
        self.style = []
        pass
    
    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            if subnode.name == 'style':
                self.style += [ [ attr_str(subnode, 'image', ''),
                                  attr_str(subnode, 'text', '') ] ]

    def prepare(self, menuset, layout):
        for s in self.style:
            for i in range(2):
                if s[i]:
                    s[i] = copy.deepcopy(menuset[s[i]])
                    s[i].prepare(layout)
                else:
                    s[i] = None

        

class XML_menuset:
    """
    the complete menu with the areas screen, title, subtitle, view, listing and info in it
    """
    def __init__(self):
        self.content = ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info' )
        for c in self.content:
            setattr(self, c, XML_area(c))


    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            for c in self.content:
                if subnode.name == c:
                    eval('self.%s.parse(subnode, scale, current_dir)' % c)


    def prepare(self, layout):
        for c in self.content:
            eval('self.%s.prepare(layout)' % c)



class XML_area(XML_data):
    """
    area class (inside menu)
    """
    def __init__(self, name):
        XML_data.__init__(self, ('visible', 'layout', 'x', 'y', 'width', 'height'))
        self.name = name
        if name == 'listing':
            self.images = {}
        self.x = -1
        self.y = -1
        self.visible = FALSE

    def parse(self, node, scale, current_dir):
        if self.x == -1:
            self.visible = TRUE

        x = self.x
        y = self.y
        XML_data.parse(self, node, scale, current_dir)
        if x != self.x:
            self.x += config.OVERSCAN_X
        if y != self.y:
            self.y += config.OVERSCAN_Y
        for subnode in node.children:
            if subnode.name == u'image' and self.name == 'listing':
                label = attr_str(subnode, 'label', '')
                if label:
                    if not label in self.images:
                        self.images[label] = XML_image()
                    x,y = self.images[label].x, self.images[label].y
                    self.images[label].parse(subnode, scale, current_dir)
                    if x != self.images[label].x:
                        self.images[label].x += config.OVERSCAN_X
                    if y != self.images[label].y:
                        self.images[label].y += config.OVERSCAN_Y

    def prepare(self, layout):
        if self.visible:
            self.layout = layout[self.layout]
        else:
            self.layout = None
            
    def rect(self, type):
        if type == 'screen':
            return (self.x - config.OVERSCAN_X, self.y - config.OVERSCAN_X,
                    self.width + 2 * config.OVERSCAN_X,
                    self.height + 2 * config.OVERSCAN_X)
        return (self.x, self.y, self.width, self.height)

    def pos(self, type):
        if type == 'screen':
            return (self.x - config.OVERSCAN_X, self.y - config.OVERSCAN_X)
        return (self.x, self.y)


# ======================================================================

class XML_layout:
    """
    layout tag
    """
    def __init__(self, label):
        self.label = label
        self.background = ()
        self.content = XML_content()
        
    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            if subnode.name == u'background':
                self.background = []
                for bg in subnode.children:
                    if bg.name in ( 'image', 'rectangle' ):
                        b = eval('XML_%s()' % bg.name)
                        b.parse(bg, scale, current_dir)
                        self.background += [ b ]
            if subnode.name == u'content':
                self.content.parse(subnode, scale, current_dir)

    def prepare(self, font, color, search_dirs):
        self.content.prepare(font, color)
        for b in self.background:
            b.prepare(color, search_dirs)
            
    def __cmp__(self, other):
        return not (self.background == other.background and self.content == other.content)


class XML_content(XML_data):
    """
    content inside a layout
    """
    def __init__(self):
        XML_data.__init__(self, ('type', 'spacing', 'x', 'y', 'width',
                                 'height', 'font', 'align', 'valign', 'color'))
        self.types = {}
        self.cdata = ''
        
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        self.cdata = node.textof()
        for subnode in node.children:
            if subnode.name == u'item':
                type = attr_str(subnode, "type", '')
                if type and not self.types.has_key(type):
                    self.types[type] = XML_data(('font', 'align', 'valign', 'height',
                                                 'width'))
                    self.types[type].rectangle = None
                    self.types[type].cdata = ''
                if type:
                    self.types[type].parse(subnode, scale, current_dir)
                    self.types[type].cdata = subnode.textof()
                    for rnode in subnode.children:
                        if rnode.name == u'rectangle':
                            self.types[type].rectangle = XML_rectangle()
                            self.types[type].rectangle.parse(rnode, scale, current_dir)

        if not self.types.has_key('default'):
            self.types['default'] = XML_data(('font',))
            self.types['default'].rectangle = None
            self.types['default'].cdata = ''
        

    def prepare(self, font, color):
        if self.font:
            try:
                self.font = font[self.font]
            except:
                print 'can\'t find font %s' % self.font
                print font
        else:
            self.font = None

        if color.has_key(self.color):
            self.color = color[self.color]

        for type in self.types:
            if self.types[type].font:
                self.types[type].font = font[self.types[type].font]
            else:
                self.types[type].font = None
            if self.types[type].rectangle:
                self.types[type].rectangle.prepare(color)
        
# ======================================================================

class XML_image(XML_data):
    """
    an image
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'filename', 'label'))

    def prepare(self, color, search_dirs):
        """
        try to guess the image localtion
        """
        if self.filename:
            self.filename = search_file(self.filename, search_dirs)
    


class XML_rectangle(XML_data):
    """
    a rectangle
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'color',
                                 'bgcolor', 'size', 'radius' ))

    def prepare(self, color, search_dirs=None):
        if color.has_key(self.color):
            self.color = color[seld.color]
        if color.has_key(self.bgcolor):
            self.bgcolor = color[self.bgcolor]



class XML_font(XML_data):
    """
    font tag
    """
    def __init__(self, label):
        XML_data.__init__(self, ('name', 'size', 'color'))
        self.label = label
        self.shadow = XML_data(('visible', 'color', 'x', 'y'))
        self.shadow.visible = FALSE
        
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        for subnode in node.children:
            if subnode.name == u'shadow':
                self.shadow.parse(subnode, scale, current_dir)

    def prepare(self, color, search_dirs=None):
        if color.has_key(self.color):
            self.color = color[self.color]
        self.h = osd.stringsize('Ajg', self.name, self.size)[1]

        if self.shadow.visible:
            if color.has_key(self.shadow.color):
                self.shadow.color = color[self.shadow.color]
            self.h += self.shadow.y
        
    def __cmp__(self, other):
        return not (not XML_data.__cmp__(self, other) and self.shadow == other.shadow)

    
# ======================================================================


class XML_player:
    """
    player tag for the audio play skin
    """
    def __init__(self):
        self.content = ( 'screen', 'title', 'subtitle', 'view', 'info' )
        for c in self.content:
            setattr(self, c, XML_area(c))


    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            for c in self.content:
                if subnode.name == c:
                    eval('self.%s.parse(subnode, scale, current_dir)' % c)

    def prepare(self, layout):
        for c in self.content:
            eval('self.%s.prepare(layout)' % c)

# ======================================================================


class XML_tv:
    """
    tv tag for the tv menu
    """
    def __init__(self):
        self.content = ( 'screen', 'title', 'subtitle', 'view', 'info', 'listing' )
        for c in self.content:
            setattr(self, c, XML_area(c))


    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            for c in self.content:
                if subnode.name == c:
                    eval('self.%s.parse(subnode, scale, current_dir)' % c)

    def prepare(self, layout):
        for c in self.content:
            eval('self.%s.prepare(layout)' % c)

# ======================================================================



class XMLSkin:
    """
    skin main settings class
    """
    def __init__(self):

        self._layout = {}
        self._font = {}
        self._color = {}
        self._menuset = {}
        self._menu = {}
        self._popup = ''
        self._player = XML_player()
        self._tv = XML_tv()
        self._mainmenu = XML_mainmenu()

        self.icon_dir = ""

        
    def parse(self, freevo_type, scale, c_dir, copy_content):
        for node in freevo_type.children:
            if node.name == u'main':
                self._mainmenu.parse(node, scale, c_dir)

            if node.name == u'menu':
                type = attr_str(node, 'type', 'default')

                if type == 'all':
                    # if type is all, all types except default are deleted and
                    # the settings will be loaded for default
                    self._menu = {}
                    type = 'default'
                    
                self._menu[type] = XML_menu()
                self._menu[type].parse(node, scale, c_dir)


            if node.name == u'menuset':
                label   = attr_str(node, 'label', '')
                inherit = attr_str(node, 'inherits', '')
                if inherit:
                    self._menuset[label] = copy.deepcopy(self._menuset[inherit])
                elif not self._menuset.has_key(label):
                    self._menuset[label] = XML_menuset()
                self._menuset[label].parse(node, scale, c_dir)


            if node.name == u'layout':
                label = attr_str(node, 'label', '')
                if label:
                    if not self._layout.has_key(label):
                        self._layout[label] = XML_layout(label)
                    self._layout[label].parse(node, scale, c_dir)
                        

            if node.name == u'font':
                label = attr_str(node, 'label', '')
                if label:
                    if not self._font.has_key(label):
                        self._font[label] = XML_font(label)
                    self._font[label].parse(node, scale, c_dir)

            if node.name == u'color':
                label = attr_str(node, 'label', '')
                if label:
                    value = attr_col(node, 'value', '')
                    self._color[label] = value
                        

            if node.name == u'iconset':
                self.icon_dir = attr_str(node, 'dir', self.icon_dir)

            if node.name == u'popup':
                self._popup = attr_str(node, 'layout', self._popup)

            if node.name == u'player':
                self._player.parse(node, scale, c_dir)

            if node.name == u'tv':
                self._tv.parse(node, scale, c_dir)



    def load(self, file, copy_content = 0, prepare = TRUE, clear=FALSE):
        """
        load and parse the skin file
        """

        if not os.path.isfile(file):
            if os.path.isfile(file+".fxd"):
                file += ".fxd"
            elif os.path.isfile('skins/xml/%s/%s.fxd' % (file, file)):
                file = 'skins/xml/%s/%s.fxd' % (file, file)
            else:
                file = "skins/xml/type1/%s" % file
                if os.path.isfile(file+".fxd"):
                    file += ".fxd"

        if not os.path.isfile(file):
            return 0

        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            for freevo_type in box.children:
                if freevo_type.name == 'skin':

                    file_geometry = attr_str(freevo_type, "geometry", '')

                    if file_geometry:
                        w, h = file_geometry.split('x')
                    else:
                        w = config.CONF.width
                        h = config.CONF.height
                        
                    scale = (float(config.CONF.width-2*config.OVERSCAN_X)/float(w),
                             float(config.CONF.height-2*config.OVERSCAN_Y)/float(h))

                    include  = attr_str(freevo_type, 'include', '')

                    if include:
                        if clear:
                            self._layout = {}
                            self._font = {}
                            self._color = {}
                            self._menuset = {}
                            self._menu = {}
                            self._popup = ''
                            self._player = XML_player()
                            self._tv = XML_tv()
                            self._mainmenu = XML_mainmenu()
                            
                        self.load(include, copy_content, prepare = FALSE)

                    self.parse(freevo_type, scale, os.path.dirname(file), copy_content)

            if not prepare:
                return 1
        
            self.menu   = copy.deepcopy(self._menu)
            self.tv     = copy.deepcopy(self._tv)
            self.player = copy.deepcopy(self._player)

            font        = copy.deepcopy(self._font)
            layout      = copy.deepcopy(self._layout)

            search_dirs = (os.path.dirname(file), 'skins/images', self.icon_dir, '.')
            for f in font:
                font[f].prepare(self._color)
                
            for l in layout:
                layout[l].prepare(font, self._color, search_dirs)
            for menu in self.menu:
                self.menu[menu].prepare(self._menuset, layout)

                # prepare listing area images
                for s in self.menu[menu].style:
                    for i in range(2):
                        if s[i] and hasattr(s[i], 'listing'):
                            for image in s[i].listing.images:
                                s[i].listing.images[image].prepare(None, search_dirs)
                        
                
            self.player.prepare(layout)
            self.tv.prepare(layout)
            # prepare listing area images
            for image in self.tv.listing.images:
                self.tv.listing.images[image].prepare(None, search_dirs)

            self.popup = layout[self._popup]

            self.mainmenu = copy.deepcopy(self._mainmenu)
            self.mainmenu.prepare(search_dirs)
            return 1

        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

