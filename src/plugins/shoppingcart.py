# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# shoppingcart.py - Example item plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is a plugin to move and copy files
#
# Activate: 
#   plugin.activate('shoppingcart')
#
# Todo:        
#   o handle fxd files
#   o also add metafiles like covers to the cart
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2005/06/04 17:18:13  dischi
# adjust to gui changes
#
# Revision 1.8  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.7  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
# Revision 1.6  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.5  2004/01/31 13:15:14  dischi
# only add the plugin if the parent is a dir
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
# ----------------------------------------------------------------------- */


import os
import plugin
import config
import shutil
import util
import eventhandler
import event as em
import menu
from gui.windows import WaitBox

class PluginInterface(plugin.ItemPlugin):
    """
    This plugin copies or moves files to directories. Go to a file hit
    enter pick 'add to cart' and then go to a directory. Press enter
    and pick what you want to do.

    plugin.activate('shoppingcart')

    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)
        self.item = None
        self.cart = []

    def moveHere(self, arg=None, menuw=None):
        popup = WaitBox(text=_('Moving files...'))
        popup.show()
        for cartfile in self.cart:
            cartfile.files.move(self.item.dir)
        popup.destroy()
        self.cart = []
        eventhandler.post(em.MENU_BACK_ONE_MENU)


    def copyHere(self, arg=None, menuw=None):
        popup = WaitBox(text=_('Copying files...'))
        popup.show()
        for cartfile in self.cart:
            cartfile.files.copy(self.item.dir)
        popup.destroy()
        self.cart = []
        eventhandler.post(em.MENU_BACK_ONE_MENU)


    def addToCart(self, arg=None, menuw=None):
        self.cart.append(self.item)
        if isinstance(menuw.menustack[-1].selected, menu.MenuItem):
            eventhandler.post(em.MENU_BACK_ONE_MENU)
        else:
            eventhandler.post(em.Event(em.OSD_MESSAGE, arg=_('Added to Cart')))
            

    def deleteCart(self, arg=None, menuw=None):
        self.cart = []
        eventhandler.post(em.MENU_BACK_ONE_MENU)


    def actions(self, item):
        self.item = item
        myactions = []

        if self.item.parent and self.item.parent.type != 'dir':
            # only activate this for directory items
            return []

        if item.type == 'dir':
            if len(self.cart) > 0:
                for c in self.cart:
                    if not c.files.move_possible():
                        break
                else:
                    myactions.append((self.moveHere, _('Cart: Move Files Here')))
                myactions.append((self.copyHere, _('Cart: Copy Files Here')))

            if not item in self.cart:
                myactions.append((self.addToCart, _('Add Directory to Cart'), 'cart:add'))

        elif hasattr(item, 'files') and item.files and item.files.copy_possible() and \
                 not item in self.cart:
            myactions.append((self.addToCart, _('Add File to Cart'), 'cart:add'))

        if self.cart:
            myactions.append((self.deleteCart, _('Delete Cart')))

        return myactions

