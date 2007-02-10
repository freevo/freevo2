# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tvlisting_area.py - A listing area for the tv guide
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the TVListingArea for the tv guide.
#
# TODO: o do not redraw everything
#       o add doc
#       o huge cleanup
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Gustavo Sverzut Barbieri <gsbarbieri@yahoo.com.br>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'TvlistingArea' ]


import copy
import os
import math
import time
from freevo.ui.config import config
from freevo.ui.gui import imagelib

# kaa imports
import kaa.epg

# freevo core imports
import freevo.ipc

from area import Area
from freevo.ui.gui.widgets import Rectangle

import logging
log = logging.getLogger('gui')

class _Geometry(object):
    """
    Simple object with x, y, with, height values
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height

    def __str__(self):
        return '_Geometry: %s,%s %sx%s' % \
               (self.x, self.y, self.width, self.height)


class TvlistingArea(Area):
    """
    this call defines the listing area
    """

    def __init__(self):

        Area.__init__(self, 'listing')
        self.last_choices = ( None, None )
        self.last_settings = None
        self.last_items_geometry = None
        self.last_start_time = 0
        self.last_channels = None

        # TODO: it is ugly keeping a list of channels everywhere
        #       it may be best to handle this in the guide object or
        #       in the freevo epg module (there we can use config items
        #       to determine sort order.
        self.channels = kaa.epg.get_channels(sort=True)

        # objects on the area
        self.chan_obj   = []
        self.time_obj   = []
        self.up_arrow   = None
        self.down_arrow = None
        self.objects    = []
        self.background = None


    def __calc_items_geometry(self):
        # get the settings
        settings = self.settings

        # get all values for the different types
        label_val     = settings.types['label']
        head_val      = settings.types['head']
        selected_val  = settings.types['selected']
        default_val   = settings.types['default']
        scheduled_val = settings.types['scheduled']
        conflict_val  = settings.types['conflict']

        self.all_vals = label_val, head_val, selected_val, default_val, \
                        scheduled_val, conflict_val

        # get max font height
        font_h = max(selected_val.font.height, default_val.font.height,
                     label_val.font.height, conflict_val.height)


        # get label width
        label_width = label_val.width
        if label_val.rectangle:
            r = label_val.rectangle.calculate(label_width,
                                              label_val.font.height)[2]
            label_width = r.width
        else:
            label_width += settings.spacing


        # get headline height
        head_h = head_val.font.height
        if head_val.rectangle:
            r = head_val.rectangle.calculate(20, head_val.font.height)[2]
            head_h = max(head_h, r.height + settings.spacing)
            settings_y = settings.y + r.height + settings.spacing
        else:
            settings_y = settings.y + head_val.font.height + settings.spacing


        # get item height
        item_h = font_h
        for val in (label_val, default_val, selected_val, conflict_val):
            if val.rectangle:
                r = val.rectangle.calculate(20, val.font.height)[2]
                item_h = max(item_h, r.height + settings.spacing)

        num_rows = (settings.height + settings.y - settings_y) / item_h
        return font_h, label_width, settings_y, num_rows, item_h, head_h



    def __fit_in_rect(self, rectangle, width, height, font_h):
        """
        calculates the rectangle geometry and fits it into the area
        """
        x = 0
        y = 0
        r = rectangle.calculate(width, font_h)[2]
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
        return _Geometry(x, y, width, height), r


    def clear(self):
        for o in self.objects + self.chan_obj + self.time_obj:
            if o:
                o.unparent()
        for o in ('background', 'up_arrow', 'down_arrow'):
            if getattr(self, o):
                getattr(self, o).unparent()
            setattr(self, o, None)
        self.objects  = []
        self.chan_obj = []
        self.time_obj = []
        self.last_channels = None


    def __draw_time_line(self, start_time, settings, col_time, x0, y0,
                         n_cols, col_size, height):
        if self.last_start_time == start_time and self.time_obj:
            return
        for o in self.time_obj:
            if o:
                o.unparent()
        timeformat = config.tv.timeformat
        if not timeformat:
            timeformat = '%H:%M'
        head_val = self.all_vals[1]

        geo = _Geometry( 0, 0, col_size, height )
        if head_val.rectangle:
            geo, rect = self.__fit_in_rect( head_val.rectangle,
                                            col_size, height, height )

        for i in range( n_cols ):
            if head_val.rectangle:
                width = int(math.floor(col_size + x0) - math.floor( x0 ) + 1)
                self.time_obj.append(self.drawbox(int(math.floor(x0)), y0,
                                                  width, height + 1, rect))

            t_str = time.strftime( timeformat,
                                   time.localtime(start_time + col_time*i*60 ))
            self.time_obj.append(self.drawstring( t_str ,
                                                 head_val.font, settings,
                                                 x=( x0 + geo.x ),
                                                 y=( y0 + geo.y ),
                                                 width=geo.width, height=-1,
                                                 align_v='center',
                                                 align_h=head_val.align))
            x0 += col_size




    def __draw_channel_list(self, channel_list, settings, y0, width, item_h,
                            font_h):
        for o in self.chan_obj:
            if o:
                o.unparent()
        self.chan_obj = []

        label_val = self.all_vals[0]
        for channel in channel_list:
            ty0 = y0
            tx0 = settings.x

            logo_geo = [ tx0, ty0, width, font_h ]

            if label_val.rectangle:
                r = label_val.rectangle.calculate(width, item_h)[2]
                if r.x < 0:
                    tx0 -= r.x
                if r.y < 0:
                    ty0 -= r.y

                self.chan_obj.append(self.drawbox(tx0 + r.x, ty0 + r.y,
                                                  r.width+1, item_h, r))
                logo_geo =[ tx0+r.x+r.size, ty0+r.y+r.size, r.width-2*r.size,
                            r.height-2*r.size ]


            self.chan_obj.append(self.drawstring(channel.name,
                                                 label_val.font,
                                                 settings, x=tx0, y=ty0,
                                                 width=r.width+2*r.x,
                                                 height=item_h))

            self.chan_obj.append(self.drawbox(tx0 + r.x, ty0 + r.y,
                                              r.width+1, item_h, r))
            y0 += item_h - 1


    def update(self):
        """
        update the listing area
        """
        menu      = self.menu
        settings  = self.settings

        # get tvserver interface
        tvserver = freevo.ipc.Instance('freevo').tvserver

        # FIXME: move to skin
        n_cols   = 4
        col_time = 30

        if not self.channels:
            # FIXME: why?
            self.channels = kaa.epg.get_channels(sort=True)
            
        if self.last_settings == self.settings:
            # same layout, only clean 'objects'
            for o in self.objects:
                if o: o.unparent()
            self.objects = []
            # get last geometry values
            geometry = self.last_items_geometry
        else:
            # layout change, clean everything
            self.clear()
            # calculate new geometry values
            geometry = self.__calc_items_geometry()
            # save everything for later use
            self.last_settings = self.settings
            self.last_items_geometry = geometry

        # split geometry
        font_h, label_width, y0, num_rows, item_h, head_h = geometry

        # get all 'val's
        label_val, head_val, selected_val, default_val, \
                   scheduled_val, conflict_val = self.all_vals

        leftarrow = None
        leftarrow_size = (0,0)

        # FIXME: there is no self.loadimage anymore
        # if area.images['leftarrow']:
        #     i = area.images['leftarrow']
        #     leftarrow = self.loadimage(i.filename, i)
        #     if leftarrow:
        #         leftarrow_size = (leftarrow.get_width(), \
        #                   leftarrow.get_height())

        rightarrow = None
        rightarrow_size = (0,0)

        # FIXME: there is no self.loadimage anymore
        # if area.images['rightarrow']:
        #     i = area.images['rightarrow']
        #     rightarrow = self.loadimage(i.filename, i)
        #     if rightarrow:
        #         rightarrow_size = (rightarrow.get_width(),
        #                        rightarrow.get_height())

        # Print the Date of the current list page
        dateformat = config.tv.dateformat
        if not dateformat:
            dateformat = '%e-%b'

        r = _Geometry(0, 0, label_width, font_h)
        if label_val.rectangle:
            r = label_val.rectangle.calculate( label_width, head_h )[ 2 ]

        chan_x = settings.x + settings.spacing + r.width
        chan_w = settings.width - 2 * settings.spacing - r.width

        timer_y = settings.y + settings.spacing

        # 1 sec = x pixels
        prop_1sec = float(chan_w) / float(n_cols * col_time * 60)
        col_size = prop_1sec * 1800 # 30 minutes

        if not self.background:
            self.background = self.drawbox(chan_x - r.width, timer_y,
                                           r.width+1, head_h+1, r)

        start_time = self.last_start_time
        if menu.selected.start == 0:
            if self.last_start_time:
                start_time = self.last_start_time
            else:
                t = list(time.localtime())
                t[4] = t[5] = 0
                start_time = int(time.mktime(t))
                
        elif menu.selected.start < self.last_start_time:
            if menu.selected.stop < self.last_start_time + \
                   (n_cols - 2) * col_time * 60:
                start_time = menu.selected.start / (60 * col_time) * \
                             (60 * col_time)

        elif menu.selected.start > self.last_start_time + (n_cols - 2) * \
                 col_time * 60:
            start_time = menu.selected.start / (60 * col_time) * \
                         (60 * col_time)

        # Print the time at the table's top
        self.__draw_time_line(start_time, settings, col_time, chan_x,
                              timer_y, n_cols, col_size, head_h)

        self.last_start_time = start_time
        stop_time  = start_time + col_time * n_cols * 60

        # get selected program and channel list:
        selected_prog = menu.selected
        start_channel = self.channels.index(menu.channel)/num_rows*num_rows
        channel_list  = self.channels[start_channel:start_channel+num_rows]

        # draw the channel list
        if self.last_channels != channel_list:
            self.__draw_channel_list(channel_list, settings, y0, label_width,
                                     item_h, font_h)
        self.last_channels = channel_list

        for channel in channel_list:
            try:
                #for prg in channel[start_time:stop_time]:
                for prg in kaa.epg.search(channel=channel, time=(start_time, stop_time)):
                    flag_left   = 0
                    flag_right  = 0

                    if prg.start < start_time:
                        flag_left = 1
                        x0 = chan_x
                        t_start = start_time
                    else:
                        x0 = chan_x+int(float(prg.start-start_time)*prop_1sec)
                        t_start = prg.start

                    if prg.stop > stop_time:
                        flag_right = 1
                        x1 = chan_x + chan_w
                    else:
                        x1 = chan_x + int(float(prg.stop-start_time)*prop_1sec)

                    if x0 > x1:
                        continue

                    if prg == selected_prog:
                        val = selected_val
                    else:
                        rs = tvserver.recordings.get(prg.channel.name, prg.start,
                                                     prg.stop)
                        if rs and rs.status in (tvserver.SCHEDULED, tvserver.RECORDING,
                                                tvserver.SAVED):
                            val = scheduled_val
                        elif rs and rs.status == tvserver.CONFLICT:
                            val = conflict_val
                        else:
                            val = default_val

                    # calc the geometry values
                    ig = _Geometry(0, 0, x1-x0+1, item_h)
                    if val.rectangle:
                        ig, r = self.__fit_in_rect(val.rectangle, x1-x0+1,
                                                   item_h, font_h)
                        box = self.drawbox(x0+r.x, y0+r.y, r.width, item_h, r)
                        self.objects.append(box)

                    # draw left flag and reduce width and add to x0
                    if flag_left:
                        x0 += leftarrow_size[0]
                        ig.width -= leftarrow_size[0]
                        if x0 < x1:
                            y = y0 + (item_h-leftarrow_size[1])/2
                            x = x0 - leftarrow_size[0]
                            image = self.drawimage(leftarrow, (x, y))
                            if image:
                                self.objects.append(d_i)

                    # draw right flag and reduce width and x1
                    if flag_right:
                        x1 -= rightarrow_size[0]
                        ig.width -= rightarrow_size[0]
                        if x0 < x1:
                            y = y0 + (item_h-rightarrow_size[1])/2
                            image = self.drawimage(rightarrow, (x1, y))
                            if image:
                                self.objects.append(image)

                    # draw the text
                    if x0 < x1:
                        txt = self.drawstring(prg.title, val.font, settings,
                                              x0+ig.x, y0+ig.y, ig.width,
                                              ig.height, 'center', val.align)
                        if txt:
                            self.objects.append(txt)
            except:
                log.exception('tv_listing')
            y0 += item_h - 1


        if start_channel > 0 and settings.images['uparrow']:
            # up arrow needed
            if not self.up_arrow:
                ifile = settings.images['uparrow'].filename
                self.up_arrow = self.drawimage(ifile,
                                               settings.images['uparrow'])
        elif self.up_arrow:
            # no arrow needed but on the screen, remove it
            self.up_arrow.unparent()
            self.up_arrow = None

        if len(self.channels) >= start_channel+num_rows and \
               settings.images['downarrow']:
            if not self.down_arrow:
                # down arrow needed
                if isinstance(settings.images['downarrow'].y, str):
                    v = copy.copy(settings.images['downarrow'])
                    v.y = eval(v.y, {'MAX' : y0})
                else:
                    v = settings.images['downarrow']
                fname = settings.images['downarrow'].filename
                self.down_arrow = self.drawimage(fname, v)
        elif self.down_arrow:
            # no arrow needed but on the screen, remove it
            self.down_arrow.unparent()
            self.down_arrow = None
