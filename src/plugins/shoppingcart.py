# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# shoppingcart.py - Add files to a card and do something
# -----------------------------------------------------------------------------
# $Id$
#
# Todo:
#   o handle fxd files
#   o also add metafiles like covers to the cart
#   o show status in the idlebar
#   o add stuff like making the card a playlist
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

# copy and move in a thread
import kaa

# freevo imports
from .. import core as freevo


class PluginInterface(freevo.ItemPlugin):
    """
    This plugin copies or moves files to directories. Go to a file hit
    enter pick 'add to cart' and then go to a directory. Press enter
    and pick what you want to do.
    """
    def __init__(self):
        super(PluginInterface, self).__init__()
        self.cart = []


    def __move_or_copy_thread(self, cart, operation, dest):
        """
        Do the copy/move in a thread.
        """
        for item in cart:
            getattr(item.files, operation)(dest)


    def move_or_copy(self, item, operation):
        """
        Move/Copy items to the given directory.
        """
        kaa.ThreadCallback(self.__move_or_copy_thread, self.cart, operation,
                           item.filename)()
        self.cart = []
        item.get_menustack().delete_submenu()


    def add_or_remove(self, item):
        """
        Add or remove an item from the cart.
        """
        if item in self.cart:
            self.cart.remove(item)
            txt = _('Removed to Cart')
        else:
            self.cart.append(item)
            txt = _('Added to Cart')
        item.get_menustack().delete_submenu(osd_message=txt)


    def clear(self, item):
        """
        Clear the cart.
        """
        self.cart = []
        item.get_menustack().delete_submenu()


    def actions(self, item):
        """
        Return actions based on the item.
        """
        actions = []

        if item.type == 'dir':
            # It is a dir, so it is possible to copy or move files
            # to this location.
            if len(self.cart) > 0:
                for c in self.cart:
                    if not c.files.move_possible():
                        # moving not possible for this item
                        break
                else:
                    # add move action
                    a = freevo.Action(_('Cart: Move Files Here'), self.move_or_copy)
                    a.parameter('move')
                    actions.append(a)
                # add copy action
                a = freevo.Action(_('Cart: Copy Files Here'), self.move_or_copy)
                a.parameter('copy')
                actions.append(a)

        if item.parent and item.parent.type != 'dir':
            # only activate the following for directory items
            return actions

        if item.type == 'dir':
            if not item in self.cart:
                txt = _('Add Directory to Cart')
            else:
                txt = _('Remove Directory to Cart')
            a = freevo.Action(txt, self.add_or_remove, 'cart:add')
            actions.append(a)

        elif hasattr(item, 'files') and item.files and \
                 item.files.copy_possible():
            if not item in self.cart:
                txt = _('Add Item to Cart')
            else:
                txt = _('Remove Item to Cart')
            a = freevo.Action(txt, self.add_or_remove, 'cart:add')
            actions.append(a)

        if self.cart:
            # add delete option
            actions.append(freevo.Action(_('Delete Cart'), self.clear))

        return actions
