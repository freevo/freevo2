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
# Revision 1.11  2003/02/25 23:27:36  dischi
# changed max usage
#
# Revision 1.10  2003/02/25 22:56:00  dischi
# New version of the new skin. It still looks the same (except that icons
# are working now), but the internal structure has changed. Now it will
# be easier to do the next steps.
#
# Revision 1.9  2003/02/23 18:42:20  dischi
# Current status of my skin redesign. Currently only the background and
# the listing area is working, the listing without icons. Let me know what
# you thing before I spend more time with it
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

# XML support
from xml.utils import qp_xml

TRUE  = 1
FALSE = 0


# XXX Shouldn't this be moved to the config file?

OSD_FONT_DIR = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/kimberly_alt.ttf'

geometry = (config.CONF.width, config.CONF.height)

#
# Help functions
#
def attr_int(node, attr, default, scale=0.0):
    try:
        if node.attrs.has_key(('', attr)):
            max = FALSE
            val = node.attrs[('', attr)]
            if val[:3] == 'max':
                max = TRUE
                val = val[3:]
            if not val:
                val = 0
            
            if scale:
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
            dfile=os.path.join(c_dir, file)
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
            if os.path.isfile("%s_800x600.png" % dfile):
                return "%s_800x600.png" % dfile
            if os.path.isfile("%s_800x600.jpg" % dfile):
                return "%s_800x600.jpg" % dfile
        return file
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


# ======================================================================

class XML_mainmenuitem:
    def __init__(self):
        self.name = ''
        self.visible = 'yes'
        self.icon = ''
        self.image = ''
        self.pos = 0
        self.action = None
        self.arg = None

    def parse(self, node, scale, c_dir=''):
        self.name = attr_str(node, "name", self.name)
        self.visible = attr_visible(node, "visible", self.visible)
        self.icon = attr_str(node, "icon", self.icon)
        self.image = attr_str(node, "image", self.image)
        self.pos = attr_int(node, "pos", self.pos)

        self.action = attr_str(node,"action", self.action)
        self.arg = attr_str(node,"arg", self.arg)


# ======================================================================

class XML_mainmenu:
    def __init__(self):
        self.items = {}

    def parse(self, menu_node, scale, c_dir=''):
        for node in menu_node.children:
            if node.name == u'item':
                item = XML_mainmenuitem()
                item.parse(node, scale, c_dir)
                self.items[item.pos] = item                

    
# ======================================================================
# ======================================================================

XML_types = {
    'x'        : ('int',  1),
    'y'        : ('int',  2),
    'width'    : ('int',  1),
    'height'   : ('int',  2),
    'spacing'  : ('int',  3),
    'color'    : ('hex',  0),
    'bgcolor'  : ('hex',  0),
    'size'     : ('int',  3),
    'radius'   : ('int',  3),
    'base'     : ('str',  0),
    'font'     : ('str',  0),
    'layout'   : ('str',  0),
    'type'     : ('str',  0),
    'align'    : ('str',  0),
    'valign'   : ('str',  0),
    'filename' : ('file', 0),
    'name'     : ('font',  0),
    'visible'  : ('visible', 0)
}

class XML_data:
    def __init__(self, content):
        self.content = content
        for c in content:
            if XML_types[c][0] in ('str', 'file', 'font'):
                setattr(self, c, '')
            elif XML_types[c][0] in ('visible',):
                setattr(self, c, 1)
            else:
                setattr(self, c, 0)

    
    def parse(self, node, scale, current_dir):
        for attr in node.attrs:
            c = attr[1].encode('latin-1')

            if c in self.content:
                this_scale = 0
                if XML_types[c][1] == '1': this_scale = scale[0]
                if XML_types[c][1] == '2': this_scale = scale[1]
                if XML_types[c][1] == '3': this_scale = min(scale[0], scale[1])

                if this_scale:
                    e = 'attr_int(node, "%s", self.%s, %s)' % (c, c, this_scale)
                elif XML_types[c][0] == 'file':
                    e = 'attr_file(node, "%s", self.%s, "%s")' % (c, c, current_dir)
                else:
                    e = 'attr_%s(node, "%s", self.%s)' % (XML_types[c][0], c, c)
                setattr(self, c, eval(e))


    def __cmp__(self, other):
        for c in self.content:
            if eval("self.%s != other.%s" % (c, c)):
                return 1
        return 0
    
# ======================================================================
# ======================================================================

