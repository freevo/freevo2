#if 0
# -----------------------------------------------------------------------
# skin_main1.py - Freevo default skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2003/12/03 21:50:44  dischi
# rework of the loading/selecting
# o all objects that need a skin need to register what they areas they need
# o remove all 'player' and 'tv' stuff to make it more generic
# o renamed some skin function names
#
# Revision 1.21  2003/11/29 11:27:41  dischi
# move objectcache to util
#
# Revision 1.20  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.19  2003/11/22 20:34:23  dischi
# use new vfs
#
# Revision 1.18  2003/11/22 12:02:11  dischi
# make the skin blankscreen a real plugin area
#
# Revision 1.17  2003/10/31 17:00:20  dischi
# splashscreen for bsd
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


import sys, os, copy
import stat
import pygame

import config
import util
import osd
import plugin

from area import Skin_Area, Screen
from gui  import GUIObject

# XML parser for skin informations
sys.path.append('skins/main1')

import xml_skin

# Create the OSD object
osd = osd.get_singleton()


class Screen_Area(Skin_Area):
    """
    this area is the screen or background of the skin
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'screen', screen)

    def update_content_needed(self):
        """
        this area needs never a content update
        """
        return FALSE

    def update_content(self):
        """
        there is no content in this area
        """
        pass



class Title_Area(Skin_Area):
    """
    in this area the title of the menu is drawn
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'title', screen)
        self.text = ''

        
    def update_content_needed(self):
        """
        check if the content needs an update. This function does the same as
        update_content, so it's faster to return always 1
        """
        return 1

    def update_content(self):
        """
        update the content
        """
        menu      = self.menu
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=True)

        text = ''
        try:
            if content.type == 'menu':
                text = menu.heading
            elif len(menu.choices) == 0:
                text = ''
            elif content.type == 'short item':
                if menu.selected.image and menu.selected.type == 'video' and \
                   hasattr(menu.selected, 'tv_show') and menu.selected.tv_show:
                    sn = menu.selected.show_name
                    text = sn[1] + "x" + sn[2] + " - " + sn[3] 
                else:
                    text = menu.selected.name
            else:
                text = menu.selected.name
        except AttributeError:
            try:
                if menu.type == 'tv':
                    if content.type == 'item' or content.type == 'short item':
                        text = menu.table[1].title
                    else:
                        text = _('TV GUIDE')
            except:
                pass
            
        self.text = text
        self.write_text(text, content.font, content, height=-1, mode='hard')


class Subtitle_Area(Title_Area):
    """
    in this area the subtitle of the menu is drawn
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'subtitle', screen)
        self.text = ''


class Plugin_Area(Skin_Area):
    """
    in this area all plugins can draw
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'plugin', screen)
        self.plugins = None
        self.x = config.OSD_OVERSCAN_X
        self.y = config.OSD_OVERSCAN_Y
        self.width   = osd.width  - 2 * config.OSD_OVERSCAN_X
        self.height  = osd.height - 2 * config.OSD_OVERSCAN_Y
        
    def get_font(self, name):
        try:
            return self.xml_settings.font[name]
        except:
            return self.xml_settings.font['default']
    
    def update_content_needed(self):
        """
        this area needs never a content update
        """
        return True

    def update_content(self):
        """
        there is no content in this area
        """
        if self.plugins == None:
            self.plugins = plugin.get('daemon_draw')

        for p in self.plugins:
            p.draw((self.widget_type, self.menuw), self)



###############################################################################

skin_engine = None

