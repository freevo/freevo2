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
# Revision 1.4  2003/03/14 19:29:07  dischi
# some position fixes
#
# Revision 1.3  2003/03/13 21:02:08  dischi
# misc cleanups
#
# Revision 1.2  2003/03/08 19:54:41  dischi
# make it look nicer
#
# Revision 1.1  2003/03/08 17:36:15  dischi
# A listing area for the tv listing
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
import pygame
import time

osd = osd.get_singleton()

from area import Skin_Area
from skin_utils import *


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class TVListing_Area(Skin_Area):
    """
    this call defines the listing area
    """

    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'listing', screen)
        self.last_choices = ( None, None )
        self.last_settings = None
        self.last_items_geometry = None
        
    def update_content_needed(self):
        """
        check if the content needs an update
        """
        return TRUE


    def get_items_geometry(self, settings, obj):
        if self.last_settings == settings:
            return self.last_items_geometry
        
        self.init_vars(settings, None, widget_type = 'tv')

        menuw     = obj
        menu      = obj
        
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        label_val  = content.types['label']
        label_font = settings.font[label_val.font]

        head_val  = content.types['head']
        head_font = settings.font[head_val.font]

        selected_val  = content.types['selected']
        selected_font = settings.font[selected_val.font]

        default_val  = content.types['default']
        default_font = settings.font[default_val.font]

        self.all_vals = label_val, label_font, head_val, head_font, selected_val, \
                        selected_font, default_val, default_font
        
        font_h = max(selected_font.h, default_font.h, label_font.h)


        # get the max width needed for the longest channel name
        label_width = 0
        for channel in menuw.all_channels:
            label_width = max(label_width, osd.stringsize(channel.displayname,
                                                          label_font.name,
                                                          label_font.size)[0])
        label_txt_width = label_width

        if label_val.rectangle:
            r = self.get_item_rectangle(label_val.rectangle, label_width, label_font.h)[2]
            label_width = r.width
        else:
            label_width += content.spacing


        # get head height
        if head_val.rectangle:
            r = self.get_item_rectangle(head_val.rectangle, 20, head_font.h)[2]
            content_y = content.y + r.height + content.spacing
        else:
            content_y = content.y + head_font.h + content.spacing


        # get item height
        item_h = font_h

        if label_val.rectangle:
            r = self.get_item_rectangle(label_val.rectangle, 20, label_font.h)[2]
            item_h = max(item_h, r.height + content.spacing)
        if default_val.rectangle:
            r = self.get_item_rectangle(default_val.rectangle, 20, default_font.h)[2]
            item_h = max(item_h, r.height + content.spacing)
        if selected_val.rectangle:
            r = self.get_item_rectangle(selected_val.rectangle, 20, selected_font.h)[2]
            item_h = max(item_h, r.height + content.spacing)

        content_h = content.height + content.y - content_y

        self.last_items_geometry = font_h, label_width, label_txt_width, content_y,\
                                   content_h / item_h, item_h

        return self.last_items_geometry
    
        
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

        to_listing = menu.table

        n_cols = len(to_listing[0])-1
        col_time = 30

        font_h, label_width, label_txt_width, y0, num_rows, item_h = \
                self.get_items_geometry(settings, menu)

        label_val, label_font, head_val, head_font, selected_val, \
                   selected_font, default_val, default_font = self.all_vals

        
        #left_arrow_size = osd.bitmapsize(val.indicator['left'])
        #right_arrow_size = osd.bitmapsize(val.indicator['right'])

        left_arrow_size = (0,0)
        right_arrow_size = (0,0)

        # col_size = int( w_contents / n_cols )

        # Display the Time on top
        #x = conf_x
        #y = conf_y

        # Display the Channel on top
        #drawroundbox(x, y, x+val.label.width, y+str_h_head + 2 * val.spacing,
        #             val.head.bgcolor, 1, val.border_color, radius=val.head.radius)
        #settings2 = copy.copy(val.head)
        # first head column is date, should be aligned like 'label'
        #settings2.align=val.label.align
        #settings2.valign=val.label.valign
        #DrawTextFramed(time.strftime("%m/%d",time.localtime(to_listing[0][1])),
        #               settings2, x + val.spacing, y + val.spacing,
        #               val.label.width - 2 * val.spacing, str_h_head)

        # other head columns should be aligned like specified in xml

        x_contents = content.x + label_width + content.spacing
        w_contents = content.width - label_width - content.spacing

        for i in range(n_cols):
            x0 = int(x_contents + (float(w_contents) / n_cols) * i)
            x1 = int(x_contents + (float(w_contents) / n_cols) * (i+1))
            ty0 = content.y
           
            if head_val.rectangle:
                r = self.get_item_rectangle(head_val.rectangle, x1-x0, head_font.h)[2]
                if r.x < 0:
                    x0 -= r.x
                if r.y < 0:
                    ty0 -= r.y
                self.drawroundbox(x0 + r.x, ty0 + r.y, r.width, r.height, r)
                
            self.write_text(time.strftime("%H:%M",time.localtime(to_listing[0][i+1])),
                            head_font, content, x=x0, y=ty0, width=x1-x0, height=-1)

        
        # define start and stop time
        date = time.strftime("%x", time.localtime())
        start_time = to_listing[0][1]
        stop_time = to_listing[0][-1]
        stop_time += (col_time*60)

        # 1 sec = x pixels
        prop_1sec = float(w_contents) / float(n_cols * col_time * 60) 

        # selected program:
        selected_prog = to_listing[1]

        for i in range(2,len(to_listing)):
            ty0 = y0
            tx0 = content.x
            if label_val.rectangle:
                r = self.get_item_rectangle(label_val.rectangle,
                                            label_txt_width, font_h)[2]
                    
                if r.x < 0:
                    tx0 -= r.x
                if r.y < 0:
                    ty0 -= r.y
                            
                self.drawroundbox(tx0 + r.x, ty0 + r.y, r.width, r.height, r)
                
            self.write_text(to_listing[i].displayname, label_font, content,
                            x=tx0, y=ty0, width=label_width, height=font_h)

            if to_listing[i].programs:
                for prg in to_listing[i].programs:
                    flag_left  = 0
                    flag_right = 0

                    if prg.start < start_time:
                        flag_left = 1
                        x0 = x_contents
                        t_start = start_time
                    else:
                        x0 = x_contents + int(float(prg.start-start_time) * prop_1sec)
                        t_start = prg.start

                    if prg.stop > stop_time:
                        flag_right = 1
                        w = w_contents + x_contents - x0                        
                        x1 = x_contents + w_contents
                    else:
                        w =  int( float(prg.stop - t_start) * prop_1sec )
                        x1 = x_contents + int(float(prg.stop-start_time) * prop_1sec)


                    if prg.title == selected_prog.title and \
                       prg.channel_id == selected_prog.channel_id and \
                       prg.start == selected_prog.start and \
                       prg.stop == selected_prog.stop:

                        val = selected_val
                        font = selected_font

                    else:
                        val = default_val
                        font = default_font

                    if prg.title == 'This channel has no data loaded':
                        val = copy.copy(val)
                        val.align='center'

                    #tx0 = min(x1, x0+(flag_left+1)*spacing+flag_left*left_arrow_size[0])
                    #tx1 = max(x0, x1-(flag_right+1)*spacing-flag_right*right_arrow_size[0])

                    tx0 = min(x1, x0)
                    tx1 = max(x0, x1)

                    ty0 = y0
                    
                    if val.rectangle:
                        r = self.get_item_rectangle(val.rectangle, tx1-tx0, font_h)[2]
                        if r.x < 0:
                            tx0 -= r.x
                        if r.y < 0:
                            ty0 -= r.y
                            
                        self.drawroundbox(tx0+r.x, ty0+r.y, r.width, r.height, r)
                        
                    self.write_text(prg.title, font, content, x=tx0,
                                    y=ty0, width=tx1-tx0, height=font_h,
                                    align_v='center', align_h = val.align)

                    #if flag_left:
                    #    osd.drawbitmap(val2.indicator['left'], x0 + spacing,
                    #                   y0+spacing+int((str_h - left_arrow_size[1])/2))
                    #if flag_right:
                    #    osd.drawbitmap(val2.indicator['right'],
                    #                   x1-right_arrow_size[0]-spacing, \
                    #                   y0+spacing+int((str_h - right_arrow_size[1])/2))

            i += 1
            y0 += item_h - 1
        return
