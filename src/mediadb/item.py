# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py -
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

# get logging object
log = logging.getLogger('mediainfo')

class ItemInfo:
    def __init__(self, basename, dirname, attr, cache=None):
        if not attr:
            attr = {}
        self.attr = attr
        self.basename = basename
        self.tmp = {}
        self.mminfo = None
        self.hidden_variables = {}
        self.dirname = dirname
        self.filename = self.dirname + '/' + self.basename
        self.cache = cache
        if self.attr.has_key('url'):
            self.url = self.attr['url']
        else:
            self.url = 'file://' + self.filename

    def __str__(self):
        return self.basename


    def __getitem__(self, key):
        if key in ('cover', 'audiocover'):
            if self.attr.has_key(key):
                return self.attr[key]
            elif self.cache:
                return self.cache.data[key]
            return ''

        if self.tmp.has_key(key):
            return self.tmp[key]
        if self.attr.has_key(key):
            return self.attr[key]
        if self.hidden_variables.has_key(key):
            return self.hidden_variables[key]
        if not self.attr.has_key('mminfo'):
            return None
        if self.mminfo == None:
            log.debug('unpickle %s' % self.basename)
            self.mminfo = cPickle.loads(self.attr['mminfo'])
        log.debug('mmget %s (%s)' % (self.basename, key))
        if self.mminfo.has_key(key):
            return self.mminfo[key]
        return None


    def __setitem__(self, key, value):
        if self.attr.has_key(key):
            self.attr[key] = value
            if self.cache:
                self.cache.changed = True
                call_later(self.cache.save)
        else:
            self.tmp[key] = value


    def has_key(self, key):
        if key in ('cover', 'audiocover'):
            return True
        if self.tmp.has_key(key):
            return True
        if self.attr.has_key(key):
            return True
        if self.hidden_variables.has_key(key):
            return True
        if not self.attr.has_key('mminfo'):
            return False
        if self.mminfo == None:
            log.debug('unpickle %s' % self.basename)
            self.mminfo = cPickle.loads(self.attr['mminfo'])
        log.debug('mmget %s (%s)' % (self.basename, key))
        if self.mminfo.has_key(key):
            return True
        return False


    def keys(self):
        ret = [ 'cover', 'audiocover' ]
        if self.mminfo == None:
            if self.attr.has_key('mminfo'):
                log.debug('unpickle %s' % self.basename)
                self.mminfo = cPickle.loads(self.attr['mminfo'])
            else:
                self.mminfo = {}
        for vardict in self.tmp, self.attr, self.hidden_variables, self.mminfo:
            for key in vardict:
                if not key in ret:
                    ret.append(key)
        return ret


    def store(self, key, value):
        self.attr[key] = value
        if self.cache:
            self.cache.changed = True
            call_later(self.cache.save)
        return True


    def store_with_mtime(self, key, value):
        self.attr[key] = value
        if self.cache:
            self.cache.changed = True
            call_later(self.cache.save)
        if not key in self.attr['mtime_dep']:
            self.attr['mtime_dep'].append(key)
        return True


    def get_variables(self):
        return self.tmp


    def set_variables(self, list):
        self.tmp = list


    def set_permanent_variables(self, variables):
        self.hidden_variables = variables

    def delete(self, key):
        pass
