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
# Revision 1.24  2004/01/01 17:41:05  dischi
# add border support for Font
#
# Revision 1.23  2004/01/01 12:25:07  dischi
# store version information and list of depending files
#
# Revision 1.22  2003/12/14 17:39:52  dischi
# Change TRUE and FALSE to True and False; vfs fixes
#
# Revision 1.21  2003/12/06 13:43:03  dischi
# more cleanup
#
# Revision 1.20  2003/12/05 18:07:55  dischi
# renaming of XML_xxx variables to Xxx
#
# Revision 1.19  2003/12/03 21:50:44  dischi
# rework of the loading/selecting
# o all objects that need a skin need to register what they areas they need
# o remove all 'player' and 'tv' stuff to make it more generic
# o renamed some skin function names
#
# Revision 1.18  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.17  2003/11/23 19:01:39  dischi
# support for new fxd parser
#
# Revision 1.16  2003/10/22 18:23:56  dischi
# speedup and less debug
#
# Revision 1.15  2003/10/21 23:46:22  gsbarbieri
# Info_Area now support images as
#    <img src="file" x="1" y="2" width="123" height="456" />
# x and y are optional and will be set to "pen position" when not specified.
# width and height are also optional and defaults to the image size.
# file is the filename.
#
# <img> will define FLOAT images, not inline ones. You can simulate inline
# images with <goto_pos>... Maybe someday, if needed, someone can implement it.
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
import os
import copy
import re
import traceback
import config
import util

import osd
import plugin

# XML support
from xml.utils import qp_xml

osd = osd.get_singleton()

geometry = (config.CONF.width, config.CONF.height)


FXD_FORMAT_VERSION = 1

#
# Help functions
#


def attr_int(node, attr, default, scale=0.0):
    """
    return the attribute as integer
    """
    try:
        if node.attrs.has_key(('', attr)):
            val = node.attrs[('', attr)]
            if val == 'line_height':
                return -1
            new_val = ''

            while val:
                ppos = val[1:].find('+') + 1
                mpos = val[1:].find('-') + 1
                if ppos and mpos:
                    pos = min(ppos, mpos)
                elif ppos or mpos:
                    pos = max(ppos, mpos)
                else:
                    pos = len(val)

                try:
                    i = int(round(scale*int(val[:pos])))
                    if i < 0:
                        new_val += str(i)
                    else:
                        new_val += '+' + str(i)
                except ValueError:
                    if val[:pos].upper() in ( '+MAX', 'MAX', '-MAX' ):
                        new_val += val[:pos].upper()
                    elif val[:pos].lower() in ( '+font_h', 'font_h', '-font_h' ):
                        new_val += val[:pos].lower()
                    else:
                        print 'WARNING: unsupported value %s' % val[:pos]
                val = val[pos:]

            try:
                return int(new_val)
            except ValueError:
                return str(new_val)

    except ValueError:
        pass
    return default


def attr_float(node, attr, default):
    """
    return the attribute as integer
    """
    try:
        if node.attrs.has_key(('', attr)):
            return float(node.attrs[('', attr)])
        
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
                return node.attrs[('', attr)].encode(config.LOCALE)
    except ValueError:
        pass
    return default


def attr_visible(node, attr, default):
    """
    return True or False based in the attribute values 'yes' or 'no'
    """
    if node.attrs.has_key(('', attr)):
        if node.attrs[('', attr)] == "no":
            return ''
        return node.attrs[('', attr)].encode(config.LOCALE)
    return default


def attr_str(node, attr, default):
    """
    return the attribute as string
    """
    if node.attrs.has_key(('', attr)):
        return node.attrs[('', attr)].encode(config.LOCALE)
    return default


def attr_font(node, attr, default):
    """
    return the attribute as font (with full path)
    """
    if node.attrs.has_key(('', attr)):
        fontext = os.path.splitext(node.attrs[('', attr)])[1]
        if fontext:
            # There is an extension (e.g. '.pfb'), use the full name
            font = os.path.join(config.FONT_DIR,
                                node.attrs[('', attr)]).encode(config.LOCALE)
        else:
            # '.ttf' is the default extension
            font = os.path.join(config.FONT_DIR, node.attrs[('', attr)] +
                                '.ttf').encode(config.LOCALE)
            if not os.path.isfile(font):
                font = os.path.join(config.FONT_DIR, node.attrs[('', attr)] +
                                    '.TTF').encode(config.LOCALE)
        if not font:
            print "can find font >%s<" % font
            font = config.OSD_DEFAULT_FONTNAME
        return font
    return default


