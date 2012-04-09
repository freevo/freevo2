# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# unpack.py - media plugin for archives
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: Freevo will hang when the sub process is waiting for input in stdin.
#       Maybe replace the WaitBox with an MessageBox and a button to stop the
#       process.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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


# python imports
import os

# kaa imports
import kaa

# freevo imports
from .. import core as freevo

# possible archives and how to unpack them
_cmdlines = {
    'zip': [ 'unzip', '__filename__', '-d', '__dirname__' ],
    'rar': [ 'unrar', 'x', '__filename__', '__dirname__' ] }


class ArchiveItem(freevo.Item):
    """
    Archive item with the action to unpack.
    """
    def __init__(self, fname, parent):
        super(ArchiveItem, self).__init__(parent)
        self.fname = fname
        self.name = os.path.basename(fname)
        self.description = _('Archive File')


    def actions(self):
        """
        Return possible actions for this item.
        """
        return [ freevo.Action(_('Unpack archive'), self.unpack) ]


    def unpack(self):
        """
        Unpack the archive in a sub process.
        """
        app = []
        for param in _cmdlines[os.path.splitext(self.fname)[1][1:]]:
            app.append(param.replace('__filename__', self.fname).\
                       replace('__dirname__', os.path.dirname(self.fname)))
        self.pop = freevo.TextWindow(text=_('unpacking...'))
        self.pop.show()
        child = kaa.Process(app)
        child.start().connect(self.finished)


    def finished(self, exit_code):
        """
        Callback after the process is done.
        """
        self.pop.destroy()

        
class PluginInterface(freevo.MediaPlugin):
    """
    A media plugin for zip and rar archives.
    """
    
    @property
    def suffix(self):
        """
        Return the list of suffixes this class handles
        """
        return _cmdlines.keys()


    def get(self, parent, listing):
        """
        Return a list of items based on the files
        """
        items = []
        for suffix in self.suffix:
            for file in listing.get(suffix):
                items.append(ArchiveItem(file.filename, parent))
        return items
