# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mainmenu.py - Freevo main menu page
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the main menu and a class for main menu plugins. There
# is also eventhandler support for the main menu showing the skin chooser.
#
# First edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
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
# -----------------------------------------------------------------------------


__all__ = [ 'MainMenuItem', 'MainMenu' ]

# python imports
import os

# freevo imports
import config
import gui.theme
import mediadb
import util
import plugin

from menu import Item, Action, Menu
from application.menuw import MenuWidget
from event import *


class MainMenuItem(Item):
    """
    This class is a main menu item. Items of this type can be returned by
    a MainMenuPlugin.
    """
    def __init__( self, name='', action=None, arg=None, type=None, image=None,
                  icon=None, parent=None, skin_type=None):

        Item.__init__(self, parent)
        self.name = Unicode(name)
        self.icon = icon
        self.image = image
        self.type = type
        self.function = action, arg

        if not type and not parent.parent:
            # this is the first page, force type to 'main'
            self.type = 'main'
            
        if not skin_type:
            return
        
        # load extra informations for the skin fxd file
        theme     = gui.theme.get()
        skin_info = theme.mainmenu.items
        imagedir  = theme.mainmenu.imagedir
        if skin_info.has_key(skin_type):
            skin_info  = skin_info[skin_type]
            self.name  = _(skin_info.name)
            self.image = skin_info.image
            if skin_info.icon:
                self.icon = os.path.join(theme.icon_dir, skin_info.icon)
            if skin_info.outicon:
                self.outicon = os.path.join(theme.icon_dir, skin_info.outicon)

        if not self.image and imagedir:
            # find a nice image based on skin type
            self.image = util.getimage(os.path.join(imagedir, skin_type))


    def actions(self):
        """
        Actions for this item.
        """
        a = Action(self.name, self.function[0])
        a.parameter(menuw=self.get_menustack(), arg=self.function[1])
        return [ a ]

    
class SkinSelectItem(Item):
    """
    Item for the skin selector
    """
    def __init__(self, parent, name, image, skin):
        Item.__init__(self, parent)
        self.name  = name
        self.image = image
        self.skin  = skin


    def actions(self):
        """
        Return the select function to load that skin
        """
        return [ Action(self.name, self.select) ]


    def select(self):
        """
        Load the new skin and rebuild the main menu
        """
        # load new theme
        theme = gui.theme.set_base_fxd(self.skin)
        # set it to the main menu as used theme
        pos = self.get_menustack()[0].theme = theme
        # and go back
        self.get_menustack().back_one_menu()




class MainMenu(Item):
    """
    This class handles the main menu. It will start the main menu widget
    and the first menu page based on the main menu plugins.
    """
    def __init__(self):
        """
        Setup the main menu and handle events (remote control, etc)
        """
        Item.__init__(self)
        items = []
        for p in plugin.get('mainmenu'):
            items += p.items(self)
        menu = Menu(_('Freevo Main Menu'), items, item_types='main',
                    theme = gui.theme.get(), reload_func=self.reload)
        self.menuw = MenuWidget()
        self.menuw.pushmenu(menu)
        self.menuw.show()

        
    def reload(self):
        # stop mediadb.watcher
        mediadb.watcher.cwd(None)

        
    def get_skins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skindir = os.path.join(config.SKIN_DIR, 'main')
        skin_files = util.match_files(skindir, ['fxd'])

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


    def get_menustack(self):
        """
        Get the menustack. This item needs to override this function
        because it is not bound to a menupage.
        """
        return self.menuw


    def eventhandler(self, event, menuw=None):
        """
        Automatically perform actions depending on the event, e.g. play DVD
        """
        # pressing DISPLAY on the main menu will open a skin selector
        # (only for the new skin code)
        if event == MENU_CHANGE_STYLE:
            items = []
            for name, image, skinfile in self.get_skins():
                items += [ SkinSelectItem(self, name, image, skinfile) ]

            self.pushmenu(Menu(_('Skin Selector'), items))
            return True

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
