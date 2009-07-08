# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# beacon.py - interface to kaa.beacon
# -----------------------------------------------------------------------------
# $Id$
#
# This file extends beacon with some functiosn freevo needs.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2006-2009 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

# kaa imports
import kaa.beacon

class ExtMap(dict):

    def get(self, attr):
        r = dict.get(self, attr)
        if r == None:
            self[attr] = []
            return self[attr]
        return r

def extmap_filter(results):
    extmap = ExtMap()
    if not isinstance(results, (list, tuple)):
        results = [ results ]
    extmap.get('beacon:all').extend(results)
    for r in results:
        t = r.get('type')
        if t and t != 'file':
            extmap.get('beacon:%s' % t).append(r)
        elif r.isdir:
            extmap.get('beacon:dir').append(r)
        elif r.isfile:
            pos = r.get('name').rfind('.')
            if pos <= 0 and pos +1 == len(r.get('name')):
                extmap.get('beacon:file').append(r)
            else:
                extmap.get(r.get('name')[pos+1:]).append(r)
        else:
            extmap.get('beacon:item').append(r)
    return extmap

def register_attributes(info):
    for type in info['types']:
        if type != 'media':
            kaa.beacon.register_file_type_attrs(type,
               freevo_cache  = (list, kaa.beacon.ATTR_SIMPLE),
               freevo_config = (dict, kaa.beacon.ATTR_SIMPLE),
               last_played = (int, kaa.beacon.ATTR_SEARCHABLE))

@kaa.coroutine()
def connect():
    kaa.beacon.register_filter('extmap', extmap_filter)
    try:
        yield kaa.beacon.connect()
    except kaa.beacon.ConnectError:
        yield kaa.beacon.launch(verbose='all', autoshutdown=True)
    # get db info and connect additional attributes
    register_attributes((yield kaa.beacon.get_db_info()))
