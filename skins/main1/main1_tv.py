#if 0 /*
# -----------------------------------------------------------------------
# main1_tv.py - skin TV support functions
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2002/11/24 06:32:01  krister
# Cleanup.
#
# Revision 1.9  2002/11/13 14:28:53  krister
# Fixed the channel logos to be sized better.
#
# Revision 1.8  2002/10/28 19:34:55  dischi
# The tv info area now shows info and description with the extra words info
# and description. The title will be writen in a larger font than the
# description. to_info now is a string (e.g. no data loaded) or a tuple
# (title, description)
#
# Revision 1.7  2002/10/24 04:33:25  gsbarbieri
# Modified to handle <head> from XML file.
#
# Revision 1.6  2002/10/21 20:30:50  dischi
# The new alpha layer support slows the system down. For that, the skin
# now saves the last background/alpha layer combination and can reuse it.
# It's quite a hack, the main skin needs to call drawroundbox in main1_utils
# to make the changes to the alpha layer. Look in the code, it's hard to
# explain, but IMHO it's faster now.
#
# Revision 1.5  2002/10/20 06:30:01  krister
# Fixed TV guide listing, draw border after icons.
#
# Revision 1.4  2002/10/19 15:09:55  dischi
# added alpha mask support
#
# Revision 1.3  2002/10/16 19:59:59  dischi
# use mode='soft' for drawstringframed for info
#
# Revision 1.2  2002/10/16 19:40:19  dischi
# Now the table looks ok for any height/font combination. Also fixed a
# float->int bug that caused one pixel spaces here and there. Some cleanups
#
# Revision 1.1  2002/10/16 04:58:16  krister
# Changed the main1 skin to use Gustavos new extended menu for TV guide, and Dischis new XML code. grey1 is now the default skin, I've tested all resolutions. I have not touched the blue skins yet, only copied from skin_dischi1 to skins/xml/type1.
#
# Revision 1.2  2002/08/14 04:33:54  krister
# Made more C-compatible.
#
# Revision 1.1  2002/08/03 07:59:15  krister
# Proposal for new standard fileheader.
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
# ----------------------------------------------------------------------- */
#endif

import sys, socket, random, time, os, copy, re
import config

from main1_utils import *

# The OSD class, used to communicate with the OSD daemon
import osd

# Create the OSD object
osd = osd.get_singleton()


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

