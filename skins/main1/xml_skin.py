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
# Revision 1.8  2003/07/03 22:05:37  dischi
# set line_height to -1
#
# Revision 1.7  2003/06/29 20:38:58  dischi
# switch to the new info area
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
            if val == 'line_height':
                return -1
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

    def prepaire(self, search_dirs, image_names):
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

    def prepare(self, search_dirs, image_names):
        for i in self.items:
            self.items[i].prepaire(search_dirs, image_names)
    
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
    'image'    : ('str', 0),
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

    def prepare(self, font, color, search_dirs, image_names):
        self.content.prepare(font, color)
        for b in self.background:
            b.prepare(color, search_dirs, image_names)
            
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
                                                 'width', 'image'))
                    self.types[type].rectangle = None
                    self.types[type].cdata = ''
                if type:
                    self.types[type].parse(subnode, scale, current_dir)
                    self.types[type].cdata = subnode.textof()
                    for rnode in subnode.children:
                        if rnode.name == u'rectangle':
                            self.types[type].rectangle = XML_rectangle()
                            self.types[type].rectangle.parse(rnode, scale, current_dir)
                        elif rnode.name in ( u'if', u'text', u'newline', u'goto_pos' ):
                            if not hasattr( self.types[ type ], 'fcontent' ):
                                self.types[ type ].fcontent = [ ]
                            child = None
                            if rnode.name == u'if':
                                child = XML_FormatIf()
                            elif rnode.name == u'text':
                                child = XML_FormatText()
                            elif rnode.name == u'newline':
                                child = XML_FormatNewline()
                            elif rnode.name == u'goto_pos':
                                child = XML_FormatGotopos()

                            self.types[ type ].fcontent += [ child ]
                            self.types[ type ].fcontent[ -1 ].parse( rnode, scale, current_dir )
                            
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
                    i.prepare( font, color )



# ======================================================================
# Formating
class XML_FormatText(XML_data):
    def __init__( self ):
        XML_data.__init__( self, ( 'align', 'valign', 'font', 'width', 'height' ) )
        self.mode = 'hard'
        self.text = ''
        self.expression = None
        self.expression_analized = 0
        self.x = 0
        self.y = 0
        
    def __str__( self ):
        str = "XML_FormatText( Text: '%s', Expression: '%s', Expression Analized: %s, Mode: %s, Font: %s, Width: %s, Height: %s, x: %s, y: %s ) " % ( self.text, self.expression, self.expression_analized, self.mode, self.font, self.width, self.height, self.x, self.y )
        return str

    def parse( self, node, scale, c_dir = '' ):
        XML_data.parse( self, node, scale, c_dir )
        self.text = node.textof()
        self.mode = attr_str( node, 'mode', self.mode )
        if self.mode != 'hard' and self.mode != 'soft':
            self.mode = 'hard'
        self.expression = attr_str( node, 'expression', self.expression )
        if self.expression: self.expression = self.expression.strip()

    def prepare(self, font, color):
        if self.font:
            try:
                self.font = font[self.font]
            except:
                print 'can\'t find font %s' % self.font
                print font
                self.font = font['default']
        else:
            self.font = font['default']

    

        
class XML_FormatGotopos(XML_data):
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
        
    def prepare(self, font, color):
        pass
    
class XML_FormatNewline:
    def __init__( self ):
        pass

    def parse( self, node, scale, c_dir = '' ):
        pass

    def prepare(self, font, color):
        pass


class XML_FormatIf:
    def __init__( self ):
        self.expression = ''
        self.content = [ ]
        self.expression_analized = 0
        
    def parse( self, node, scale, c_dir = '' ):
        self.expression = attr_str( node, 'expression', self.expression )
        for subnode in node.children:
            if subnode.name == u'if':
                child = XML_FormatIf()
            elif subnode.name == u'text':
                child = XML_FormatText()
            elif subnode.name == u'newline':
                child = XML_FormatNewline()
            elif subnode.name == u'goto_pos':
                child = XML_FormatGotopos()
            
            child.parse( subnode, scale, c_dir )
            self.content += [ child ]

    def prepare(self, font, color):
        for i in self.content:
            i.prepare( font, color )

                              




# ======================================================================

class XML_image(XML_data):
    """
    an image
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'image', 'filename', 'label'))

    def prepare(self, color, search_dirs, image_names):
        """
        try to guess the image localtion
        """
        if self.image:
            try:
                self.filename = image_names[self.image]
            except KeyError:
                print 'can\'t find image definition %s' % self.image
                pass

        if self.filename:
            self.filename = search_file(self.filename, search_dirs)



class XML_rectangle(XML_data):
    """
    a rectangle
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'color',
                                 'bgcolor', 'size', 'radius' ))

    def prepare(self, color, search_dirs=None, image_names=None):
        if color.has_key(self.color):
            self.color = color[self.color]
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

    def prepare(self, color, search_dirs=None, image_names=None, scale=1.0):
        if color.has_key(self.color):
            self.color = color[self.color]
        self.size = int(float(self.size) * scale)
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
        self._images = {}
        self._menuset = {}
        self._menu = {}
        self._popup = ''
        self._player = XML_player()
        self._tv = XML_tv()
        self._mainmenu = XML_mainmenu()
        self.skin_directories = []
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
                        
            if node.name == u'image':
                label = attr_str(node, 'label', '')
                if label:
                    value = attr_col(node, 'filename', '')
                    self._images[label] = value
                        
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

        font_scale = 1.0
        
        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            for freevo_type in box.children:
                if freevo_type.name == 'skin':

                    font_scale = attr_float(freevo_type, "fontscale", 1.0)

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
                            self._images = {}
                            self._menuset = {}
                            self._menu = {}
                            self._popup = ''
                            self._player = XML_player()
                            self._tv = XML_tv()
                            self._mainmenu = XML_mainmenu()
                            self.skin_directories = []
                            
                        self.load(include, copy_content, prepare = FALSE)

                    self.parse(freevo_type, scale, os.path.dirname(file), copy_content)
                    if not os.path.dirname(file) in self.skin_directories:
                        self.skin_directories = [ os.path.dirname(file) ] + \
                                                self.skin_directories
                    
            if not prepare:
                return 1
        
            self.menu   = copy.deepcopy(self._menu)
            self.tv     = copy.deepcopy(self._tv)
            self.player = copy.deepcopy(self._player)

            font        = copy.deepcopy(self._font)
            layout      = copy.deepcopy(self._layout)

            search_dirs = self.skin_directories + [ 'skins/images', self.icon_dir, '.' ]

            for f in font:
                font[f].prepare(self._color, scale=font_scale)
                
            for l in layout:
                layout[l].prepare(font, self._color, search_dirs, self._images)
            for menu in self.menu:
                self.menu[menu].prepare(self._menuset, layout)

                # prepare listing area images
                for s in self.menu[menu].style:
                    for i in range(2):
                        if s[i] and hasattr(s[i], 'listing'):
                            for image in s[i].listing.images:
                                s[i].listing.images[image].prepare(None, search_dirs,
                                                                   self._images)
                        
                
            self.player.prepare(layout)
            self.tv.prepare(layout)
            # prepare listing area images
            for image in self.tv.listing.images:
                self.tv.listing.images[image].prepare(None, search_dirs, self._images)

            self.popup = layout[self._popup]

            self.mainmenu = copy.deepcopy(self._mainmenu)
            self.mainmenu.prepare(search_dirs, self._images)
            return 1

        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

