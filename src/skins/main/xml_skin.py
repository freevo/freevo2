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
# Revision 1.14  2003/10/03 16:46:13  dischi
# moved the encoding type (latin-1) to the config file config.LOCALE
#
# Revision 1.13  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.12  2003/09/07 15:43:06  dischi
# tv guide can now also have different styles
#
# Revision 1.11  2003/09/05 18:16:43  dischi
# parse all named images into self.images
#
# Revision 1.10  2003/09/02 19:13:05  dischi
# move box_under_icon as variable into the skin fxd file
#
# Revision 1.9  2003/08/25 18:44:32  dischi
# Moved HOURS_PER_PAGE into the skin fxd file, default=2
#
# Revision 1.8  2003/08/24 19:12:31  gsbarbieri
# Added:
#   * support for different icons in main menu (final part)
#   * BOX_UNDER_ICON, that is, in text listings, if you have an icon you may
#     set this to 1 so the selection box (<item type="* selected"><rectangle>)
#     will be under the icon too. Not changed freevo_config.py version
#     because I still don't know if it should stay there.
#
# Revision 1.7  2003/08/24 16:36:25  dischi
# add support for y=max-... in listing area arrows
#
# Revision 1.6  2003/08/24 11:01:59  dischi
# use round not int after scaling
#
# Revision 1.5  2003/08/24 10:04:05  dischi
# added font_h as variable for y and height settings
#
# Revision 1.4  2003/08/24 06:58:18  gsbarbieri
# Partial support for "out" icons in main menu.
# The missing part is in listing_area, which have other changes to
# allow box_under_icon feature (I mailed the list asking for opinions on
# that)
#
# Revision 1.3  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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
import util

import osd
import plugin

# XML support
from xml.utils import qp_xml

osd = osd.get_singleton()

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
    return TRUE or FALSE based in the attribute values 'yes' or 'no'
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

    _debug_('can\'t find image %s' % file)
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
        self.outicon = ''

    def parse(self, node, scale, c_dir=''):
        self.label = attr_str(node, "label", self.label)
        self.name  = attr_str(node, "name",  self.name)
        self.icon  = attr_str(node, "icon",  self.icon)
        self.image = attr_str(node, "image", self.image)
        self.outicon  = attr_str(node, "outicon",  self.outicon)

    def prepare(self, search_dirs, image_names):
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
            try:
                self.x += config.OVERSCAN_X
            except TypeError:
                pass
        if y != self.y:
            try:
                self.y += config.OVERSCAN_Y
            except TypeError:
                pass
        for subnode in node.children:
            if subnode.name == u'image' and self.name == 'listing':
                label = attr_str(subnode, 'label', '')
                if label:
                    if not label in self.images:
                        self.images[label] = XML_image()
                    x,y = self.images[label].x, self.images[label].y
                    self.images[label].parse(subnode, scale, current_dir)
                    if x != self.images[label].x:
                        try:
                            self.images[label].x += config.OVERSCAN_X
                        except TypeError:
                            pass
                    if y != self.images[label].y:
                        try:
                            self.images[label].y += config.OVERSCAN_Y
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
        self.content.prepare(font, color, search_dirs)
        for b in self.background:
            b.prepare(color, search_dirs, image_names)
            


class XML_content(XML_data):
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
                    delete_fcontent = TRUE
                    for rnode in subnode.children:
                        if rnode.name == u'rectangle':
                            self.types[type].rectangle = XML_rectangle()
                            self.types[type].rectangle.parse(rnode, scale, current_dir)
                        elif rnode.name in ( u'if', u'text', u'newline', u'goto_pos', u'img' ):
                            if (not hasattr( self.types[ type ], 'fcontent' )) or \
                                   delete_fcontent:
                                self.types[ type ].fcontent = [ ]
                            delete_fcontent = FALSE
                            child = None
                            if rnode.name == u'if':
                                child = XML_FormatIf()
                            elif rnode.name == u'text':
                                child = XML_FormatText()
                            elif rnode.name == u'newline':
                                child = XML_FormatNewline()
                            elif rnode.name == u'goto_pos':
                                child = XML_FormatGotopos()
                            elif rnode.name == u'img':
                                child = XML_FormatImg()

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
class XML_FormatText(XML_data):
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

    def prepare(self, font, color, search_dirs):
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
        
    def prepare(self, font, color, search_dirs):
        pass
    
