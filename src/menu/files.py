# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# file.py - File handling for items
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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

__all__ = [ 'Files' ]

# python imports
import os
import shutil
import logging

# freevo imports
import util

# get logging object
log = logging.getLogger()

class Files(object):
    """
    File operations for an item.
    """
    def __init__(self):
        self.files     = []
        self.fxd_file  = ''
        self.image     = ''
        self.read_only = False


    def append(self, filename):
        """
        Append a file to the list.
        """
        self.files.append(filename)


    def get(self):
        """
        Return all files.
        """
        return self.files


    def copy_possible(self):
        """
        Return true if it is possible to copy the files.
        """
        return self.files != []


    def copy(self, destdir):
        """
        Copy all files to destdir.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if f:
                if not os.path.isdir(destdir):
                    os.makedirs(destdir)
                shutil.copy(f, destdir)


    def move_possible(self):
        """
        Return true if it is possible to move the files.
        """
        return self.files and not self.read_only


    def move(self, destdir):
        """
        Move all files to destdir.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if f:
                if not os.path.isdir(destdir):
                    os.makedirs(destdir)
                os.system('mv "%s" "%s"' % (f, destdir))


    def delete_possible(self):
        """
        Return true if it is possible to delete the files.
        """
        return self.files and not self.read_only


    def delete(self):
        """
        Delete all files.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if not f:
                continue
            util.unlink(f)
