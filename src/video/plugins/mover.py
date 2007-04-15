# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mover.py - Move files to a predefined directory
# -----------------------------------------------------------------------------
# $Id$
#
# This is an example how plugins work. This plugin add a move action to movie
# items in a given directory to move the item to a second given directory.
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

# Python imports
import os
import logging

# Freevo imports
from freevo.ui.menu import ItemPlugin, Action

# get logging object
log = logging.getLogger('video')


class PluginInterface(ItemPlugin):
    """
    Plugin to move video files

    Activate:
      plugin.activate('video.mover', args=('from-dir', 'to-dir'))

    from_dir: from which directory the files should be moved from
    to_dir:   to which directory the files should be moved to

    Optional parameters:
    recursive (boolean): should the plugin work for every subdirectory of
                         the from-directory (defaults to False)

      This parameter can be used to make a 'safe delete function':
      map(lambda dir: plugin.activate('video.mover', args=(dir[1],
                                                           '/mnt/media/trash',
                                                           True)),
          VIDEO_ITEMS)


    makedirs (boolean): should freevo create the to-dir if it doesn't exist
                        (defaults to False)

      This parameter can be used to move seen tv-episodes/movies
      into a subdirectory ('seen'):

      map(lambda dir: plugin.activate('video.mover', args=(dir[1],
                                                           'seen',
                                                           True,
                                                           True)),
          VIDEO_ITEMS)

      When to-dir is not specified as an absolute path, the mover will try
      to locate it in the current dir. If makedirs==True and to-dir
      doesn't exist, it will be created in the current-dir.

    """
    def __init__(self, from_dir, to_dir, recursive=False, makedirs=False):
        """
        Init the plugin.
        """
        ItemPlugin.__init__(self)
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.recursive = recursive
        self.makedirs = makedirs


    def actions(self, item):
        """
        Return possible actions for the given item. This is either nothing
        or the move action.
        """
        if item.type != 'video' or item.mode != 'file' or \
           item.parent.type != 'dir':
            # we don't move such items
            return []

        if self.to_dir == os.path.dirname(item.filename):
            # don't bother moving to current-dir
            return []

        cp = os.path.commonprefix((item.parent.filename, self.from_dir))
        if (self.recursive and cp == self.from_dir) \
           or ( item.parent.filename == self.from_dir) \
           or ( item.parent.filename == self.from_dir + '/'):
               # Create Action
               name = _('Move to [%s]') % os.path.basename(self.to_dir)
               return [ Action(name, self.move_item) ]

        # nothing to do
        return []


    def move_item(self, item):
        # make to_dir an absolute path
        local_to_dir = self.to_dir
        if not os.path.isabs(self.to_dir):
            local_to_dir = os.path.join(os.path.dirname(item.filename),
                                        self.to_dir)

        # make to_dir if it doesn't exist and makedirs==True
        if not os.path.exists(local_to_dir):
            if os.path.exists(os.path.dirname(local_to_dir)):
                if self.makedirs:
                    os.makedirs(local_to_dir)
                else:
                    log.info("Path doesn't exist, and makedirs=%s" % \
                             self.makedirs)

        elif not os.path.isdir(local_to_dir):
            log.info("%s is not a dir" % local_to_dir)

        elif item.files:
            item.files.move(local_to_dir)

        else:
            log.info("no files to move")

        item.show_menu()
