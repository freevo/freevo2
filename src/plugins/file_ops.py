#if 0 /*
# -----------------------------------------------------------------------
# file_ops.py - Small file operations (currently only delete)
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/10/04 18:37:29  dischi
# i18n changes and True/False usage
#
# Revision 1.6  2003/09/20 15:46:48  dischi
# fxd and imdb patches from Eirik Meland
#
# Revision 1.5  2003/09/20 15:08:26  dischi
# some adjustments to the missing testfiles
#
# Revision 1.4  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.3  2003/09/03 18:03:06  dischi
# fix crash in DEBUG
#
# Revision 1.2  2003/08/31 17:18:33  dischi
# exception handling
#
# Revision 1.1  2003/08/31 17:14:21  dischi
# Move delete file from VideoItem into a global plugin. Now it's also
# possible to remove audio and image files.
#
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
#endif

import os
import config
import plugin

from gui.ConfirmBox import ConfirmBox

class PluginInterface(plugin.ItemPlugin):
    """
    small plugin to delete files
    """

    def actions(self, item):
        """
        create list of possible actions
        """
        items = []
        if ((item.type == 'video' and item.mode == 'file') or \
            item.type in ( 'audio', 'image' )) and not item.media:
            self.item = item
            items.append((self.confirm_delete, _('Delete file'), 'delete'))
            if item.type == 'video' and hasattr(item, 'fxd_file'):
                items.append((self.confirm_info_delete, _('Delete info'), 'delete_info'))
        return items


    def confirm_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text=_('Do you wish to delete\n \'%s\'?') % self.item.name,
                   handler=self.delete_file, default_choice=1).show()
        
    def confirm_info_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text=_('Delete info about\n \'%s\'?') % self.item.name,
                   handler=self.delete_info, default_choice=1).show()

    def safe_unlink(self, filename):
        try:
            os.unlink(filename)
        except:
            print 'can\'t delete %s' % filename
        
    def delete_pictures(self):
        _debug_('Deleting pictures for %s' % self.item.filename)
        if self.item.type in ('video', 'audio'):
            base = os.path.splitext(self.item.filename)[0] + '.'
            if os.path.isfile(base + 'jpg'):
                self.safe_unlink(base + 'jpg')
            if os.path.isfile(base + 'png'):
                self.safe_unlink(base + 'png')

    def delete_fxd(self):
        _debug_('Deleting fxd for %s' % self.item.filename)
        if self.item.type == 'video' and hasattr(self.item, 'fxd_file') and \
               os.path.isfile(self.item.fxd_file) and \
               ((not config.TV_SHOW_DATA_DIR) or \
                (self.item.fxd_file.find(config.TV_SHOW_DATA_DIR) != 0)):
            self.safe_unlink(self.item.fxd_file)

    def delete_file(self):
        _debug_('Deleting %s' % self.item.filename)

        self.delete_pictures()
        self.delete_fxd()

        if os.path.isfile(self.item.filename):
            self.safe_unlink(self.item.filename)

        if self.menuw:
            self.menuw.back_one_menu(arg='reload')

    def delete_info(self):
        _debug_('Deleting info for %s' % self.item.filename)
        self.delete_pictures()
        self.delete_fxd()
        if self.menuw:
            self.menuw.back_one_menu(arg='reload')
