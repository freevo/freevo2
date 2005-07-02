# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - an item returned in listings
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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

__all__ = [ 'ItemInfo' ]

# python imports
import pickle
import cPickle
import logging

# freevo imports
from util.callback import *

# mediadb globals
from globals import *

# get logging object
log = logging.getLogger('mediadb')

class ItemInfo(object):
    """
    Objcets of this class are returned in the different listing functions.
    They store mediadb data and extra data only valid in the current session.
    """
    def __init__(self, basename, dirname, attr, cache=None):
        if not attr:
            # make sure attr is set to something valid
            attr = {}
            if basename:
                attr[EXTENTION] = basename[basename.rfind('.')+1:].lower()
        # attr is the dict that will be stored in the mediadb
        self.attr = attr
        # tmp data only valid in the current session
        self.tmp = {}
        # kaa.metadata data for the item
        self.mminfo = None
        # hidden variables (FIXME)
        self.hidden_variables = {}
        # some basic attributes
        self.basename = basename
        self.dirname = dirname
        self.filename = self.dirname + '/' + self.basename
        # cache this item belongs to (needed for saving)
        self.cache = cache
        if self.attr.has_key(URL):
            self.url = self.attr[URL]
        else:
            self.url = 'file://' + self.filename


    def __str__(self):
        """
        String function for debugging.
        """
        if not self.basename:
            return 'mediadbItem() object'
        return 'mediadbItem() object for %s' % basename


    def __getitem__(self, key):
        """
        Get the itnformation 'key' from the item.
        """
        if key in (COVER, EXTRA_COVER):
            if self.attr.has_key(key):
                return self.attr[key]
            elif self.cache:
                if self.cache.data.has_key(key):
                    return self.cache.data[key]
            return ''

        if self.tmp.has_key(key):
            return self.tmp[key]
        if self.attr.has_key(key):
            return self.attr[key]
        elif key == TITLE and self.attr.has_key(FILETITLE):
            return self.attr[FILETITLE]
        if self.hidden_variables.has_key(key):
            return self.hidden_variables[key]
        if self.mminfo == None:
            # unpickle kaa.metadata data
            if not self.attr.has_key(MMINFO):
                return None
            log.debug('unpickle %s' % self.basename)
            self.mminfo = cPickle.loads(self.attr[MMINFO])
        log.debug('mmget %s (%s)' % (self.basename, key))
        if self.mminfo.has_key(key):
            return self.mminfo[key]
        return None


    def __setitem__(self, key, value):
        """
        Set information. If the key is in attr, the data will be stored in
        the mediadb, else the tmp dict will be used and the information is
        valid only in this object and won't be saved.
        """
        if self.attr.has_key(key):
            self.attr[key] = value
            if self.cache:
                self.cache.changed = True
                call_later(self.cache.save)
        else:
            self.tmp[key] = value


    def has_key(self, key):
        """
        Check if 'key' is in the item somewhere.
        """
        if key in (COVER, EXTRA_COVER):
            return True
        if self.tmp.has_key(key):
            return True
        if self.attr.has_key(key):
            return True
        if self.hidden_variables.has_key(key):
            return True
        if self.mminfo == None:
            # unpickle kaa.metadata data
            if not self.attr.has_key(MMINFO):
                return False
            log.debug('unpickle %s' % self.basename)
            self.mminfo = cPickle.loads(self.attr[MMINFO])
        log.debug('mmget %s (%s)' % (self.basename, key))
        if self.mminfo.has_key(key):
            return True
        return False


    def store(self, key, value):
        """
        Store key/value in the mediadb for later use.
        """
        self.attr[key] = value
        if self.cache:
            self.cache.changed = True
            call_later(self.cache.save)
        return True


    def store_with_mtime(self, key, value):
        """
        Store key/value in the mediadb for later use. The storage depends on
        the modification of the item. If the item is modified on disc, the
        data will be deleted.
        """
        self.attr[key] = value
        if self.cache:
            self.cache.changed = True
            call_later(self.cache.save)
        if not key in self.attr[MTIME_DEP]:
            self.attr[MTIME_DEP].append(key)
        return True


    def get_variables(self):
        return self.tmp


    def set_variables(self, list):
        self.tmp = list


    def set_permanent_variables(self, variables):
        self.hidden_variables = variables


    def delete(self, key):
        pass


    def get_subitem(self, id):
        """
        Get a subitem if the given id.
        """
        if not self.attr.has_key('subitems'):
            # create 'subitems' info
            self.store_with_mtime('subitems', {})
        if not self.attr['subitems'].has_key(id):
            self.attr['subitems'][id] = {}
        info = self.attr['subitems'][id]
        return ItemInfo(self.basename, self.dirname, info, self.cache)
