# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# listing_area.py - A listing area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/24 12:21:31  dischi
# use new renderer and screen features
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.28  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.27  2004/03/14 17:22:47  dischi
# seperate ellipses and dim in drawstringframed
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


import copy

from area import Skin_Area
from skin_utils import *
import config

class Listing_Area(Skin_Area):
    """
    this call defines the listing area
    """

    def __init__(self):
        Skin_Area.__init__(self, 'listing')
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

        content   = self.calc_geometry(self.layout.content, copy_object=True)

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
            if hasattr(i, 'display_type') and i.display_type:
                x = i.display_type
                if content.types.has_key(x) and not possible_types.has_key(x):
                    possible_types[x] = content.types[x]
                x = '%s selected' % i.display_type
                if content.types.has_key(x) and not possible_types.has_key(x):
                    possible_types[x] = content.types[x]

        if content.types.has_key('default'):
            possible_types['default'] = content.types['default']
        if content.types.has_key('selected'):
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
                    if content.type == 'image+text':
                        rw, rh, r = self.get_item_rectangle(ct.rectangle, ct.width,
                                                            max(ct.height,
                                                                int(ct.font.h * 1.1)))
                    else:
                        rw, rh, r = self.get_item_rectangle(ct.rectangle, ct.width,
                                                            ct.height)
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
            return True

        i = 0
        for choice in self.menuw.menu_items:
            try:
                if self.last_choices[1][i] != choice:
                    return True
                i += 1
            except IndexError:
                return True
            
        
    def update_content(self):
        """
        update the listing area
        """

        menuw     = self.menuw
        menu      = self.menu
        settings  = self.settings
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=True)

        cols, rows, hspace, vspace, hskip, vskip, width = \
              self.get_items_geometry(settings, menu, self.display_style)

        BOX_UNDER_ICON = self.xml_settings.box_under_icon

        if not len(menu.choices):
            val = content.types['default']
            self.drawstring(_('This directory is empty'), content.font, content)
            
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
            
        last_tvs      = ('', 0)
        all_tvs       = True
        tvs_shortname = True
                
        for choice in menuw.menu_items:
            if content.types.has_key( '%s selected' % choice.type ):
                s_val = content.types[ '%s selected' % choice.type ]
            else:
                s_val = content.types[ 'selected' ]

            if content.types.has_key( choice.type ):
                n_val = content.types[ choice.type ]
            else:
                n_val = content.types['default']
                

            if choice == menu.selected:
                val = s_val
            else:
                val = n_val
                
            text = choice.name
            if not text:
                text = "unknown"

            type_image = None
            if hasattr( val, 'icon' ):
                type_image = val.icon
                
            if not choice.icon and not type_image:
                if choice.type == 'playlist':
                    text = 'PL: %s' % text

                if choice.type == 'dir' and choice.parent and \
                   choice.parent.type != 'mediamenu':
                    text = '[%s]' % text

            if content.type == 'text':
                x0 = item_x0
                y0 = item_y0
                icon_x = 0
                image = None
                align = val.align or content.align
                
                if choice != menu.selected and hasattr( choice, 'outicon' ) and \
                       choice.outicon:
                    image = self.loadimage(choice.outicon, (vspace-content.spacing,
                                                            vspace-content.spacing))
                elif choice.icon:
                    image = self.loadimage(choice.icon, (vspace-content.spacing,
                                                         vspace-content.spacing))
                if not image and type_image:
                    image = self.loadimage( settings.icon_dir + '/' + type_image,
                                             ( vspace-content.spacing,
                                               vspace-content.spacing ) )
                x_icon = 0
                if image:
                    mx = x0
                    icon_x = vspace
                    x_icon = icon_x
                    if align == 'right':
                        # know how many pixels to offset (dammed negative and max+X
                        # values in (x,y,width) from skin!)
                        r1 = r2 = None
                        if s_val.rectangle:
                            r1 = self.get_item_rectangle(s_val.rectangle,
                                                         width, s_val.font.h)[2]
                        if n_val.rectangle:
                            r2 = self.get_item_rectangle(n_val.rectangle,
                                                         width, n_val.font.h)[2]
                        min_rx = 0
                        max_rw = width
                        if r1:
                            min_rx = min( min_rx, r1.x )
                            max_rw = max( max_rw, r1.width )
                        if r2:
                            min_rx = min( min_rx, r2.x )
                            max_rw = max( max_rw, r2.width )

                        mx = x0 + width + hskip + ( max_rw + min_rx - width ) - icon_x 
                        x_icon = 0
                    self.drawimage(image, (mx, y0))

                if val.rectangle:
                    r = self.get_item_rectangle(val.rectangle, width, val.font.h)[2]
                    self.drawroundbox(x0 + hskip + r.x + x_icon - BOX_UNDER_ICON * x_icon,
                                      y0 + vskip + r.y,
                                      r.width - icon_x + BOX_UNDER_ICON * icon_x,
                                      r.height, r)

                # special handling for tv shows
                if choice.type == 'video' and hasattr(choice,'tv_show') and \
                   choice.tv_show and (val.align=='left' or val.align=='') and \
                   (content.align=='left' or content.align==''):
                    sn = choice.show_name

                    if last_tvs[0] == sn[0]:
                        tvs_w = last_tvs[1]
                    else:
                        season  = 0
                        episode = 0
                        for c in menu.choices:
                            if c.type == 'video' and hasattr(c,'tv_show') and \
                               c.tv_show and c.show_name[0] == sn[0]:
                                # do not use val.font.stringsize because this will
                                # add shadow and outline values we add later for the
                                # normal text again. So just use val.font.font.stringsize
                                stringsize = val.font.font.stringsize
                                season  = max(season, stringsize(c.show_name[1]))
                                episode = max(episode, stringsize(c.show_name[2]))
                                if tvs_shortname and not c.image:
                                    tvs_shortname = False
                            else:
                                all_tvs = False

                        if all_tvs and not tvs_shortname and len(menu.choices) > 5:
                            tvs_shortname = True
                            
                        if all_tvs and tvs_shortname:
                            tvs_w = val.font.stringsize('x') + season + episode
                        else:
                            tvs_w = val.font.stringsize('%s x' % sn[0]) + season + episode
                        last_tvs = (sn[0], tvs_w)
                        
                    self.drawstring(' - %s' % sn[3], val.font, content,
                                    x=x0 + hskip + icon_x + tvs_w,
                                    y=y0 + vskip, width=width-icon_x-tvs_w, height=-1,
                                    align_h='left', dim=False, mode='hard')
                    self.drawstring(sn[2], val.font, content,
                                    x=x0 + hskip + icon_x + tvs_w - 100,
                                    y=y0 + vskip, width=100, height=-1,
                                    align_h='right', dim=False, mode='hard')
                    if all_tvs and tvs_shortname:
                        text = '%sx' % sn[1]
                    else:
                        text = '%s %sx' % (sn[0], sn[1])

                # if the menu has an attr table, the menu is a table. Each
                # item _must_ have that many tabs as the table needs!!!
                if hasattr(menu, 'table'):
                    table_x = x0 + hskip + x_icon
                    table_text = text.split('\t')
                    for i in range(len(menu.table)):
                        table_w = ((width-icon_x-len(table_text)*5)*menu.table[i]) / 100
                        if i != len(menu.table) - 1:
                            table_w += 5
                        x_mod = 0
                        if table_text[i].find('ICON_') == 0:
                            x_mod, table_text[i] = text_or_icon(settings, table_text[i],
                                                                table_x, table_w, val.font,
                                                                self.screen.renderer)
                            if not isstring(table_text[i]):
                                self.drawimage(table_text[i], (table_x + x_mod, y0 + vskip))
                                table_text[i] = ''
                                
                        if table_text[i]:
                            self.drawstring(table_text[i], val.font, content,
                                            x=table_x + x_mod,
                                            y=y0 + vskip, width=table_w, height=-1,
                                            align_h=val.align, mode='hard', dim=False)
                        table_x += table_w + 5

                else:
                    self.drawstring(text, val.font, content, x=x0 + hskip + x_icon,
                                    y=y0 + vskip, width=width-icon_x, height=-1,
                                    align_h=val.align, mode='hard', dim=True)


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
                    if content.type == 'image+text':
                        r = self.get_item_rectangle(val.rectangle, val.width,
                                                    max(rec_h, int(val.font.h * 1.1)))[2]
                    else:
                        r = self.get_item_rectangle(val.rectangle, val.width, rec_h)[2]
                    self.drawroundbox(x0 + r.x, y0 + r.y, r.width, r.height, r)

                image, i_w, i_h = format_image(self.screen.renderer, settings,
                                               choice, val.width, val.height, force=True)
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

                    if val.shadow and val.shadow.visible and image.get_alpha() == None:
                        box = self.drawroundbox(x0 + addx + val.shadow.x,
                                                y0 + addy + val.shadow.y,
                                                image.get_width(), image.get_height(),
                                                (val.shadow.color, 0, 0, 0))
                        box.position = 10
                        
                    self.drawimage(image, (x0 + addx, y0 + addy))
                        
                if content.type == 'image+text':
                    self.drawstring(choice.name, val.font, content, x=x0,
                                    y=y0 + val.height, width=val.width, height=-1,
                                    align_h=val.align, mode='hard', ellipses='', dim=False)
                    
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
                self.drawimage(area.images['uparrow'].filename, area.images['uparrow'])
            if menuw.menu_items[-1] != menu.choices[-1] and area.images['downarrow']:
                if isinstance(area.images['downarrow'].y, str):
                    v = copy.copy(area.images['downarrow'])
                    v.y = eval(v.y, {'MAX':(item_y0-vskip)})
                else:
                    v = area.images['downarrow']
                self.drawimage(area.images['downarrow'].filename, v)
        except:
            # empty menu / missing images
            pass
        
        self.last_choices = (menu.selected, copy.copy(menuw.menu_items))
