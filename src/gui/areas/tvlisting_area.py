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
# Revision 1.2  2004/07/24 17:49:05  dischi
# interface cleanup
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.22  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.21  2004/03/14 17:22:47  dischi
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

import time
import config
import math
from area import Skin_Area, Geometry
from skin_utils import *


class TVListing_Area(Skin_Area):
    """
    this call defines the listing area
    """

    def __init__(self):
        Skin_Area.__init__(self, 'listing', imagecachesize=20)
        self.last_choices = ( None, None )
        self.last_settings = None
        self.last_items_geometry = None
        
    def update_content_needed(self):
        """
        check if the content needs an update
        """
        return True


    def get_items_geometry(self, settings, obj, display_style=0):
        if self.last_settings == settings:
            return self.last_items_geometry
        
        self.display_style = display_style
        self.init_vars(settings, None, widget_type = 'tv')

        menuw     = obj
        menu      = obj
        
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=True)

        label_val     = content.types['label']
        head_val      = content.types['head']
        selected_val  = content.types['selected']
        default_val   = content.types['default']
        scheduled_val = content.types['scheduled']

        self.all_vals = label_val, head_val, selected_val, default_val, scheduled_val
        
        font_h = max(selected_val.font.h, default_val.font.h, label_val.font.h)


        # get the max width needed for the longest channel name
        label_width = label_val.width

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
                                   content_h / item_h, item_h, head_h, \
                                   content.hours_per_page
        return self.last_items_geometry
    
        

    def fit_item_in_rectangle(self, rectangle, width, height, font_h):
        """
        calculates the rectangle geometry and fits it into the area
        """
        x = 0
        y = 0
        r = self.get_item_rectangle(rectangle, width, font_h)[2]
        if r.width > width:
            r.width, width = width, width - (r.width - width)
        if r.height > height:
            r.height, height = height, height - (r.height - height)
        if r.x < 0:
            r.x, x = 0, -r.x
            width -= x
        if r.y < 0:
            r.y, y = 0, -r.y
            height -= y
        return Geometry(x, y, width, height), r
    

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

        to_listing     = menu.table

        n_cols   = len(to_listing[0])-1
        col_time = 30

        font_h, label_width, label_txt_width, y0, num_rows, item_h, head_h = \
                self.get_items_geometry(settings, menu)[:-1]

        label_val, head_val, selected_val, default_val, scheduled_val = self.all_vals

        leftarrow = None
        if area.images['leftarrow']:
            i = area.images['leftarrow']
            leftarrow = self.loadimage(i.filename, i)
            if leftarrow:
                leftarrow_size = (leftarrow.get_width(), leftarrow.get_height())

        rightarrow = None
        if area.images['rightarrow']:
            i = area.images['rightarrow']
            rightarrow = self.loadimage(i.filename, i)
            if rightarrow:
                rightarrow_size = (rightarrow.get_width(), rightarrow.get_height())


        x_contents = content.x + content.spacing
        y_contents = content.y + content.spacing
        
        w_contents = content.width  - 2 * content.spacing
        h_contents = content.height - 2 * content.spacing

        # Print the Date of the current list page
        dateformat = config.TV_DATEFORMAT
        timeformat = config.TV_TIMEFORMAT
        if not timeformat:
            timeformat = '%H:%M'
        if not dateformat:
            dateformat = '%e-%b'

        r = Geometry( 0, 0, label_width, font_h )
        if label_val.rectangle:
            r = self.get_item_rectangle( label_val.rectangle, label_width, head_h )[ 2 ]
            pad_x = 0
            pad_y = 0
            if r.x < 0: pad_x = -1 * r.x
            if r.y < 0: pad_y = -1 * r.y

        x_contents += r.width
        y_contents += r.height
        w_contents -= r.width
        h_contents -= r.width

        # 1 sec = x pixels
        prop_1sec = float(w_contents) / float(n_cols * col_time * 60)
        col_size = prop_1sec * 1800 # 30 minutes


        ig = Geometry( 0, 0, col_size, head_h )
        if head_val.rectangle:
            ig, r2 = self.fit_item_in_rectangle( head_val.rectangle, col_size,
                                                 head_h, head_h )


        self.drawbox( x_contents - r.width, y_contents - r.height,
                      r.width+1, head_h+1, r )

        # use label padding for x; head padding for y
        self.drawstring( time.strftime( dateformat, time.localtime( to_listing[ 0 ][ 1 ] ) ),
                         head_val.font, content,
                         x=( x_contents  - r.width + pad_x ),
                         y=( y_contents - r.height + ig.y ),
                         width=( r.width - 2 * pad_x ), height=-1,
                         align_v='center', align_h=head_val.align )



        # Print the time at the table's top
        x0 = x_contents
        ty0 = y_contents - r.height
        for i in range( n_cols ):
            self.drawbox( math.floor(x0), ty0,
                          math.floor( col_size + x0 ) - math.floor( x0 ) + 1,
                          head_h + 1, r2 )

            self.drawstring( time.strftime( timeformat,
                                            time.localtime( to_listing[ 0 ][ i + 1 ] ) ),
                             head_val.font, content,
                             x=( x0 + ig.x ), y=( ty0 + ig.y ),
                             width=ig.width, height=-1,
                             align_v='center', align_h=head_val.align)
            x0 += col_size

        # define start and stop time
        date = time.strftime("%x", time.localtime())
        start_time = to_listing[0][1]
        stop_time = to_listing[0][-1]
        stop_time += (col_time*60)

        # selected program:
        selected_prog = to_listing[1]

        for i in range(2,len(to_listing)):
            ty0 = y0
            tx0 = content.x

            logo_geo = [ tx0, ty0, label_width, font_h ]
            
            if label_val.rectangle:
                r = self.get_item_rectangle(label_val.rectangle, label_width, item_h)[2]
                if r.x < 0:
                    tx0 -= r.x
                if r.y < 0:
                    ty0 -= r.y
                            
                val = default_val

                self.drawbox(tx0 + r.x, ty0 + r.y, r.width+1, item_h, r)
                logo_geo =[ tx0+r.x+r.size, ty0+r.y+r.size, r.width-2*r.size,
                            r.height-2*r.size ]
                    

            channel_logo = config.TV_LOGOS + '/' + to_listing[i].id + '.png'
            if os.path.isfile(channel_logo):
                channel_logo = self.loadimage(channel_logo, (r.width+1-2*r.size,
                                                              item_h-2*r.size))
            else:
                channel_logo = None


            if channel_logo:
                self.drawimage(channel_logo, (logo_geo[0], logo_geo[1]))


            else:
                self.drawstring(to_listing[i].displayname, label_val.font, content,
                                x=tx0, y=ty0, width=r.width+2*r.x, height=item_h)

            self.drawbox(tx0 + r.x, ty0 + r.y, r.width+1, item_h, r)

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

                    elif prg.scheduled:
                        val = scheduled_val
                    else:
                        val = default_val

                    font = val.font

                    try:
                        if prg.title == _('This channel has no data loaded'):
                            val = copy.copy(val)
                            val.align='center'
                    except UnicodeError:
                        pass
                    
                    if x0 > x1:
                        break

                    # text positions
                    tx0 = x0
                    tx1 = x1
                    ty0 = y0

                    # calc the geometry values
                    ig = Geometry(0, 0, tx1-tx0+1, item_h)
                    if val.rectangle:
                        ig, r = self.fit_item_in_rectangle(val.rectangle, tx1-tx0+1,
                                                           item_h, font_h)
                        self.drawbox(tx0+r.x, ty0+r.y, r.width, item_h, r)

                    # draw left flag and reduce width and add to x0
                    if flag_left:
                        tx0      += leftarrow_size[0]
                        ig.width -= leftarrow_size[0]
                        if tx0 < tx1:
                            self.drawimage(leftarrow, (tx0-leftarrow_size[0], ty0 +\
                                                       (item_h-leftarrow_size[1])/2))

                    # draw right flag and reduce width and x1
                    if flag_right:
                        tx1      -= rightarrow_size[0]
                        ig.width -= rightarrow_size[0]
                        if tx0 < tx1:
                            self.drawimage(rightarrow,
                                           (tx1, ty0 + (item_h-rightarrow_size[1])/2))

                    # draw the text
                    if tx0 < tx1:
                        self.drawstring(prg.title, font, content, x=tx0+ig.x,
                                        y=ty0+ig.y, width=ig.width, height=ig.height,
                                        align_v='center', align_h = val.align)

            i += 1
            y0 += item_h - 1


        # print arrow:
        if menuw.display_up_arrow and area.images['uparrow']:
            self.drawimage(area.images['uparrow'].filename, area.images['uparrow'])
        if menuw.display_down_arrow and area.images['downarrow']:
            if isinstance(area.images['downarrow'].y, str):
                v = copy.copy(area.images['downarrow'])
                v.y = eval(v.y, {'MAX' : y0})
            else:
                v = area.images['downarrow']
            self.drawimage(area.images['downarrow'].filename, v)

