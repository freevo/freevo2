# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# vux.py - Vacillating Utilitarian eXtemporizer
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
# vux.py - a trivial vux plugin for freevo
#
# coded by P.W.deBruin@its.tudelft.nl
#
# Debian packages a simple tool called vux that can
# randomly play a set of files. Based on how a file is
# skipped the 'score' of that file is adapted. My freevo box is
# Debian based, so adding vux is as simple as:
# apt-get install vux
#
# have all the playlist and scorelist stuff done (see man vux)
#
# add a line to local_conf.py containing
# plugin.activate('audio.vux')
#
# TODO
# 1) use mplayer to play ogg/mp3
# 2) display which song is playing
# 3) playlist control and what have you
# 4) ...
#
# Usage: 
# after adding the plugin any of of the items (dir/mp3/ogg) in the music
# menu should have a number of [VUX] entries. 
#
# Todo: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.3  2003/09/20 09:42:32  dischi
# cleanup
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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


class PluginInterface(plugin.ItemPlugin):
    """
    Debian packages a simple tool called vux that can
    randomly play a set of files. Based on how a file is
    skipped the 'score' of that file is adapted. My freevo box is
    Debian based, so adding vux is as simple as:
    apt-get install vux
   
    have all the playlist and scorelist stuff done (see man vux)
   
    add a line to local_conf.py containing
    plugin.activate('audio.vux')
   
    Usage: 
    after adding the plugin any of of the items (dir/mp3/ogg) in the music
    menu should have a number of [VUX] entries. 
    """
    
    def __init__(self):
		
        plugin.ItemPlugin.__init__(self)

        # create actions and corresponding functions
        self.commands = [('default', _('[VUX] Start playing'),           'vuxctl start'),
                         ('default', _('[VUX] Stop playing'),            'vuxctl stop'),
                         ('default', _('[VUX] Next (rating down)'),      'vuxctl down next'),
                         ('default', _('[VUX] Next (rating intact)'),    'vuxctl next'),
                         ('default', _('[VUX] Next (rating up)'),        'vuxctl up next'),
                         ('default', _('[VUX] Playing item rating up'),  'vuxctl up'),
                         ('default', _('[VUX] Playing item rating down'),'vuxctl down'),
                         ('dir',     _('[VUX] a dir item do not select'), None),
                         ('audio',   _('[VUX] an audio item, do not select'), None) ]


    def actions(self, item): 
        items = []
        for action_type in ['default', item.type]:
            items.extend(([(eval('lambda arg=None, menuw=None: os.system("%s")' % x[2]) ,
                            x[1]) for x in self.commands if x[0] == action_type]))

        return items