class BlankScreen(Skin_Area):
    """
    An area only with the background. This can be used by plugins to
    draw some objects with the osd to the screen with bypassing every
    skin setting except the background.
    """
    class Rectange(xml_skin.XML_rectangle):
        def __init__(self, color=None, bgcolor=None, size=None, radius = None):
            xml_skin.XML_rectangle.__init__(self)
            if not color == None:
                self.color = color
            if not bgcolor == None:
                self.bgcolor = bgcolor
            if not size == None:
                self.size = size
            if not radius == None:
                self.radius = radius
    
    def __init__(self):
        """
        init the screen
        """
        global skin_engine
        Skin_Area.__init__(self, name='blank', screen=skin_engine.screen)
        if not skin_engine.settings.prepared:
            skin_engine.settings.prepare()
            
        if skin_engine.settings.images.has_key('background'):
            image = osd.loadbitmap(skin_engine.settings.images['background'])
            image = pygame.transform.scale(image, (osd.width, osd.height))

        self.allow_plugins = False
        self.bg = xml_skin.XML_image()
        self.bg.x = 0
        self.bg.y = 0
        self.bg.width  = osd.width
        self.bg.height = osd.height
        self.bg.label  = 'background'
        self.bg.image  = image

        self.area_val    = None
        self.area_name   = 'blank'
        self.skin_engine = skin_engine
        
        # be aware of the idlebar
        if plugin.getbyname('idlebar'):
            self.has_idlebar = True
        else:
            self.has_idlebar = False


            
    def draw(self, x0, y0, x1, y1):
        """
        there is no content in this area
        """

    def init_vars(self, settings, display_type, widget_type):
        self.area_val = xml_skin.XML_area(self.area_name)
        self.area_val.visible = True
        self.area_val.r = (0, 0, osd.width, osd.height)
        self.layout = 1
        return 1


    def update_content(self):
        y0 = config.OSD_OVERSCAN_Y
        if self.allow_plugins and self.has_idlebar:
            y0 += 70
        self.draw(config.OSD_OVERSCAN_X, y0, osd.width - config.OSD_OVERSCAN_X,
                  osd.height - config.OSD_OVERSCAN_Y)

            
    def draw_background(self):
        self.draw_image(self.bg.image, self.bg)
        

    def refresh(self):
        """
        Refresh the screen. The background will be drawn and saved as
        self.bg. The class inheriting from this may override self.bg
        later to add something to it.
        """
        self.skin_engine.draw(('', self))

        

class Splashscreen(BlankScreen):
    """
    A simple splash screen for osd startup
    """
    def __init__(self):
        BlankScreen.__init__(self)
        self.initialized = FALSE
        self.pos = 0

        self.bar_border   = self.Rectange(bgcolor=0xff000000, size=2)
        self.bar_position = self.Rectange(bgcolor=0xa0000000L)


    def draw(self, x0, y0, x1, y1):
        """
        draw the current position
        """
        x0 += 20
        x1 -= 20

        if not self.initialized:
            if os.uname()[0] == 'FreeBSD':
                logo = os.path.join(config.IMAGE_DIR, 'splashscreen-bsd.png')
            else:
                logo = os.path.join(config.IMAGE_DIR, 'splashscreen.png')
                
            image = osd.loadbitmap(logo)
            if image:
                image = pygame.transform.scale(image, (x1-x0, y1-y0))
                osd.drawbitmap(image, x0, y0, layer=self.bg.image)

            osd.drawstringframed(_('Starting Freevo, please wait ...'),
                                 x0, y1-180, x1-x0, 40,
                                 osd.getfont(config.OSD_DEFAULT_FONTNAME, 20),
                                 fgcolor=0xffffff, align_h='center',
                                 align_v='bottom', layer=self.bg.image)
            self.initialized = True

        pos = 0
        if self.pos:
            pos = round(float((x1 - x0 - 4)) / (float(100) / self.pos))
        self.drawroundbox(x0, y1-130, x1-x0, 20, self.bar_border)
        self.drawroundbox(x0+2, y1-128, pos, 16, self.bar_position)


    def progress(self, pos):
        """
        set the progress position and refresh the screen
        """
        self.pos = pos
        self.refresh()


###############################################################################
# Skin main functions
###############################################################################

