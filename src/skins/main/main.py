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
# Revision 1.46  2004/07/09 11:20:12  dischi
# do not load outdated skins
#
# Revision 1.45  2004/03/14 11:42:34  dischi
# make idlebar have a background image
#
# Revision 1.44  2004/02/24 19:50:35  dischi
# change extra area location to skins/plugins
#
# Revision 1.43  2004/02/24 19:36:25  dischi
# add function to change a skin area
#
# Revision 1.42  2004/02/22 20:46:46  dischi
# oops, remove test code
#
# Revision 1.41  2004/02/22 20:46:09  dischi
# add Unicode error warning
#
# Revision 1.40  2004/02/18 21:54:03  dischi
# small update needed for the new gui code
#
# Revision 1.39  2004/02/14 13:00:39  dischi
# function to return the settings
#
# Revision 1.38  2004/02/06 18:24:39  dischi
# make to possible to override busy icon with skin
#
# Revision 1.37  2004/02/02 23:06:03  outlyer
# This probably isn't neccessary to show every startup.
#
# Revision 1.36  2004/02/01 17:03:58  dischi
# speedup
#
# Revision 1.35  2004/01/18 16:45:32  dischi
# store last skin information
#
# Revision 1.34  2004/01/13 19:12:02  dischi
# support for basic.fxd
#
# Revision 1.33  2004/01/13 17:20:54  dischi
# fixed display toggle
#
# Revision 1.32  2004/01/13 15:46:19  outlyer
# Temporary fix for a crash.... probably not the ideal solution, but I don't
# have the time right now to investigate fully.
#
# To reproduce the crash, remove the "hasattr()" line and click 'display'
# when in any 'feature' menu (TV, Movies, Music, etc.)
#
# Revision 1.31  2004/01/10 13:20:52  dischi
# better skin cache function and set_base_fxd to load a basic skin
#
# Revision 1.30  2004/01/09 20:04:18  dischi
# add overscan to cache name
#
# Revision 1.29  2004/01/05 18:03:43  dischi
# support for extra fxd files for plugins
#
# Revision 1.28  2004/01/01 12:26:15  dischi
# use pickle to cache parsed skin files
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


import os, copy
import stat
import traceback

import config
import util
import osd

from area import Skin_Area
from gui  import GUIObject

import xml_skin
import screen

# Create the OSD object
osd = osd.get_singleton()

###############################################################################
# Skin main functions
###############################################################################


