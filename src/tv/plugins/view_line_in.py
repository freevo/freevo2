# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# view_line_in.py - view the line in in VCR mode
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.1  2004/02/23 18:07:10  mikeruelle
# add this as a plugin instead of the funky if in tvmenu.py
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


import config
import plugin
import menu

class PluginInterface(plugin.Plugin):
    """
    """
    def __init__(self):
        """
        normal plugin init, but sets _type to 'mainmenu_tv'
        """
        plugin.Plugin.__init__(self)
        self._type = 'mainmenu_tv'
        self.parent = None
                                                                                
    def items(self, parent):
        self.parent = parent
        return [menu.MenuItem(_('View VCR Input'), action=self.start_vcr)]
                                                                                
    def start_vcr(self, menuw=None, arg=None):
        plugin.getbyname(plugin.TV).Play('vcr', None)