class Skin:
    """
    main skin class
    """
    
    class BlankScreen(BlankScreen):
        pass

    class Splashscreen(Splashscreen):
        pass
    
    def __init__(self):
        """
        init the skin engine
        """
        global skin_engine
        skin_engine = self
        
        self.display_style = { 'menu' : config.SKIN_START_LAYOUT }
        self.force_redraw  = True
        self.last_draw     = None, None
        self.screen        = Screen()
        self.xml_cache     = util.objectcache.ObjectCache(3, desc='xmlskin')
        self.areas         = {}
        self.freevo_active = False

        # load default areas
        from listing_area   import Listing_Area
        from tvlisting_area import TVListing_Area
        from view_area      import View_Area
        from info_area      import Info_Area
        for a in ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info'):
            self.areas[a] = eval('%s%s_Area(self, self.screen)' % \
                                 (a[0].upper(), a[1:]))
        self.areas['tvlisting'] = TVListing_Area(self, self.screen)
        self.plugin_area = Plugin_Area(self, self.screen)


        # load the fxd file
        self.settings = xml_skin.XMLSkin()
        
        # try to find the skin xml file
        if not self.settings.load(config.SKIN_XML_FILE):
            print "skin not found, using fallback skin"
            self.settings.load('blue.fxd')
        
        for dir in config.cfgfilepath:
            local_skin = '%s/local_skin.fxd' % dir
            if os.path.isfile(local_skin):
                _debug_('Skin: Add local config %s to skin' % local_skin,2)
                self.settings.load(local_skin)
                break


    def register(self, type, areas):
        """
        register a new type objects to the skin
        """
        setattr(self, '%s_areas' % type, [])
        for a in areas:
            getattr(self, '%s_areas' % type).append(self.areas[a])
        getattr(self, '%s_areas' % type).append(self.plugin_area)
        
            
    def load(self, dir, copy_content = 1):
        """
        return an object with new skin settings
        """
        if dir and vfs.isfile(vfs.join(dir, 'folder.fxd')):
            file = vfs.join(dir, 'folder.fxd')

        elif dir and vfs.isfile(dir):
            file = dir
        else:
            return None

        if copy_content:
            cname = '%s%s%s' % (str(self.settings), file, vfs.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = copy.copy(self.settings)
                if not settings.load(file, copy_content, clear=True):
                    return None
                self.xml_cache[cname] = settings
        else:
            cname = '%s%s' % (file, vfs.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = xml_skin.XMLSkin()
                if not settings.load(file, copy_content, clear=True):
                    return None
                self.xml_cache[cname] = settings

        return settings
    


    def get_skins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skin_files = util.match_files(os.path.join(config.SKIN_DIR, 'main'), ['fxd'])

        # image is not usable stand alone
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/image.fxd'))
        
        for skin in skin_files:
            name  = os.path.splitext(os.path.basename(skin))[0]
            if os.path.isfile('%s.png' % os.path.splitext(skin)[0]):
                image = '%s.png' % os.path.splitext(skin)[0]
            elif os.path.isfile('%s.jpg' % os.path.splitext(skin)[0]):
                image = '%s.jpg' % os.path.splitext(skin)[0]
            else:
                image = None
            ret += [ ( name, image, skin ) ]
        return ret
    
        
    def toggle_display_style(self, menu):
        """
        Toggle display style
        """
        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            self.display_style[menu] = (self.display_style[menu] + 1) % \
                                       len(self.settings.sets[menu].style)
            return 1
            
        if menu.force_skin_layout != -1:
            return 0
        
        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        # get the correct <menu>
        if settings.menu.has_key(menu.item_types):
            area = settings.menu[menu.item_types]
        else:
            area = settings.menu['default']

        if self.display_style['menu'] >=  len(area.style):
            self.display_style['menu'] = 0
        self.display_style['menu'] = (self.display_style['menu'] + 1) % len(area.style)
        return 1


    def get_display_style(self, menu=None):
        """
        return current display style
        """
        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            return self.display_style[menu]
        
        if menu:            
            if menu.force_skin_layout != -1:
                return menu.force_skin_layout
        return self.display_style['menu']


    def __find_current_menu__(self, widget):
        if not widget:
            return None
        if not hasattr(widget, 'menustack'):
            return self.__find_current_menu__(widget.parent)
        return widget.menustack[-1]
        

    def get_popupbox_style(self, widget=None):
        """
        This function returns style information for drawing a popup box.

        return backround, spacing, color, font, button_default, button_selected
        background is ('image', XML_image) or ('rectangle', XML_rectangle)

        XML_image attributes: filename
        XML_rectangle attributes: color (of the border), size (of the border),
           bgcolor (fill color), radius (round box for the border). There are also
           x, y, width and height as attributes, but they may not be needed for the
           popup box

        button_default, button_selected are XML_item
        attributes: font, rectangle (XML_rectangle)

        All fonts are XML_font objects
        attributes: name, size, color, shadow
        shadow attributes: visible, color, x, y
        """

        menu = self.__find_current_menu__(widget)

        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        layout = settings.popup

        background = None

        for bg in layout.background:
            if isinstance(bg, xml_skin.XML_image):
                background = ( 'image', bg)
            elif isinstance(bg, xml_skin.XML_rectangle):
                background = ( 'rectangle', bg)

        button_default  = None
        button_selected = None

        spacing = layout.content.spacing
        color   = layout.content.color

        if layout.content.types.has_key('default'):
            button_default = layout.content.types['default']

        if layout.content.types.has_key('selected'):
            button_selected = layout.content.types['selected']

        return (background, spacing, color, layout.content.font,
                button_default, button_selected)

        

    def get_font(self, name):
        """
        Get the skin font object 'name'. Return the default object if
        a font with this name doesn't exists.
        """
        try:
            return self.settings.font[name]
        except:
            return self.settings.font['default']

        
    def items_per_page(self, (type, object)):
        """
        returns the number of items per menu page
        (cols, rows) for normal menu and
        rows         for the tv menu
        """
        if type == 'tv':
            info = self.areas['tvlisting']
            info = info.get_items_geometry(self.settings, object,
                                           self.get_display_style('tv'))
            return (info[4], info[-1])

        if object.skin_settings:
            settings = object.skin_settings
        else:
            settings = self.settings

        menu = None
        if type == 'menu':
            menu = object

        info = self.areas['listing']
        rows, cols = info.get_items_geometry(settings, object,
                                             self.get_display_style( menu ))[:2]
        return (cols, rows)



    def clear(self, osd_update=True):
        """
        clean the screen
        """
        _debug_('clear: %s' % osd_update, 2)
        self.force_redraw = True
        osd.clearscreen(osd.COL_BLACK)
        if osd_update:
            osd.update()


    def redraw(self):
        """
        redraw the current screen
        """
        _debug_('redraw', 2)
        if self.last_draw[0] and self.last_draw[1]:
            self.draw(self.last_draw)

            
    def draw(self, (type, object)):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """

        if not self.settings.prepared:
            self.settings.prepare()

        if isinstance(object, GUIObject):
            # handling for gui objects: are they visible? what about children?
            if not object.visible:
                return

            draw_allowed = True
            for child in object.children:
                draw_allowed = draw_allowed and not child.visible

            if not draw_allowed:
                self.force_redraw = True
                return

        settings = self.settings
            
        if type == 'menu':
            if not self.freevo_active:
                self.freevo_active = True
                self.settings.prepare()
            menu = object.menustack[-1]
            if menu.skin_settings:
                settings = menu.skin_settings
            # XXX FIXME
            if len(object.menustack) == 1:
                menu.item_types = 'main'
            style = self.get_display_style(menu)

        else:
            try:
                if not object.visible:
                    return
            except AttributeError:
                pass
            style = self.get_display_style(type)


        if self.last_draw[0] != type:
            self.force_redraw = True

        self.last_draw = type, object

        self.screen.clear()

        if isinstance(object, Skin_Area):
            Skin_Area.draw(object, settings, object, style, type, self.force_redraw)
            if object.allow_plugins:
                self.plugin_area.draw(settings, object, style, type, self.force_redraw)
        else:
            all_areas = getattr(self, '%s_areas' % type)
            for a in all_areas:
                a.draw(settings, object, style, type, self.force_redraw)
            
        self.screen.show(self.force_redraw)

        osd.update()
        self.force_redraw = False



