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
# Revision 1.10  2003/03/30 14:13:23  dischi
# (listing.py from prev. checkin has the wrong log message)
# o tvlisting now has left/right items and the label width is taken from the
#   skin xml file. The channel logos are scaled to fit that space
# o add image load function to area
# o add some few lines here and there to make it possible to force the
#   skin to a specific layout
# o initial display style is set to config.SKIN_START_LAYOUT
#
# Revision 1.9  2003/03/22 20:08:31  dischi
# Lots of changes:
# o blue2_big and blue2_small are gone, it's only blue2 now
# o Support for up/down arrows in the listing area
# o a sutitle area for additional title information (see video menu in
#   blue2 for an example)
# o some layout changes in blue2 (experimenting with the skin)
# o the skin searches for images in current dir, skins/images and icon dir
# o bugfixes
#
# Revision 1.8  2003/03/20 18:55:46  dischi
# Correct the rectangle drawing
#
# Revision 1.7  2003/03/19 11:00:31  dischi
# cache images inside the area and some bugfixes to speed up things
#
# Revision 1.6  2003/03/16 19:36:07  dischi
# Adjustments to the new xml_parser, added listing type 'image+text' to
# the listing area and blue2, added grey skin. It only looks like grey1
# in the menu. The skin inherits from blue1 and only redefines the colors
# and the fonts. blue2 now has an image view for the image menu.
#
# Revision 1.5  2003/03/15 11:08:40  dischi
# added channel logos
#
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
import config

osd = osd.get_singleton()