class XML_area(XML_data):
    def __init__(self):
        XML_data.__init__(self, ('visible', 'layout', 'x', 'y', 'width', 'height'))
        self.area2   = None
        pass
    
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        area = 1
        for subnode in node.children:
            if subnode.name == u'area' and area == 1:
                XML_data.parse(self, subnode, scale, current_dir)
                area = 2
            elif subnode.name == u'area' and area == 2:
                if not self.area2:
                    self.area2 = XML_data('x', 'y', 'width', 'height')
                    self.area2.parse(subnode, scale, current_dir)

    def __cmp__(self, other):
        return not (not XML_data.__cmp__(self, other) and self.area2 == other.area2)

    
class XML_menu:
    def __init__(self):
        self.content = ( 'screen', 'title', 'view', 'listing', 'info' )
        for c in self.content:
            setattr(self, c, XML_area())


    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            for c in self.content:
                if subnode.name == c:
                    eval('self.%s.parse(subnode, scale, current_dir)' % c)
        pass


# ======================================================================

class XML_image(XML_data):
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'filename'))


class XML_rectangle(XML_data):
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'color',
                                 'bgcolor', 'size', 'radius', 'base' ))


class XML_content(XML_data):
    def __init__(self):
        XML_data.__init__(self, ('type', 'spacing', 'x', 'y',
                                 'width', 'height'))
        self.types = {}
        
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        for subnode in node.children:
            if subnode.name == u'item':
                type = attr_str(subnode, "type", '')
                if type and not self.types.has_key(type):
                    self.types[type] = XML_data(('font',))
                    self.types[type].rectangle = None
                if type:
                    self.types[type].parse(subnode, scale, current_dir)
                    for rnode in subnode.children:
                        if rnode.name == u'rectangle':
                            self.types[type].rectangle = XML_rectangle()
                            self.types[type].rectangle.parse(rnode, scale, current_dir)


        
class XML_layout:
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

    def __cmp__(self, other):
        return not (self.background == other.background and self.content == other.content)


# ======================================================================

class XML_font(XML_data):
    def __init__(self, label):
        XML_data.__init__(self, ('name', 'size', 'color', 'align', 'valign'))
        self.label = label
        self.shadow = XML_data(('visible', 'color', 'x', 'y'))
        
    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            if subnode.name == u'definition':
                XML_data.parse(self, subnode, scale, current_dir)
            if subnode.name == u'shadow':
                self.shadow.parse(node, scale, current_dir)

    def __cmp__(self, other):
        return not (not XML_data.__cmp__(self, other) and self.shadow == other.shadow)

    
# ======================================================================
# ======================================================================

#
# Main XML skin class
#
class XMLSkin:
    def __init__(self):
        self.menu = {}
        
        self.menu_types = ( 'default', 'main', 'video', 'audio', 'image' )
        for t in self.menu_types:
            self.menu[t] = [ XML_menu(), ] 

        self.layout = {}
        self.font = {}
        
        self.mainmenu = XML_mainmenu()
        self.icon_dir = ""
        
        
    def parse(self, freevo_type, scale, c_dir, copy_content):
        for node in freevo_type.children:
            if node.name == u'main':
                self.mainmenu.parse(node, scale, c_dir)

            if node.name == u'menu':
                type = attr_str(node, "type", "all")
                if type == "all":
                    if copy_content:
                        self.menu = copy.deepcopy(self.menu)
                    for t in self.menu_types:
                        for e in self.menu[t]:
                            e.parse(node, scale, c_dir)

                if type in self.menu:
                    display = attr_int(node, 'display', 0)
                    self.menu[type][display].parse(node, scale, c_dir)

            if node.name == u'layout':
                label = attr_str(node, 'label', '')
                if label:
                    if not self.layout.has_key(label):
                        self.layout[label] = XML_layout(label)
                    self.layout[label].parse(node, scale, c_dir)
                        
                self.mainmenu.parse(node, scale, c_dir)

            if node.name == u'font':
                label = attr_str(node, 'label', '')
                if label:
                    if not self.font.has_key(label):
                        self.font[label] = XML_font(label)
                    self.font[label].parse(node, scale, c_dir)
                        
                self.mainmenu.parse(node, scale, c_dir)

            if node.name == u'iconset':
                self.icon_dir = attr_str(node, 'dir', self.icon_dir)


    #
    # parse the skin file
    #
    def load(self, file, copy_content = 0):
        if not os.path.isfile(file):
            if os.path.isfile(file+".xml"):
                file += ".xml"
            else:
                file = "skins/dischi/%s" % file
                if os.path.isfile(file+".xml"):
                    file += ".xml"

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

                        
                    include  = attr_file(freevo_type, "include", "", \
                                         os.path.dirname(file))
                    if include:
                        self.load(include, copy_content)

                    self.parse(freevo_type, scale, os.path.dirname(file), copy_content)

        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

        return 1
