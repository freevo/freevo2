#if 0
# -----------------------------------------------------------------------
# listing.py - A listing area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/02/26 19:18:53  dischi
# Added blue1_small and changed the coordinates. Now there is no overscan
# inside the skin, it's only done via config.OVERSCAN_[XY]. The background
# images for the screen area should have a label "background" to override
# the OVERSCAN resizes.
#
# Revision 1.2  2003/02/25 23:27:36  dischi
# changed max usage
#
# Revision 1.1  2003/02/25 22:56:00  dischi
# New version of the new skin. It still looks the same (except that icons
# are working now), but the internal structure has changed. Now it will
# be easier to do the next steps.
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


import copy

import osd
import util

from area import Skin_Area

# Create the OSD object
osd = osd.get_singleton()

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class Skin_Listing(Skin_Area):
    def __init__(self, parent):
        Skin_Area.__init__(self, 'listing')
        self.last_choices = ( None, None )
        self.depends = ( parent.screen_area, )

    def get_item_rectangle(self, rectangle, item_w, item_h):
        r = copy.copy(rectangle)
        
        if not r.width:
            r.width = item_w

        if not r.height:
            r.height = item_h

        MAX = item_w
        r.x = int(eval('%s' % r.x))
        r.width = int(eval('%s' % r.width))
            
        MAX = item_h
        r.y = int(eval('%s' % r.y))
        r.height = int(eval('%s' % r.height))

        if r.x < 0:
            item_w -= r.x

        if r.y < 0:
            item_h -= r.y

        return max(item_w, r.width), max(item_h, r.height), r
    

    def get_items_geometry(self, settings, menu):
        # store the old values in case we are called by ItemsPerMenuPage
        backup = ( self.area_val, self.layout)
        
        self.init_vars(settings, menu.item_types)

        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        items_w = area.width - content.spacing
        items_h = 0

        possible_types = {}

        hskip = 0
        vskip = 0
        for i in menu.choices:
            if hasattr(i, 'display_type') and i.display_type and \
               content.types.has_key(i.display_type):
                possible_types[i.display_type] = content.types[i.display_type]
            else:
                possible_types['default'] = content.types['default']

            if hasattr(i, 'display_type') and i.display_type and \
               content.types.has_key('%s selected' % i.display_type):
                possible_types['%s selected' % i.display_type] = \
                                   content.types['%s selected' % i.display_type]
            else:
                possible_types['selected'] = content.types['selected']
                
        # get the max height of a text item
        for t in possible_types:
            ct = possible_types[t]

            if not settings.font.has_key(ct.font):
                print '*** font <%s> not found' % ct.font
                break

            font = settings.font[ct.font]
            font_w, font_h = osd.stringsize('Arj', font=font.name, ptsize=font.size)

            rh = 0
            rw = 0
            if ct.rectangle:
                rw, rh, r = self.get_item_rectangle(ct.rectangle, font_w, font_h)
                hskip = min(hskip, r.x)
                vskip = min(vskip, r.y)
                
            items_h = max(items_h, font_h, rh)
            items_w = max(items_w, font_w, rw)

        # restore
        self.area_val, self.layout = backup

        items_w += content.spacing
        items_h += content.spacing

        # return cols, rows, item_w, item_h
        return (content.width/items_w, content.height/items_h,
                items_w, items_h, -hskip, -vskip)


    def update_content_needed(self, settings, menuw):
        menu = menuw.menustack[-1]
        if self.last_choices[0] != menu.selected:
            return TRUE

        i = 0
        for choice in menuw.menu_items:
            if self.last_choices[1][i] != choice:
                return TRUE
            i += 1
                
    def update_content(self, settings, menuw):
        menu = menuw.menustack[-1]

        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        cols, rows, hspace, vspace, hskip, vskip = \
              self.get_items_geometry(settings, menu)

        x0 = area.x + content.spacing
        y0 = area.y + content.spacing

        width  = content.width - 2 * content.spacing

        for choice in menuw.menu_items:
            if choice == menu.selected:
                if content.types.has_key('% selected' % choice.type):
                    val = content.types['% selected' % choice.type]
                else:
                    val = content.types['selected']
            else:
                if content.types.has_key(choice.type):
                    val = content.types[choice.type]
                else:
                    val = content.types['default']
                
            if not settings.font.has_key(val.font):
                print '*** font <%s> not found' % val.font
                break

            font = settings.font[val.font]


            text = choice.name
            if not text:
                text = "unknown"

            if choice.type == 'playlist':
                text = 'PL: %s' % text

            if content.type == 'text':
                font_w, font_h = osd.stringsize('Arj', font=font.name, ptsize=font.size)
                if choice.icon:
                    osd.drawbitmap(util.resize(choice.icon, font_h, font_h), x0, y0)
                    icon_x = font_h + content.spacing
                else:
                    icon_x = 0

                if val.rectangle:
                    None, None, r = self.get_item_rectangle(val.rectangle, width, font_h)
                    if hskip + r.x + r.width > width:
                        r.width = width - hskip - r.y
                    self.drawroundbox(x0 + hskip + r.x + icon_x, y0 + vskip + r.y,
                                      r.width - icon_x, r.height, r)
                                  
                    
                self.write_text(text, font, area, x=x0 + hskip + icon_x, y=y0 + vskip,
                                width=width-icon_x, height=-1, mode='hard')

            else:
                print 'no support for content type %s' % content.type

            y0 += vspace

        self.last_choices = (menu.selected, copy.copy(menuw.menu_items))


        
