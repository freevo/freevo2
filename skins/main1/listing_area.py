#if 0
# -----------------------------------------------------------------------
# listing_area.py - A listing area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/07/07 20:18:56  dischi
# bugfix
#
# Revision 1.7  2003/07/05 09:25:00  dischi
# use new osd font class for stringsize
#
# Revision 1.6  2003/06/29 20:38:58  dischi
# switch to the new info area
#
# Revision 1.5  2003/05/24 04:29:54  gsbarbieri
# Now we have support to use "type images" in front of items in text listing.
# I.E.: you can have a playlist icon in front of playlists, a folder icon in
# front of folders, and goes...
#
# Revision 1.4  2003/04/24 19:57:52  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/20 15:02:07  dischi
# fall back to text view
#
# Revision 1.2  2003/04/20 13:49:00  dischi
# some special tv show handling
#
# Revision 1.1  2003/04/06 21:19:44  dischi
# Switched to new main1 skin
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

from area import Skin_Area
from skin_utils import *


TRUE  = 1
FALSE = 0


class Listing_Area(Skin_Area):
    """
    this call defines the listing area
    """

    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'listing', screen)
        self.last_choices = ( None, None )
        self.last_get_items_geometry = [ None, None ]

        
    def get_items_geometry(self, settings, menu, display_style):
        """
        get the geometry of the items. How many items per row/col, spaces
        between each item, etc
        """

        # hack for empty directories
        if not len(menu.choices):
            return self.last_get_items_geometry[1]

        if self.last_get_items_geometry[0] == ( menu, settings, display_style ) and \
               hasattr(menu, 'skin_force_text_view'):
            return self.last_get_items_geometry[1]
        
        # store the old values in case we are called by ItemsPerMenuPage
        backup = ( self.area_val, self.layout)

        self.display_style = display_style
        if menu.force_skin_layout != -1:
            self.display_style = menu.force_skin_layout

        self.scan_for_text_view(menu)
        self.init_vars(settings, menu.item_types)

        content   = self.calc_geometry(self.layout.content, copy_object=TRUE)

        self.last_get_items_geometry[0] = ( menu, settings, display_style )
        
        if content.type == 'text':
            items_w = content.width
            items_h = 0
        elif content.type == 'image' or content.type == 'image+text':
            items_w = 0
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
        if content.type == 'text':
            for t in possible_types:
                ct = possible_types[t]

                rh = 0
                rw = 0
                if ct.rectangle:
                    rw, rh, r = self.get_item_rectangle(ct.rectangle, content.width,
                                                        ct.font.h)
                    hskip = min(hskip, r.x)
                    vskip = min(vskip, r.y)
                    items_w = max(items_w, r.width)

                items_h = max(items_h, ct.font.h, rh)

        elif content.type == 'image' or content.type == 'image+text':
            for t in possible_types:
                ct = possible_types[t]
                rh = 0
                rw = 0
                if ct.rectangle:
                    rw, rh, r = self.get_item_rectangle(ct.rectangle, ct.width, ct.height)
                    hskip = min(hskip, r.x)
                    vskip = min(vskip, r.y)

                addh = 0
                if content.type == 'image+text':
                    addh = int(ct.font.h * 1.1)
                    
                items_w = max(items_w, ct.width, rw)
                items_h = max(items_h, ct.height + addh, rh + addh)


        else:
            print 'unknown content type %s' % content.type
            self.area_val, self.layout = backup
            return None
        
        # restore
        self.area_val, self.layout = backup

        # shrink width for text menus
        # FIXME
        width = content.width

        if items_w > width:
            width, items_w = width - (items_w - width), width 

        cols = 0
        rows = 0

        while (cols + 1) * (items_w + content.spacing) - \
              content.spacing <= content.width:
            cols += 1

        while (rows + 1) * (items_h + content.spacing) - \
              content.spacing <= content.height:
            rows += 1

        # return cols, rows, item_w, item_h, content.width
        self.last_get_items_geometry[1] = (cols, rows, items_w + content.spacing,
                                           items_h + content.spacing, -hskip, -vskip,
                                           width)

        return self.last_get_items_geometry[1]



    def update_content_needed(self):
        """
        check if the content needs an update
        """
        if self.last_choices[0] != self.menu.selected:
            return TRUE

        i = 0
        for choice in self.menuw.menu_items:
            try:
                if self.last_choices[1][i] != choice:
                    return TRUE
                i += 1
            except IndexError:
                return TRUE
            
        
    def update_content(self):
        """
        update the listing area
        """

        menuw     = self.menuw
        menu      = self.menu
        settings  = self.settings
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        cols, rows, hspace, vspace, hskip, vskip, width = \
              self.get_items_geometry(settings, menu, self.display_style)


        if not len(menu.choices):
            val = content.types['default']
            self.write_text('This directory is empty', content.font, content)
            
        if content.align == 'center':
            item_x0 = content.x + (content.width - cols * hspace) / 2
        else:
            item_x0 = content.x

        if content.valign == 'center':
            item_y0 = content.y + (content.height - rows * vspace) / 2
        else:
            item_y0 = content.y

        current_col = 1
        
        if content.type == 'image':
            width  = hspace - content.spacing
            height = vspace - content.spacing
            
        last_tvs = ('', 0)
        all_tvs  = TRUE
        
        for choice in menuw.menu_items:
            if choice == menu.selected:
                if content.types.has_key( '%s selected' % choice.type ):
                    val = content.types[ '%s selected' % choice.type ]
                else:
                    val = content.types[ 'selected' ]
            else:
                if content.types.has_key( choice.type ):
                    val = content.types[ choice.type ]
                else:
                    val = content.types['default']

            text = choice.name
            if not text:
                text = "unknown"

            if choice.type == 'playlist':
                text = 'PL: %s' % text

            if choice.type == 'dir' and choice.parent and \
               choice.parent.type != 'mediamenu':
                text = '[%s]' % text

            type_image = None
            if hasattr( val, 'image' ):
                type_image = val.image
                
            if content.type == 'text':
                x0 = item_x0
                y0 = item_y0
                icon_x = 0
                image = None
                if choice.icon:
                    image = self.load_image(choice.icon, (vspace-content.spacing,
                                                          vspace-content.spacing))
                if not image and type_image:
                    image = self.load_image( settings.icon_dir + '/' + type_image,
                                             ( vspace-content.spacing,
                                               vspace-content.spacing ) )
                if image:
                    self.draw_image(image, (x0, y0))
                    icon_x = vspace

                if val.rectangle:
                    r = self.get_item_rectangle(val.rectangle, width, val.font.h)[2]
                    self.drawroundbox(x0 + hskip + r.x + icon_x, y0 + vskip + r.y,
                                      r.width - icon_x, r.height, r)

                # special handling for tv shows
                if choice.type == 'video' and hasattr(choice,'tv_show') and \
                   choice.tv_show and (val.align=='left' or val.align==''):
                    sn = choice.show_name

                    if last_tvs[0] == sn[0]:
                        tvs_w = last_tvs[1]
                    else:
                        season  = 0
                        episode = 0
                        font = val.font.font
                        for c in menuw.menu_items:
                            if c.type == 'video' and hasattr(c,'tv_show') and \
                               c.tv_show and c.show_name[0] == sn[0]:
                                season  = max(season, font.stringsize(c.show_name[1]))
                                episode = max(episode, font.stringsize(c.show_name[2]))
                            else:
                                all_tvs = FALSE

                        if all_tvs and choice.image:
                            tvs_w = font.stringsize('x') + season + episode
                        else:
                            tvs_w = font.stringsize('%s x' % sn[0]) + season + episode
                        last_tvs = (sn[0], tvs_w)
                        
                    self.write_text(' - %s' % sn[3], val.font, content,
                                    x=x0 + hskip + icon_x + tvs_w,
                                    y=y0 + vskip, width=width-icon_x-tvs_w, height=-1,
                                    align_h='left', mode='hard')
                    self.write_text(sn[2], val.font, content,
                                    x=x0 + hskip + icon_x + tvs_w - 100,
                                    y=y0 + vskip, width=100, height=-1,
                                    align_h='right', mode='hard')
                    if all_tvs and choice.image:
                        text = '%sx' % sn[1]
                    else:
                        text = '%s %sx' % (sn[0], sn[1])

                self.write_text(text, val.font, content, x=x0 + hskip + icon_x,
                                y=y0 + vskip, width=width-icon_x, height=-1,
                                align_h=val.align, mode='hard')


            elif content.type == 'image' or content.type == 'image+text':
                rec_h = val.height
                if content.type == 'image+text':
                    rec_h += int(1.1 * val.font.h)

                if val.align == 'center':
                    x0 = item_x0 + (hspace - val.width) / 2
                else:
                    x0 = item_x0 + hskip

                if val.valign == 'center':
                    y0 = item_y0 + (vspace - rec_h) / 2
                else:
                    y0 = item_y0 + vskip

                if val.rectangle:
                    r = self.get_item_rectangle(val.rectangle, val.width, rec_h)[2]
                    self.drawroundbox(x0 + r.x, y0 + r.y, r.width, r.height, r)

                image, i_w, i_h = format_image(settings, choice, val.width,
                                               val.height, force=TRUE)
                if image:
                    addx = 0
                    addy = 0
                    if val.align == 'center' and i_w < val.width:
                        addx = (val.width - i_w) / 2

                    if val.align == 'right' and i_w < val.width:
                        addx = val.width - i_w
            
                    if val.valign == 'center' and i_h < val.height:
                        addy = (val.height - i_h) / 2
                        
                    if val.valign == 'bottom' and i_h < val.height:
                        addy = val.height - i_h

                    self.draw_image(image, (x0 + addx, y0 + addy))
                    
                if content.type == 'image+text':
                    self.write_text(choice.name, val.font, content, x=x0,
                                    y=y0 + val.height, width=val.width, height=-1,
                                    align_h=val.align, mode='hard', ellipses='')
                    
            else:
                print 'no support for content type %s' % content.type

            if current_col == cols:
                if content.align == 'center':
                    item_x0 = content.x + (content.width - cols * hspace) / 2
                else:
                    item_x0 = content.x
                item_y0 += vspace
                current_col = 1
            else:
                item_x0 += hspace
                current_col += 1
                
        # print arrow:
        try:
            if menuw.menu_items[0] != menu.choices[0] and area.images['uparrow']:
                self.draw_image(area.images['uparrow'].filename, area.images['uparrow'])
            if menuw.menu_items[-1] != menu.choices[-1] and area.images['downarrow']:
                self.draw_image(area.images['downarrow'].filename, area.images['downarrow'])
        except:
            # empty menu / missing images
            pass
        
        self.last_choices = (menu.selected, copy.copy(menuw.menu_items))