def search_file(file, search_dirs):
    for s_dir in search_dirs:
        dfile=os.path.join(s_dir, file)

        if vfs.isfile(dfile):
            return vfs.abspath(dfile)
        
        if vfs.isfile("%s.png" % dfile):
            return vfs.abspath("%s.png" % dfile)
        
        if vfs.isfile("%s.jpg" % dfile):
            return vfs.abspath("%s.jpg" % dfile)

    _debug_('can\'t find image %s' % file)
    return ''



# ======================================================================

#
# data structures
#


# ======================================================================

class MainMenuItem:
    def __init__(self):
        self.label   = ''
        self.name    = ''
        self.icon    = ''
        self.image   = ''
        self.outicon = ''

    def parse(self, node, scale, c_dir=''):
        self.label    = attr_str(node, "label", self.label)
        self.name     = attr_str(node, "name",  self.name)
        self.icon     = attr_str(node, "icon",  self.icon)
        self.image    = attr_str(node, "image", self.image)
        self.outicon  = attr_str(node, "outicon",  self.outicon)

    def prepare(self, search_dirs, image_names):
        if self.image:
            self.image = search_file(self.image, search_dirs)
            

# ======================================================================

class MainMenu:
    def __init__(self):
        self.items = {}

    def parse(self, menu_node, scale, c_dir=''):
        for node in menu_node.children:
            if node.name == u'item':
                item = MainMenuItem()
                item.parse(node, scale, c_dir)
                self.items[item.label] = item                

    def prepare(self, search_dirs, image_names):
        for i in self.items:
            self.items[i].prepare(search_dirs, image_names)
    
# ======================================================================
# ======================================================================