class Skin_TV:

    tvguide_expand = 0

    def DrawTVGuide(self, settings):
        self.DrawTVGuide_Clear(settings)


    def DrawTVGuide_Clear(self, settings):

        InitScreen(settings, (settings.background.mask, ))

        # Show title and date
        s = time.strftime('%m/%d %H:%M')
        DrawTextFramed('TV Guide  -  %s' % s, settings.header)


    def DrawTVGuide_getExpand(self, settings):
        return self.tvguide_expand

    def DrawTVGuide_setExpand(self, expand, settings):
        self.tvguide_expand = expand

    def DrawTVGuide_View(self, to_view, settings):
        val = settings.view
        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)
        DrawTextFramed(to_view, val, x=val.x+val.spacing, y=val.y+val.spacing,
                       width=val.width-2*val.spacing, height=val.height-2*val.spacing)



    def DrawTVGuide_Info(self, to_info, settings):
        val = settings.info
        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)
        if isinstance(to_info, tuple):
            w,h = osd.stringsize(to_info[0], font=val.font, ptsize=val.size+3);
            DrawTextFramed(to_info[0], val, x=val.x+val.spacing, y=val.y+val.spacing,
                           width=val.width-2*val.spacing, height=h+5,
                           size=val.size+3, mode='soft')
            DrawTextFramed(to_info[1], val, x=val.x+val.spacing,
                           y=val.y+val.spacing+h+5,
                           width=val.width-2*val.spacing,
                           height=val.height-h+5-2*val.spacing, mode='soft')
        else:
            DrawTextFramed(to_info, val, x=val.x+val.spacing, y=val.y+val.spacing,
                           width=val.width-2*val.spacing, height=val.height-2*val.spacing,
                           mode='soft')



    def DrawTVGuide_ItemsPerPage(self, settings):
        items = -1
        val = settings.listing 

        str_w_label, str_h_label = osd.stringsize('Ajg', val.label.font, val.label.size)
        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max (str_h_label, str_h_selection, str_h_normal )

        if self.DrawTVGuide_getExpand(settings) == 0:
            height = val.height - str_h_label - 2 * val.spacing
        else:
            height = val.expand.height - str_h_label - 2 * val.spacing

        items = height / ( str_h + 2 * val.spacing )

        return int(items)


    def DrawTVGuide_Listing(self, to_listing, settings):
        val = settings.listing 

        if self.DrawTVGuide_getExpand(settings) == 0:
            conf_x = val.x
            conf_y = val.y
            conf_w = val.width
            conf_h = val.height
        else:
            conf_x = val.expand.x
            conf_y = val.expand.y
            conf_w = val.expand.width
            conf_h = val.expand.height


        str_w_label = str_h_label = 0
        str_w_selection = str_h_selection = 0
        str_w_normal = str_h_normal = 0
        val.left_arrow_size = val.right_arrow_size = (0, 0)
        n_cols = len(to_listing[0])-1
        col_time = 30

        str_w_label, str_h_label = osd.stringsize('Ajg', val.label.font, val.label.size)
        str_w_head, str_h_head = osd.stringsize('Ajg', val.head.font, val.head.size)
        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        left_arrow_size = osd.bitmapsize(val.left_arrow)
        right_arrow_size = osd.bitmapsize(val.right_arrow)


        y_contents = conf_y + str_h_label + 2 * val.spacing
        h_contents = conf_h - str_h_label - 2 * val.spacing
        x_contents = conf_x + val.label.width
        w_contents = conf_w - val.label.width

        col_size = int( w_contents / n_cols )


        # Display the Time on top
        x = conf_x
        y = conf_y
        # Display the Channel on top
        drawroundbox(x, y, x+val.label.width, y+str_h_head + 2 * val.spacing,
                     val.head.bgcolor, 1, val.border_color, radius=val.head.radius)
        settings2 = copy.copy(val.head)
        # first head column is date, should be aligned like 'label'
        settings2.align=val.label.align
        settings2.valign=val.label.valign
        DrawTextFramed(time.strftime("%m/%d",time.localtime(to_listing[0][1])),
                       settings2, x + val.spacing, y + val.spacing,
                       val.label.width - 2 * val.spacing, str_h_head)

        # other head columns should be aligned like specified in xml
        settings2.align=val.head.align
        settings2.valign=val.head.valign
        for i in range(n_cols):
            x0 = int(x_contents + (float(w_contents) / n_cols) * i)
            x1 = int(x_contents + (float(w_contents) / n_cols) * (i+1))
            
            drawroundbox(x0, y, x1, y+ str_h_head + 2 * val.spacing,
                         val.head.bgcolor, 1, val.border_color, radius=val.head.radius)   
            DrawTextFramed(time.strftime("%H:%M",time.localtime(to_listing[0][i+1])),
                           settings2, x0 + val.spacing, y + val.spacing, x1-x0, str_h_head)

        # define start and stop time
        date = time.strftime("%x", time.localtime())
        start_time = to_listing[0][1]
        stop_time = to_listing[0][-1]
        stop_time += (col_time*60)

        str_h = max( str_h_label, str_h_selection, str_h_normal )

        # 1 sec = x pixels
        prop_1sec = float(w_contents) / float(n_cols * col_time * 60) 

        # selected program:
        selected_prog = to_listing[1]

        items_per_page = self.DrawTVGuide_ItemsPerPage(settings)

        h = str_h
        for i in range(2,len(to_listing)):
            if i - 1 > items_per_page:
                break
            
            y0 = int(y_contents + (i-2) * (float(h_contents) / items_per_page))
            y1 = int(y_contents + (i-1) * (float(h_contents) / items_per_page))

            # draw the channel name/logo/id

            # Background color
            drawroundbox(conf_x, y0, conf_x+val.label.width, y1,
                         color=val.label.bgcolor, radius=val.label.radius)

            # Logo
            channel_logo = config.TV_LOGOS + '/' + to_listing[i].id + '.png'
            if not os.path.isfile(channel_logo):
                channel_logo = None

            logo_w, logo_h = 0, 0
            if channel_logo:
                # Get logo size
                logo_w, logo_h = osd.bitmapsize(channel_logo)
                # Resize according to the available height
                scalefac = float(y1 - y0 - 2) / logo_h
                logo_w = int(logo_w * scalefac)
                logo_h = int(logo_h * scalefac)
                osd.drawbitmap(util.resize(channel_logo, logo_w, logo_h),
                               conf_x + val.spacing, y0 + val.spacing +
                               (str_h - logo_h)/2)

            DrawTextFramed(to_listing[i].displayname, val.label,
                           conf_x + val.spacing + logo_w, y0 + val.spacing,
                           val.label.width - 2 * val.spacing - logo_h, str_h)

            # Border is drawn afterwards to delineate the icons
            drawroundbox(conf_x, y0, conf_x+val.label.width, y1, border_size=1,
                         color=val.border_color, radius=val.label.radius)

            if to_listing[i].programs:
                for prg in to_listing[i].programs:
                    x0 = 0
                    x1 = 0

                    w = 0
                    flag_left = 0
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

                        
                    val2 = copy.copy(val)
                    val2.selection = copy.copy(val.selection)

                    if prg.title == 'This channel has no data loaded':
                        val2.align='center'
                        val2.selection.align='center'

                    spacing = val2.spacing + 1

                    cur_val = val2

                    if prg.title == selected_prog.title and \
                       prg.channel_id == selected_prog.channel_id and \
                       prg.start == selected_prog.start and \
                       prg.stop == selected_prog.stop:

                        cur_val = val2.selection

                    drawroundbox(x0, y0, x1, y1, cur_val.bgcolor, 1, val2.border_color, radius=val2.radius)

                    tx0 = min(x1, x0+(flag_left+1)*spacing+flag_left*left_arrow_size[0])
                    tx1 = max(x0, x1-(flag_right+1)*spacing-flag_right*right_arrow_size[0])

                    DrawTextFramed(prg.title, cur_val, tx0, y0+spacing, tx1-tx0, h)

                    if flag_left:
                        osd.drawbitmap(val2.left_arrow, x0 + spacing,
                                       y0+spacing+int((str_h - left_arrow_size[1])/2))
                    if flag_right:
                        osd.drawbitmap(val2.right_arrow, x1-right_arrow_size[0]-spacing, \
                                       y0+spacing+int((str_h - right_arrow_size[1])/2))

            else:
                drawroundbox(x_contents, y0, x_contents+w_contents, y1,
                             val2.bgcolor, 1, val2.border_color, radius=val2.radius)
                DrawTextFramed('-[ NO DATA ]-', val, x_contents+val.spacing,
                               y0+val.spacing, w_contents - 2 * val2.spacing, h)


        # draw a border around the contents
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)

