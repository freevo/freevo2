#if 0
# -----------------------------------------------------------------------
# info_area.py - An info area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/03/18 09:37:00  dischi
# Added viewitem and infoitem to the menu to set an item which image/info
# to take (only for the new skin)
#
# Revision 1.8  2003/03/16 19:36:04  dischi
# Adjustments to the new xml_parser, added listing type 'image+text' to
# the listing area and blue2, added grey skin. It only looks like grey1
# in the menu. The skin inherits from blue1 and only redefines the colors
# and the fonts. blue2 now has an image view for the image menu.
#
# Revision 1.7  2003/03/14 19:38:48  dischi
# some cosmetic fixes
#
# Revision 1.6  2003/03/13 21:02:04  dischi
# misc cleanups
#
# Revision 1.5  2003/03/11 20:38:48  dischi
# some speed ups
#
# Revision 1.4  2003/03/11 20:26:48  dischi
# Added tv info area. After that day of work, I needed to do something
# that has a result
#
# Revision 1.3  2003/03/07 17:28:18  dischi
# small fixes
#
# Revision 1.2  2003/03/06 21:45:24  dischi
# Added mp3 player view area. You can set the infos you want to see in the
# skin. @VAR@ means insert a variable from the item object here, \t means
# next col (currently only two cols are supported). I don't like the
# delimiter @@ and \t, but I don't have a better idea (&var; doesn't work
# because pyXML want's to replace it)
#
# Revision 1.1  2003/03/05 21:55:21  dischi
# empty info area
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
# -----------------------------------------------------------------------
#endif

from area import Skin_Area
from skin_utils import *

import re

TRUE  = 1
FALSE = 0

class Info_Area(Skin_Area):
    """
    this call defines the view area
    """

    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'info', screen)
        self.re_space    = re.compile('^\t *(.*)')
        self.re_var      = re.compile('@[a-z_]*@')
        self.re_table    = re.compile('^(.*)\\\\t(.*)')

        self.last_item   = None
        self.auto_update = []
        self.table       = []

    def update_content_needed(self):
        """
        check if the content needs an update
        """
        return self.auto_update or (self.last_item != self.infoitem)
        

    def update_content(self):
        """
        update the info area
        """
        content   = self.calc_geometry(self.layout.content, copy_object=TRUE)
        item      = self.infoitem

        if hasattr(item, 'type') and content.types.has_key(item.type):
            val = content.types[item.type]
        else:
            val = content.types['default']

        table = [ [], [] ]
        self.auto_update = []

        for line in val.cdata.encode('Latin-1').split('\n'):
            m = self.re_space.match(line)
            if m:
                line = m.groups(1)[0]

            has_vars       = FALSE 
            autoupdate     = ''
            vars_exists    = FALSE

            for m in self.re_var.findall(line):
                has_vars = TRUE
                if m[1:-1] == 'elapsed':
                    autoupdate = 'elapsed'

                a = item.getattr(m[1:-1])
                if a:
                    line = re.sub(m, a, line)
                    vars_exists = TRUE
                else:
                    line = re.sub(m, '', line)

            if ((not has_vars) or vars_exists) and (line or table[0]):
                m = self.re_table.match(line)
                if m:
                    table[0] += [ m.groups(1)[0] ]
                    table[1] += [ m.groups(2)[1] ]
                    if autoupdate:
                        self.auto_update += [ ( autoupdate, len(table[0]) - 1) ]
                else:
                    table[0] += [ line ]
                    table[1] += [ '' ]

        x0 = content.x

        font = content.font
        y_spacing = font.h * 1.1
            
        w = 0
        for row in table[0]:
            w = max(w, osd.stringsize(row, font=font.name, ptsize=font.size)[0])
            if x0 + w > content.x + content.width:
                w = content.x + content.width - x0

        y0 = content.y
        for i in range(0,len(table[0])):
            if table[0][i] and not table[1][i]:
                rec = self.write_text(table[0][i], font, content, x=x0, y=y0, width=w,
                                      height=content.height + content.y - y0, mode='soft',
                                      return_area = TRUE)
                y0 += rec[3]-rec[1]
            else:
                if table[0][i]:
                    self.write_text(table[0][i], font, content, x=x0, y=y0, width=w,
                                    height=-1, mode='hard')
                if table[1][i]:
                    self.write_text(table[1][i], font, content, x=x0+w+content.spacing, y=y0,
                                    width=content.width - w - content.spacing,
                                    height=-1, mode='hard')
                y0 += y_spacing

        self.last_item = self.infoitem
        self.table = table
