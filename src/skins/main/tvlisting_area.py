#if 0
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
# Revision 1.12  2003/10/18 09:35:30  dischi
# handling to show scheduled recordings
#
# Revision 1.11  2003/09/21 18:19:36  dischi
# Oops. remove debug
#
# Revision 1.10  2003/09/21 18:18:31  dischi
# do not calc the arrows twice
#
# Revision 1.9  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.8  2003/09/13 10:08:23  dischi
# i18n support
#
# Revision 1.7  2003/09/07 15:43:06  dischi
# tv guide can now also have different styles
#
# Revision 1.6  2003/08/25 18:44:31  dischi
# Moved HOURS_PER_PAGE into the skin fxd file, default=2
#
# Revision 1.5  2003/08/24 16:36:25  dischi
# add support for y=max-... in listing area arrows
#
# Revision 1.4  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.3  2003/08/22 05:59:35  gsbarbieri
# Fixed some mistakes.
# Now it's possible to have more than one line for program/label, just make
# the height fit the number of wanted lines.
#
# Revision 1.2  2003/08/21 22:40:55  gsbarbieri
# Now left-top corner cell (date) use vertical padding from head and
# horizontal padding from label.
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

import time
import config
import math
from area import Skin_Area, Geometry
from skin_utils import *


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


    def get_items_geometry(self, settings, obj, display_style=0):
        if self.last_settings == settings:
            return self.last_items_geometry
        
        self.display_style = display_style
        self.init_vars(settings, None, widget_type = 'tv')

        menuw     = obj
        menu      = obj
        
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

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

        recordingshows = self.check_schedule()
        recnow = 0
        to_listing = menu.table

        n_cols = len(to_listing[0])-1
        col_time = 30

        font_h, label_width, label_txt_width, y0, num_rows, item_h, head_h = \
                self.get_items_geometry(settings, menu)[:-1]

        label_val, head_val, selected_val, default_val, scheduled_val = self.all_vals


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
            ig, r2 = self.fit_item_in_rectangle( head_val.rectangle, col_size, head_h )


        self.drawroundbox( x_contents - r.width, y_contents - r.height,
                           r.width+1, head_h+1, r )

        # use label padding for x; head padding for y
        self.write_text( time.strftime( dateformat, time.localtime( to_listing[ 0 ][ 1 ] ) ),
                         head_val.font, content,
                         x=( x_contents  - r.width + pad_x ),
                         y=( y_contents - r.height + ig.y ),
                         width=( r.width - 2 * pad_x ), height=-1,
                         align_v='center', align_h=head_val.align )



        # Print the time at the table's top
        x0 = x_contents
        ty0 = y_contents - r.height
        for i in range( n_cols ):
            self.drawroundbox( math.floor(x0), ty0,
                               math.floor( col_size + x0 ) - math.floor( x0 ) + 1,
                               head_h + 1, r2 )

            self.write_text( time.strftime( timeformat,
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

                self.drawroundbox(tx0 + r.x, ty0 + r.y, r.width+1, item_h, r)
                logo_geo =[ tx0+r.x+r.size, ty0+r.y+r.size, r.width-2*r.size,
                            r.height-2*r.size ]
                    

            channel_logo = config.TV_LOGOS + '/' + to_listing[i].id + '.png'
            if os.path.isfile(channel_logo):
                channel_logo = self.load_image(channel_logo, (r.width+1-2*r.size,
                                                              item_h-2*r.size))
            else:
                channel_logo = None


            if channel_logo:
                self.draw_image(channel_logo, (logo_geo[0], logo_geo[1]))


            else:
                self.write_text(to_listing[i].displayname, label_val.font, content,
                                x=tx0, y=ty0, width=r.width+2*r.x, height=item_h)

            self.drawroundbox(tx0 + r.x, ty0 + r.y, r.width+1, item_h, r)

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

                    # Not at all elegant.
                    # TODO:
                    #    * This is going to be SLOW for large schedules
                    #    * We should have a skin setting for recording background color
                    #    * I dunno what else.
                    #   I will work on this soon, but think of this as a proof of concept.
                    if recordingshows:
                        for recprogs in recordingshows:
                            if (prg.channel_id, prg.start, prg.stop) == recprogs:
                                val = selected_val

                    if prg.title == _('This channel has no data loaded'):
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
                        self.drawroundbox(tx0+r.x, ty0+r.y, r.width, item_h, r)
                        
                    if flag_left:
                        tx0 += leftarrow_size[0]
                        ig.width -= leftarrow_size[0]
                        if tx0 < tx1:
                            self.draw_image(leftarrow, (tx0-leftarrow_size[0], ty0 +\
                                                        (item_h-leftarrow_size[1])/2))
                    if flag_right:
                        tx1 -= rightarrow_size[0]
                        ig.width -= rightarrow_size[0]
                        if tx0 < tx1:
                            self.draw_image(rightarrow, (tx1, ty0 + \
                                                         (item_h-rightarrow_size[1])/2))

                    if tx0 < tx1:
                        self.write_text(prg.title, font, content, x=tx0+ig.x,
                                        y=ty0+ig.y, width=ig.width,
                                        height=item_h - 2 * ig.y,
                                        align_v='center', align_h = val.align)

            i += 1
            y0 += item_h - 1


        # print arrow:
        if menuw.display_up_arrow and area.images['uparrow']:
            self.draw_image(area.images['uparrow'].filename, area.images['uparrow'])
        if menuw.display_down_arrow and area.images['downarrow']:
            if isinstance(area.images['downarrow'].y, str):
                v = copy.copy(area.images['downarrow'])
                MAX=y0
                v.y = eval(v.y)
            else:
                v = area.images['downarrow']
            self.draw_image(area.images['downarrow'].filename, v)

        
    def check_schedule (self):

        SCHEDULE = config.REC_SCHEDULE_FILE
        if not os.path.isfile(SCHEDULE):
            return None
        fd = open(SCHEDULE, 'r')
        schedule = fd.readlines()
        fd.close()
        recordingshows = []

        for s in schedule[1:]:
            if s[0] == '#':
                continue

            vals = s.strip().split(',')

            try:
                start_time = time.mktime(time.strptime(vals[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                continue
            stop_time = start_time+int(vals[1])
            if (time.localtime()[8]==1): # IF daylight savings time in effect
                start_time = start_time-3600
                stop_time = stop_time-3600

            channel_id = vals[3]
            recordingshows.append((channel_id,start_time,stop_time))
        
        return recordingshows