from area import Skin_Area, Geometry
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
        Skin_Area.__init__(self, 'listing', screen, imagecachesize=20)
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

        label_val    = content.types['label']
        head_val     = content.types['head']
        selected_val = content.types['selected']
        default_val  = content.types['default']

        self.all_vals = label_val, label_val.font, head_val, head_val.font, selected_val, \
                        selected_val.font, default_val, default_val.font
        
        font_h = max(selected_val.font.h, default_val.font.h, label_val.font.h)


        # get the max width needed for the longest channel name
        label_width = label_val.width

        #for channel in menuw.all_channels:
        #    label_width = max(label_width, osd.stringsize(channel.displayname,
        #                                                  label_val.font.name,
        #                                                  label_val.font.size)[0])

        label_txt_width = label_width

        if label_val.rectangle:
            r = self.get_item_rectangle(label_val.rectangle, label_width, label_val.font.h)[2]
            label_width = r.width
        else:
            label_width += content.spacing

        # get head height
        if head_val.rectangle:
            r = self.get_item_rectangle(head_val.rectangle, 20, head_val.font.h)[2]
            content_y = content.y + r.height + content.spacing
        else:
            content_y = content.y + head_val.font.h + content.spacing


        # get item height
        item_h = font_h

        if label_val.rectangle:
            r = self.get_item_rectangle(label_val.rectangle, 20, label_val.font.h)[2]
            item_h = max(item_h, r.height + content.spacing)
        if default_val.rectangle:
            r = self.get_item_rectangle(default_val.rectangle, 20, default_val.font.h)[2]
            item_h = max(item_h, r.height + content.spacing)
        if selected_val.rectangle:
            r = self.get_item_rectangle(selected_val.rectangle, 20, selected_val.font.h)[2]
            item_h = max(item_h, r.height + content.spacing)

        head_h = head_val.font.h
        if head_val.rectangle:
            r = self.get_item_rectangle(head_val.rectangle, 20, head_val.font.h)[2]
            head_h = max(head_h, r.height + content.spacing)

        content_h = content.height + content.y - content_y

        self.last_items_geometry = font_h, label_width, label_txt_width, content_y,\
                                   content_h / item_h, item_h, head_h

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

        font_h, label_width, label_txt_width, y0, num_rows, item_h, head_h = \
                self.get_items_geometry(settings, menu)

        label_val, label_font, head_val, head_font, selected_val, \
                   selected_font, default_val, default_font = self.all_vals


        leftarraw = None
        if area.images['leftarrow']:
            i = area.images['leftarrow']
            leftarrow = self.load_image(i.filename, i)
            if leftarrow:
                leftarrow_size = (leftarrow.get_width(), leftarrow.get_height())

        rightarraw = None
        if area.images['rightarrow']:
            i = area.images['rightarrow']
            rightarrow = self.load_image(i.filename, i)
            if rightarrow:
                rightarrow_size = (rightarrow.get_width(), rightarrow.get_height())

        x_contents = content.x + label_width + content.spacing
        w_contents = content.width - label_width - content.spacing

        for i in range(n_cols):
            x0 = int(x_contents + (float(w_contents) / n_cols) * i)
            x1 = int(x_contents + (float(w_contents) / n_cols) * (i+1))
            ty0 = content.y

            ig = Geometry(0, 0, x1-x0+1, head_h)
            if head_val.rectangle:
                ig, r = self.fit_item_in_rectangle(head_val.rectangle, x1-x0+1, head_h)
                self.drawroundbox(x0+r.x, ty0+r.y, r.width, r.height, r)
                
            self.write_text(time.strftime("%H:%M",time.localtime(to_listing[0][i+1])),
                            head_font, content, x=x0+ig.x,
                            y=ty0+ig.y, width=ig.width, height=-1,
                            align_v='center', align_h = head_val.align)

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

            logo_geo = [ tx0, ty0, label_width, font_h ]
            
            if label_val.rectangle:
                r = self.get_item_rectangle(label_val.rectangle,
                                            label_txt_width, font_h)[2]

                if r.x < 0:
                    tx0 -= r.x
                if r.y < 0:
                    ty0 -= r.y
                            
                self.drawroundbox(tx0 + r.x, ty0 + r.y, r.width, r.height, r)
                
                logo_geo =[ tx0+r.x+r.size, ty0+r.y+r.size, r.width-2*r.size,
                            r.height-2*r.size ]
                    

            channel_logo = config.TV_LOGOS + '/' + to_listing[i].id + '.png'
            if os.path.isfile(channel_logo):
                channel_logo = self.load_image(channel_logo, logo_geo[2:])
            else:
                channel_logo = None


            if channel_logo:
                self.draw_image(channel_logo, (logo_geo[0], logo_geo[1]))


            else:
                self.write_text(to_listing[i].displayname, label_font, content,
                                x=tx0, y=ty0, width=label_width, height=font_h)

            if to_listing[i].programs:
                for prg in to_listing[i].programs:
                    flag_left   = 0
                    flag_right  = 0

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

                    if x0 > x1:
                        break
                    
                    tx0 = x0
                    tx1 = x1
                    ty0 = y0

                    ig = Geometry(0, 0, tx1-tx0+1, item_h)
                    if val.rectangle:
                        ig, r = self.fit_item_in_rectangle(val.rectangle, tx1-tx0+1, item_h)
                        self.drawroundbox(tx0+r.x, ty0+r.y, r.width, r.height, r)
                        
                    if flag_left:
                        tx0 += leftarrow_size[0]
                        if tx0 < tx1:
                            self.draw_image(leftarrow, (tx0-leftarrow_size[0], ty0 + ig.y +\
                                                        (ig.height-leftarrow_size[1])/2))
                    if flag_right:
                        tx1 -= rightarrow_size[0]
                        if tx0 < tx1:
                            self.draw_image(rightarrow, (tx1, ty0 + ig.y + \
                                                         (ig.height-rightarrow_size[1])/2))

                    if tx0 < tx1:
                        self.write_text(prg.title, font, content, x=tx0+ig.x,
                                        y=ty0+ig.y, width=ig.width, height=-1,
                                        align_v='center', align_h = val.align)

            i += 1
            y0 += item_h - 1


        # print arrow:
        if menuw.display_up_arrow and area.images['uparrow']:
            self.draw_image(area.images['uparrow'].filename, area.images['uparrow'])
        if menuw.display_down_arrow and area.images['downarrow']:
            self.draw_image(area.images['downarrow'].filename, area.images['downarrow'])