XML_types = {
    'x'        : ('int',  1),
    'y'        : ('int',  2),
    'width'    : ('int',  1),
    'height'   : ('int',  2),
    'spacing'  : ('int',  3),
    'hours_per_page': ('int',  3),
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
    'image'    : ('str', 0),    
    'name'     : ('font',  0),
    'visible'  : ('visible', 0),
    'border'   : ('visible', 0),
    'icon'     : ('str', 0),    
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
            c = attr[1].encode(config.LOCALE)

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


    def prepare(self):
        """
        basic prepare function
        """
        try:
            if self.visible not in ('', 'yes'):
                if len(self.visible) > 4 and self.visible[:4] == 'not ':
                    p = plugin.getbyname(self.visible[4:])
                else:
                    p = plugin.getbyname(self.visible)
                try:
                    p = p.visible
                except:
                    pass
                if len(self.visible) > 4 and self.visible[:4] == 'not ':
                    self.visible = not p
                else:
                    self.visible = p
        except (TypeError, AttributeError):
            pass
            
    

# ======================================================================


class Menu:
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

        

class MenuSet:
    """
    the complete menu with the areas screen, title, subtitle, view, listing and info in it
    """
    def __init__(self):
        self.content = ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info' )
        for c in self.content:
            setattr(self, c, Area(c))


    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            for c in self.content:
                if subnode.name == c:
                    eval('self.%s.parse(subnode, scale, current_dir)' % c)


    def prepare(self, layout):
        for c in self.content:
            eval('self.%s.prepare(layout)' % c)



class Area(XML_data):
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
        self.visible = False

    def parse(self, node, scale, current_dir):
        if self.x == -1:
            self.visible = True

        x = self.x
        y = self.y
        XML_data.parse(self, node, scale, current_dir)
        if x != self.x:
            try:
                self.x += config.OSD_OVERSCAN_X
            except TypeError:
                pass
        if y != self.y:
            try:
                self.y += config.OSD_OVERSCAN_Y
            except TypeError:
                pass
        for subnode in node.children:
            if subnode.name == u'image' and self.name == 'listing':
                label = attr_str(subnode, 'label', '')
                if label:
                    if not label in self.images:
                        self.images[label] = Image()
                    x,y = self.images[label].x, self.images[label].y
                    self.images[label].parse(subnode, scale, current_dir)
                    if x != self.images[label].x:
                        try:
                            self.images[label].x += config.OSD_OVERSCAN_X
                        except TypeError:
                            pass
                    if y != self.images[label].y:
                        try:
                            self.images[label].y += config.OSD_OVERSCAN_Y
                        except TypeError:
                            pass

    def prepare(self, layout):
        XML_data.prepare(self)
        if self.visible:
            self.layout = layout[self.layout]
        else:
            self.layout = None
            
    def rect(self, type):
        if type == 'screen':
            return (self.x - config.OSD_OVERSCAN_X, self.y - config.OSD_OVERSCAN_X,
                    self.width + 2 * config.OSD_OVERSCAN_X,
                    self.height + 2 * config.OSD_OVERSCAN_X)
        return (self.x, self.y, self.width, self.height)

    def pos(self, type):
        if type == 'screen':
            return (self.x - config.OSD_OVERSCAN_X, self.y - config.OSD_OVERSCAN_X)
        return (self.x, self.y)


# ======================================================================

class Layout:
    """
    layout tag
    """
    def __init__(self, label):
        self.label = label
        self.background = ()
        self.content = Content()
        
    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            if subnode.name == u'background':
                self.background = []
                for bg in subnode.children:
                    if bg.name in ( 'image', 'rectangle' ):
                        b = eval(bg.name.capitalize()+'()')
                        b.parse(bg, scale, current_dir)
                        self.background += [ b ]
            if subnode.name == u'content':
                self.content.parse(subnode, scale, current_dir)

    def prepare(self, font, color, search_dirs, image_names):
        self.content.prepare(font, color, search_dirs)
        for b in self.background:
            b.prepare(color, search_dirs, image_names)
            


class Content(XML_data):
    """
    content inside a layout
    """
    def __init__(self):
        XML_data.__init__(self, ('type', 'spacing', 'x', 'y', 'width',
                                 'height', 'font', 'align', 'valign', 'color',
                                 'hours_per_page'))
        self.types = {}
        self.cdata = ''
        self.hours_per_page = 2
        
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        self.cdata = node.textof()
        for subnode in node.children:
            if subnode.name == u'item':
                type = attr_str(subnode, "type", '')
                if type and not self.types.has_key(type):
                    self.types[type] = XML_data(('font', 'align', 'valign', 'height',
                                                 'width', 'icon' ))
                    self.types[type].rectangle = None
                    self.types[type].cdata = ''
                if type:
                    self.types[type].parse(subnode, scale, current_dir)
                    self.types[type].cdata = subnode.textof()
                    delete_fcontent = True
                    for rnode in subnode.children:
                        if rnode.name == u'rectangle':
                            self.types[type].rectangle = Rectangle()
                            self.types[type].rectangle.parse(rnode, scale, current_dir)
                        elif rnode.name in ( u'if', u'text', u'newline',
                                             u'goto_pos', u'img' ):
                            if (not hasattr( self.types[ type ], 'fcontent' )) or \
                                   delete_fcontent:
                                self.types[ type ].fcontent = [ ]
                            delete_fcontent = False
                            child = None
                            if rnode.name == u'if':
                                child = FormatIf()
                            elif rnode.name == u'text':
                                child = FormatText()
                            elif rnode.name == u'newline':
                                child = FormatNewline()
                            elif rnode.name == u'goto_pos':
                                child = FormatGotopos()
                            elif rnode.name == u'img':
                                child = FormatImg()

                            self.types[ type ].fcontent += [ child ]
                            self.types[ type ].fcontent[-1].parse(rnode, scale, current_dir)

        if not self.types.has_key('default'):
            self.types['default'] = XML_data(('font',))
            self.types['default'].rectangle = None
            self.types['default'].cdata = ''
        

    def prepare(self, font, color, search_dirs):
        XML_data.prepare(self)
        if self.font:
            try:
                self.font = font[self.font]
            except:
                print 'can\'t find font %s' % self.font
                print font
                self.font = font['default']
        else:
            self.font = font['default']

        if color.has_key(self.color):
            self.color = color[self.color]

        for type in self.types:
            if self.types[type].font:
                self.types[type].font = font[self.types[type].font]
            else:
                self.types[type].font = None
            if self.types[type].rectangle:
                self.types[type].rectangle.prepare(color)

            if hasattr( self.types[type], 'fcontent' ):
                for i in self.types[type].fcontent:
                    i.prepare( font, color, search_dirs )



# ======================================================================
# Formating
class FormatText(XML_data):
    def __init__( self ):
        XML_data.__init__( self, ( 'align', 'valign', 'font', 'width', 'height' ) )
        self.mode   = 'hard'
        self.align  = 'left'
        self.height = -1
        self.text = ''
        self.expression = None
        self.expression_analized = 0
        self.x = 0
        self.y = 0
        
    def __str__( self ):
        str = "FormatText( Text: '%s', Expression: '%s', "+\
              "Expression Analized: %s, Mode: %s, Font: %s, Width: %s, "+\
              "Height: %s, x: %s, y: %s ) "
        str = str % ( self.text, self.expression, self.expression_analized,
                      self.mode, self.font, self.width, self.height, self.x, self.y )
        return str


    def parse( self, node, scale, c_dir = '' ):
        XML_data.parse( self, node, scale, c_dir )
        self.text = node.textof()
        self.mode = attr_str( node, 'mode', self.mode )
        if self.mode != 'hard' and self.mode != 'soft':
            self.mode = 'hard'
        self.expression = attr_str( node, 'expression', self.expression )
        if self.expression: self.expression = self.expression.strip()


    def prepare(self, font, color, search_dirs):
        if self.font:
            try:
                self.font = font[self.font]
            except:
                print 'can\'t find font %s' % self.font
                self.font = font['default']
        else:
            self.font = font['default']

    

        
class FormatGotopos(XML_data):
    def __init__( self ):
        XML_data.__init__( self, ( 'x', 'y' ) )
        self.mode = 'relative'
        self.x = None
        self.y = None
        
    def parse( self, node, scale, c_dir = '' ):
        XML_data.parse( self, node, scale, c_dir )
        self.mode = attr_str( node, 'mode', self.mode )
        if self.mode != 'relative' and self.mode != 'absolute':
            self.mode = 'relative'
        
    def prepare(self, font, color, search_dirs):
        pass

    
class FormatNewline:
    def __init__( self ):
        pass

    def parse( self, node, scale, c_dir = '' ):
        pass

    def prepare(self, font, color, search_dirs):
        pass

class FormatImg( XML_data ):
    def __init__( self ):
        XML_data.__init__( self, ( 'x', 'y', 'width', 'height' ) )
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.src = ''
        
    def parse( self, node, scale, c_dir = '' ):
        XML_data.parse( self, node, scale, c_dir )
        self.src = attr_str( node, 'src', self.src )
        
    def prepare(self, font, color, search_dirs ):
        self.src = search_file( self.src, search_dirs )
        


class FormatIf:
    def __init__( self ):
        self.expression = ''
        self.content = [ ]
        self.expression_analized = 0
        
    def parse( self, node, scale, c_dir = '' ):
        self.expression = attr_str( node, 'expression', self.expression )
        for subnode in node.children:
            if subnode.name == u'if':
                child = FormatIf()
            elif subnode.name == u'text':
                child = FormatText()
            elif subnode.name == u'newline':
                child = FormatNewline()
            elif subnode.name == u'goto_pos':
                child = FormatGotopos()
            elif subnode.name == u'img':
                child = FormatImg()
            
            child.parse( subnode, scale, c_dir )
            self.content += [ child ]

    def prepare(self, font, color, search_dirs):
        for i in self.content:
            i.prepare( font, color, search_dirs )

                              




# ======================================================================

class Image(XML_data):
    """
    an image
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'image', 'filename',
                                 'label', 'visible'))

    def prepare(self, color, search_dirs, image_names):
        """
        try to guess the image localtion
        """
        XML_data.prepare(self)
        if self.image:
            try:
                self.filename = image_names[self.image]
            except KeyError:
                print 'can\'t find image definition %s' % self.image
                pass

        if self.filename:
            self.filename = search_file(self.filename, search_dirs)



class Rectangle(XML_data):
    """
    a Rectangle
    """
    def __init__(self, color=None, bgcolor=None, size=None, radius = None):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'color',
                                 'bgcolor', 'size', 'radius' ))
        if not color == None:
            self.color = color
        if not bgcolor == None:
            self.bgcolor = bgcolor
        if not size == None:
            self.size = size
        if not radius == None:
            self.radius = radius

    def prepare(self, color, search_dirs=None, image_names=None):
        XML_data.prepare(self)
        if color.has_key(self.color):
            self.color = color[self.color]
        if color.has_key(self.bgcolor):
            self.bgcolor = color[self.bgcolor]



class Font(XML_data):
    """
    font tag
    """
    def __init__(self, label):
        XML_data.__init__(self, ('name', 'size', 'color', 'bgcolor'))
        self.label  = label
        self.shadow = XML_data(('visible', 'color', 'x', 'y', 'border'))
        self.shadow.visible = False
        self.shadow.border  = False
        
    def parse(self, node, scale, current_dir):
        XML_data.parse(self, node, scale, current_dir)
        for subnode in node.children:
            if subnode.name == u'shadow':
                self.shadow.parse(subnode, scale, current_dir)

    def stringsize(self, text):
        size = self.font.stringsize(text)
        if self.shadow.visible:
            if self.shadow.border:
                return size + (self.size / 10) * 2
            else:
                return size + abs(self.shadow.x)
        return size
    
    def prepare(self, color, search_dirs=None, image_names=None, scale=1.0):
        if color.has_key(self.color):
            self.color = color[self.color]
        self.size   = int(float(self.size) * scale)
        self.font   = osd.getfont(self.name, self.size)
        self.h      = self.font.height
        if self.shadow.visible:
            if color.has_key(self.shadow.color):
                self.shadow.color = color[self.shadow.color]
            self.h += self.shadow.y
        self.height = self.h
        

    
# ======================================================================


class AreaSet:
    """
    A tag with different area pointer in it, e.g. used for <player>
    """
    def __init__(self):
        self.areas = {}

    def parse(self, node, scale, current_dir):
        for subnode in node.children:
            if not self.areas.has_key(subnode.name):
                self.areas[subnode.name] = Area(subnode.name)
                self.areas[subnode.name].visible = True
            self.areas[subnode.name].parse(subnode, scale, current_dir)

    def prepare(self, layout):
        for c in self.areas:
            self.areas[c].prepare(layout)

    
# ======================================================================


class XMLSkin:
    """
    skin main settings class
    """
    def __init__(self):

        self._layout   = {}
        self._font     = {}
        self._color    = {}
        self._images   = {}
        self._menuset  = {}
        self._menu     = {}
        self._popup    = ''
        self._sets     = {}
        self._mainmenu = MainMenu()
        self.skindirs  = []
        self.icon_dir  = ""

        self.fxd_files        = []

        # variables set by set_var
        self.all_variables    = ('box_under_icon', )
        self.box_under_icon   = 0

        
    def parse(self, freevo_type, scale, c_dir, copy_content):
        for node in freevo_type.children:
            if node.name == u'main':
                self._mainmenu.parse(node, scale, c_dir)

            elif node.name == u'menu':
                type = attr_str(node, 'type', 'default')

                if type == 'all':
                    # if type is all, all types except default are deleted and
                    # the settings will be loaded for default
                    self._menu = {}
                    type       = 'default'
                    
                self._menu[type] = Menu()
                self._menu[type].parse(node, scale, c_dir)


            elif node.name == u'menuset':
                label   = attr_str(node, 'label', '')
                inherit = attr_str(node, 'inherits', '')
                if inherit:
                    self._menuset[label] = copy.deepcopy(self._menuset[inherit])
                elif not self._menuset.has_key(label):
                    self._menuset[label] = MenuSet()
                self._menuset[label].parse(node, scale, c_dir)


            elif node.name == u'layout':
                label = attr_str(node, 'label', '')
                if label:
                    if not self._layout.has_key(label):
                        self._layout[label] = Layout(label)
                    self._layout[label].parse(node, scale, c_dir)
                        

            elif node.name == u'font':
                label = attr_str(node, 'label', '')
                if label:
                    if not self._font.has_key(label):
                        self._font[label] = Font(label)
                    self._font[label].parse(node, scale, c_dir)

            elif node.name == u'color':
                label = attr_str(node, 'label', '')
                if label:
                    value = attr_col(node, 'value', '')
                    self._color[label] = value
                        
            elif node.name == u'image':
                label = attr_str(node, 'label', '')
                if label:
                    value = attr_col(node, 'filename', '')
                    self._images[label] = value
                        
            elif node.name == u'iconset':
                self.icon_dir = attr_str(node, 'theme', self.icon_dir)

            elif node.name == u'popup':
                self._popup = attr_str(node, 'layout', self._popup)

            elif node.name == u'setvar':
                for v in self.all_variables:
                    if node.attrs[('', 'name')].upper() == v.upper():
                        try:
                            setattr(self, v, int(node.attrs[('', 'val')]))
                        except ValueError:
                            setattr(self, v, node.attrs[('', 'val')])

            else:
                if node.children and node.children[0].name == 'style':
                    self._sets[node.name] = Menu()
                elif not self._sets.has_key(node.name):
                    self._sets[node.name] = AreaSet()
                self._sets[node.name].parse(node, scale, c_dir)


    def prepare(self):
        self.prepared = True
        self.menu     = copy.deepcopy(self._menu)
        self.sets     = copy.deepcopy(self._sets)
        
        self.font     = copy.deepcopy(self._font)
        layout        = copy.deepcopy(self._layout)

        if not os.path.isdir(self.icon_dir):
            self.icon_dir = os.path.join(config.ICON_DIR, 'themes', self.icon_dir)
        search_dirs = self.skindirs + [ config.IMAGE_DIR, self.icon_dir, '.' ]
        
        for f in self.font:
            self.font[f].prepare(self._color, scale=self.font_scale)
            
        for l in layout:
            layout[l].prepare(self.font, self._color, search_dirs, self._images)

        for menu in self.menu:
            self.menu[menu].prepare(self._menuset, layout)

            # prepare listing area images
            for s in self.menu[menu].style:
                for i in range(2):
                    if s[i] and hasattr(s[i], 'listing'):
                        for image in s[i].listing.images:
                            s[i].listing.images[image].prepare(None, search_dirs,
                                                               self._images)
                        
                
        for s in self.sets:
            if isinstance(self.sets[s], AreaSet):
                # prepare an areaset
                self.sets[s].prepare(layout)
            else:
                # prepare a menu
                self.sets[s].prepare(self._menuset, layout)
                for s in self.sets[s].style:
                    for i in range(2):
                        if s[i] and hasattr(s[i], 'listing'):
                            for image in s[i].listing.images:
                                s[i].listing.images[image].prepare(None, search_dirs,
                                                                   self._images)

        self.popup = layout[self._popup]
        
        self.mainmenu = copy.deepcopy(self._mainmenu)
        self.mainmenu.prepare(search_dirs, self._images)

        self.images = {}
        for name in self._images:
            self.images[name] = search_file(self._images[name], search_dirs)
        return 1


    def fxd_callback(self, fxd, node):
        """
        callback for the 'skin' tag
        """
        # get args back
        (clear, copy_content, file, prepare) = fxd.getattr(None, 'args')

        font_scale    = attr_float(node, "fontscale", 1.0)
        file_geometry = attr_str(node, "geometry", '')
        
        if file_geometry:
            w, h = file_geometry.split('x')
        else:
            w = config.CONF.width
            h = config.CONF.height

        scale = (float(config.CONF.width-2*config.OSD_OVERSCAN_X)/float(w),
                 float(config.CONF.height-2*config.OSD_OVERSCAN_Y)/float(h))

        include  = attr_str(node, 'include', '')

        if include:
            if clear:
                self._layout   = {}
                self._font     = {}
                self._color    = {}
                self._images   = {}
                self._menuset  = {}
                self._menu     = {}
                self._popup    = ''
                self._sets     = {}
                self._mainmenu = MainMenu()
                self.skindirs  = []
                self.fxd_files = []
            self.load(include, copy_content, prepare=False)

        self.parse(node, scale, os.path.dirname(file), copy_content)
        if not os.path.dirname(file) in self.skindirs:
            self.skindirs = [ os.path.dirname(file) ] + self.skindirs
        if not prepare:
            return
            
        self.font_scale = font_scale
        self.prepare()
        self.prepared = False
        return

        
    def load(self, file, copy_content=0, prepare=True, clear=False):
        """
        load and parse the skin file
        """
        self.prepared     = False
        
        if not vfs.isfile(file):
            if vfs.isfile(file+".fxd"):
                file += ".fxd"

            elif vfs.isfile(vfs.join(config.SKIN_DIR, '%s/%s.fxd' % (file, file))):
                file = vfs.join(config.SKIN_DIR, '%s/%s.fxd' % (file, file))

            else:
                file = vfs.join(config.SKIN_DIR, 'main/%s' % file)
                if vfs.isfile(file+".fxd"):
                    file += ".fxd"

        if not vfs.isfile(file):
            return 0

        try:
            parser = util.fxdparser.FXD(file)
            parser.setattr(None, 'args', (clear, copy_content, file, prepare))
            parser.set_handler('skin', self.fxd_callback)
            parser.parse()
            self.fxd_files.append(file)
            return 1
        
        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

