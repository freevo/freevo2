# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# default_areas.py - Some areas for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This file contains only small areas, other areas like
#        ListingArea have there own file
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2004/10/03 10:16:48  dischi
# remove old code we do not need anymore
#
# Revision 1.5  2004/08/22 20:06:18  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.4  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
#
# Revision 1.3  2004/08/05 17:30:24  dischi
# cleanup
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
# -----------------------------------------------------------------------


from area import Area


class Screen_Area(Area):
    """
    this area is the screen or background of the skin
    """
    def __init__(self):
        Area.__init__(self, 'screen')



class Title_Area(Area):
    """
    in this area the title of the menu is drawn
    """
    def __init__(self, type='title'):
        Area.__init__(self, type)
        self.text = (None, None, None)
        self.gui_object = None


    def clear(self):
        """
        delete the title
        """
        if self.gui_object:
            self.gui_object.unparent()
            self.gui_object = None
        self.text = (None, None, None)

            
    def update(self):
        """
        update the screen area
        """
        menu      = self.menu
        content   = self.calc_geometry(self.layout.content, copy_object=True)

        text = ''
        try:
            item = menu.selected
            if content.type == 'menu':
                text = menu.heading
            elif len(menu.choices) == 0:
                text = ''
            elif content.type == 'short item':
                if item.type == 'video' and item.tv_show and \
                       ((item.image and not item.image.endswith('.raw')) or \
                        (item.parent and item.parent.name == item.show_name[0])):
                    sn   = item.show_name
                    text = sn[1] + "x" + sn[2] + " - " + sn[3] 
                elif item.parent and len(item.parent.name) > 5 and \
                         Unicode(item.name).startswith(Unicode(item.parent.name)):
                    text = item.name[len(item.parent.name):].strip(' -_')
                    if not text:
                        text = item.name
                else:
                    text = item.name
            else:
                text = item.name
        except AttributeError:
            try:
                if menu.type == 'tv':
                    if content.type == 'item' or content.type == 'short item':
                        text = menu.table[1].title
                    else:
                        text = _('TV GUIDE')
            except:
                pass

        if not text:
            if hasattr(self.infoitem, 'name'):
                text = self.infoitem.name
            else:
                if content.type == 'short item' and hasattr(menu, 'subtitle'):
                    text = menu.subtitle
                elif hasattr(menu, 'title'):
                    text = menu.title

        if self.text == (text, content.font, content):
            return
        
        self.clear()
        self.text = text, content.font, content
        self.gui_object = self.drawstring(text, content.font, content,
                                          height=-1, mode='hard')
        


class Subtitle_Area(Title_Area):
    """
    in this area the subtitle of the menu is drawn
    """
    def __init__(self):
        Title_Area.__init__(self, 'subtitle')