class Skin:
    """
    main skin class
    """
    
    Rectange = xml_skin.Rectangle
    Image    = xml_skin.Image
    Area     = Skin_Area

    def __init__(self):
        """
        init the skin engine
        """
        global skin_engine
        skin_engine = self
        
        self.display_style = { 'menu' : 0 }
        self.force_redraw  = True
        self.last_draw     = None, None, None
        self.screen        = screen.get_singleton()
        self.areas         = {}

        # load default areas
        from listing_area   import Listing_Area
        from tvlisting_area import TVListing_Area
        from view_area      import View_Area
        from info_area      import Info_Area
        from default_areas  import Screen_Area, Title_Area, Subtitle_Area, Plugin_Area
        
        for a in ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info', 'plugin'):
            self.areas[a] = eval('%s_Area()' % a.capitalize())
        self.areas['tvlisting'] = TVListing_Area()

        self.storage_file = os.path.join(config.FREEVO_CACHEDIR, 'skin-%s' % os.getuid())
        self.storage = util.read_pickle(self.storage_file)
        if self.storage:
            if not config.SKIN_XML_FILE:
                config.SKIN_XML_FILE = self.storage['SKIN_XML_FILE']
            else:
                _debug_('skin forced to %s' % config.SKIN_XML_FILE, 2)
        else:
            if not config.SKIN_XML_FILE:
                config.SKIN_XML_FILE = config.SKIN_DEFAULT_XML_FILE
            self.storage = {}
            
        # load the fxd file
        self.settings = xml_skin.XMLSkin()
        self.set_base_fxd(config.SKIN_XML_FILE)


    def cachename(self, filename):
        """
        create cache name
        """
        geo  = '%sx%s-%s-%s' % (osd.width, osd.height, config.OSD_OVERSCAN_X,
                                config.OSD_OVERSCAN_Y)
        return vfs.getoverlay('%s.skin-%s-%s' % (filename, config.SKIN_XML_FILE, geo))

        
    def save_cache(self, settings, filename):
        """
        cache the fxd skin settings in 'settings' to the OVERLAY_DIR cachfile
        for filename and this resolution
        """
        cache = self.cachename(filename)
        if cache:
            # delete font object, because it can't be pickled
            for f in settings.font:
                del settings.font[f].font
            # save object and version information
            util.save_pickle((xml_skin.FXD_FORMAT_VERSION, settings), cache)
            # restore font object
            for f in settings.font:
                settings.font[f].font = osd.getfont(settings.font[f].name,
                                                    settings.font[f].size)
            

    def load_cache(self, filename):
        """
        load a skin cache file
        """
        if hasattr(self, '__last_load_cache__') and self.__last_load_cache__[0] == filename:
            return self.__last_load_cache__[1]
            
        if not os.path.isfile(filename):
            return None
        
        cache = self.cachename(filename)
        if not cache:
            return None

        if not os.path.isfile(cache):
            return None
        
        version, settings = util.read_pickle(cache)
        if not settings or version != xml_skin.FXD_FORMAT_VERSION:
            return None

        pdir = os.path.join(config.SHARE_DIR, 'skins/plugins')
        if os.path.isdir(pdir):
            ffiles = util.match_files(pdir, [ 'fxd' ])
        else:
            ffiles = []

        for f in settings.fxd_files:
            if not os.path.dirname(f).endswith(pdir):
                ffiles.append(f)
            
        # check if all files used by the skin are not newer than
        # the cache file
        ftime = os.stat(cache)[stat.ST_MTIME]
        for f in ffiles:
            if os.stat(f)[stat.ST_MTIME] > ftime:
                return None

        # restore the font objects
        for f in settings.font:
            settings.font[f].font = osd.getfont(settings.font[f].name,
                                                settings.font[f].size)
        self.__last_load_cache__ = filename, settings
        return settings

        
    def register(self, type, areas):
        """
        register a new type objects to the skin
        """
        setattr(self, '%s_areas' % type, [])
        for a in areas:
            if isinstance(a, str):
                getattr(self, '%s_areas' % type).append(self.areas[a])
            else:
                getattr(self, '%s_areas' % type).append(a)


    def delete(self, type):
        """
        delete informations about a special skin type
        """
        exec('del self.%s_areas' % type)
        self.last_draw = None, None, None


    def change_area(self, name, module, object):
        """
        replace an area with the code from module.object() from skins/plugins
        """
        exec('import skins.plugins.%s' % module)
        self.areas[name] = eval('skins.plugins.%s.%s()' % (module, object))

        
    def set_base_fxd(self, name):
        """
        set the basic skin fxd file
        """
        config.SKIN_XML_FILE = os.path.splitext(os.path.basename(name))[0]
        _debug_('load basic skin settings: %s' % config.SKIN_XML_FILE)
        
        # try to find the skin xml file
        if not self.settings.load(name, clear=True):
            print "skin not found, using fallback skin"
            self.settings.load('basic.fxd', clear=True)
            
        for dir in config.cfgfilepath:
            local_skin = '%s/local_skin.fxd' % dir
            if os.path.isfile(local_skin):
                _debug_('Skin: Add local config %s to skin' % local_skin,2)
                self.settings.load(local_skin)
                break

        self.storage['SKIN_XML_FILE'] = config.SKIN_XML_FILE
        util.save_pickle(self.storage, self.storage_file)

        if self.storage.has_key(config.SKIN_XML_FILE):
            self.display_style['menu'] = self.storage[config.SKIN_XML_FILE]
        else:
            self.display_style['menu'] = 0
        
        
    def load(self, filename, copy_content = 1):
        """
        return an object with new skin settings
        """
        _debug_('load additional skin info: %s' % filename)
        if filename and vfs.isfile(vfs.join(filename, 'folder.fxd')):
            filename = vfs.abspath(os.path.join(filename, 'folder.fxd'))

        elif filename and vfs.isfile(filename):
            filename = vfs.abspath(filename)

        else:
            return None

        settings = self.load_cache(filename)
        if settings:
            return settings
            
        if copy_content:
            settings = copy.copy(self.settings)
        else:
            settings = xml_skin.XMLSkin()

        if not settings.load(filename, clear=True):
            return None

        self.save_cache(settings, filename)
        return settings
    


    def get_skins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skin_files = util.match_files(os.path.join(config.SKIN_DIR, 'main'), ['fxd'])

        # image is not usable stand alone
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/image.fxd'))
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/basic.fxd'))
        
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


    def get_settings(self):
        """
        return the current loaded settings
        """
        return self.settings
    
        
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

        if settings.special_menu.has_key(menu.item_types):
            area = settings.special_menu[menu.item_types]
        else:
            area = settings.default_menu['default']

        if self.display_style['menu'] >=  len(area.style):
            self.display_style['menu'] = 0
        self.display_style['menu'] = (self.display_style['menu'] + 1) % len(area.style)

        self.storage[config.SKIN_XML_FILE] = self.display_style['menu']
        util.save_pickle(self.storage, self.storage_file)
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
        background is ('image', Image) or ('rectangle', Rectangle)

        Image attributes: filename
        Rectangle attributes: color (of the border), size (of the border),
           bgcolor (fill color), radius (round box for the border). There are also
           x, y, width and height as attributes, but they may not be needed for the
           popup box

        button_default, button_selected are XML_item
        attributes: font, rectangle (Rectangle)

        All fonts are Font objects
        attributes: name, size, color, shadow
        shadow attributes: visible, color, x, y
        """
        menu = self.__find_current_menu__(widget)

        if menu and hasattr(menu, 'skin_settings') and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        layout = settings.popup

        background = []
        for bg in layout.background:
            if isinstance(bg, xml_skin.Image):
                background.append(( 'image', bg))
            elif isinstance(bg, xml_skin.Rectangle):
                background.append(( 'rectangle', bg))

        return layout.content, background


    def get_font(self, name):
        """
        Get the skin font object 'name'. Return the default object if
        a font with this name doesn't exists.
        """
        try:
            return self.settings.font[name]
        except:
            return self.settings.font['default']

        
    def get_image(self, name):
        """
        Get the skin image object 'name'. Return None if
        an image with this name doesn't exists.
        """
        try:
            return self.settings.images[name]
        except:
            return None

        
    def get_icon(self, name):
        """
        Get the icon object 'name'. Return the icon in the theme dir if it
        exists, else try the normal image dir. If not found, return ''
        """
        icon = util.getimage(os.path.join(self.settings.icon_dir, name))
        if icon:
            return icon
        return util.getimage(os.path.join(config.ICON_DIR, name), '')

        
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
            self.draw(self.last_draw[0], self.last_draw[1], self.last_draw[2])


    def prepare(self):
        """
        prepare the skin
        """
        self.settings.prepare()

        
    def draw(self, type, object, menu=None):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """
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
            self.all_areas    = getattr(self, '%s_areas' % type)
            

        self.last_draw = type, object, menu

        try:
            self.screen.clear()
            for a in self.all_areas:
                a.draw(settings, object, menu, style, type, self.force_redraw)
            osd.update([self.screen.show(self.force_redraw)])
            self.force_redraw = False
        except UnicodeError, e:
            print '******************************************************************'
            print 'Unicode Error: %s' % e
            print 'Please report the following lines to the freevo mailing list'
            print 'or with the subject \'[Freevo-Bugreport\] Unicode\' to'
            print 'freevo@dischi-home.de.'
            print
            print traceback.print_exc()
            print
            print type, object
            if type == 'menu':
                for i in object.menustack[-1].choices:
                    print i
            print
            raise UnicodeError, e