class XML_FormatNewline:
    def __init__( self ):
        pass

    def parse( self, node, scale, c_dir = '' ):
        pass

    def prepare(self, font, color, search_dirs):
        pass

class XML_FormatImg( XML_data ):
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
            elif subnode.name == u'img':
                child = XML_FormatImg()
            
            child.parse( subnode, scale, c_dir )
            self.content += [ child ]

    def prepare(self, font, color, search_dirs):
        for i in self.content:
            i.prepare( font, color, search_dirs )

                              




# ======================================================================

class XML_image(XML_data):
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



class XML_rectangle(XML_data):
    """
    a rectangle
    """
    def __init__(self):
        XML_data.__init__(self, ('x', 'y', 'width', 'height', 'color',
                                 'bgcolor', 'size', 'radius' ))

    def prepare(self, color, search_dirs=None, image_names=None):
        XML_data.prepare(self)
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
        self.font = osd.getfont(self.name, self.size)
        self.h = self.font.height
        if self.shadow.visible:
            if color.has_key(self.shadow.color):
                self.shadow.color = color[self.shadow.color]
            self.h += self.shadow.y
        

    
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


class XML_tv(XML_menu):
    """
    tv tag for the tv menu
    """
    pass


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

        # variables set by set_var
        self.all_variables  = ('box_under_icon', )
        self.box_under_icon = 0
        
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
                self.icon_dir = attr_str(node, 'theme', self.icon_dir)

            if node.name == u'popup':
                self._popup = attr_str(node, 'layout', self._popup)

            if node.name == u'player':
                self._player.parse(node, scale, c_dir)

            if node.name == u'tv':
                self._tv = XML_tv()
                self._tv.parse(node, scale, c_dir)

            if node.name == u'setvar':
                for v in self.all_variables:
                    if node.attrs[('', 'name')].upper() == v.upper():
                        try:
                            setattr(self, v, int(node.attrs[('', 'val')]))
                        except ValueError:
                            setattr(self, v, node.attrs[('', 'val')])
                
    def prepare(self):
        self.prepared = TRUE
        self.menu   = copy.deepcopy(self._menu)
        self.tv     = copy.deepcopy(self._tv)
        self.player = copy.deepcopy(self._player)
        
        self.font   = copy.deepcopy(self._font)
        layout      = copy.deepcopy(self._layout)

        if not os.path.isdir(self.icon_dir):
            self.icon_dir = os.path.join(config.ICON_DIR, 'themes', self.icon_dir)
        search_dirs = self.skin_directories + [ config.IMAGE_DIR, self.icon_dir, '.' ]
        
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
                        
                
        self.player.prepare(layout)
        self.tv.prepare(self._menuset, layout)
        # prepare listing area images
        for s in self.tv.style:
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

        
    def load(self, file, copy_content = 0, prepare = TRUE, clear=FALSE):
        """
        load and parse the skin file
        """

        self.prepared = FALSE
        if not os.path.isfile(file):
            if os.path.isfile(file+".fxd"):
                file += ".fxd"
            elif os.path.isfile(os.path.join(config.SKIN_DIR, '%s/%s.fxd' % (file, file))):
                file = os.path.join(config.SKIN_DIR, '%s/%s.fxd' % (file, file))
            else:
                file = os.path.join(config.SKIN_DIR, 'main/%s' % file)
                if os.path.isfile(file+".fxd"):
                    file += ".fxd"

        if not os.path.isfile(file):
            return 0

        font_scale = 1.0

        try:
            parser = qp_xml.Parser()
            f = open(file)
            box = parser.parse(f.read())
            f.close()
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
                    break
            else:
                # no new skin settings loaded, return without action
                return 1
            
            if not prepare:
                return 1
            self.font_scale = font_scale
            self.prepare()
            self.prepared = FALSE
            return 1
        

        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
            return 0

