#if 0 /*
# -----------------------------------------------------------------------
# main1_video.py - skin Video support functions
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/02/19 14:54:02  dischi
# Some cleanups:
# utils has a function to return a preview image based on the item and
# possible files in mimetypes. image and video now use this and the
# extend function is gone -- it should be an extra section in the skin xml
# file.
#
# Revision 1.4  2003/02/18 07:27:23  gsbarbieri
# Corrected the misspelled 'elipses' -> 'ellipses'
# Now, main1_video uses osd.drawtext(mode='soft') to render text, so it should be better displayed
#
# Revision 1.3  2003/02/18 06:05:21  gsbarbieri
# Bug fixes and new UI features.
#
# Revision 1.2  2003/02/17 18:32:55  dischi
# Display some example xml infos
#
# Revision 1.1  2003/02/17 05:40:45  gsbarbieri
# main1_image: now the image_{width,height} are not hardcoded anymore
#
# main1_video, skin_main1: support Video Browser (extended menu)
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

import sys
import os
import copy
import re
import math

import config

from main1_utils import *

# The OSD class, used to communicate with the OSD daemon
import osd

# Create the OSD object
osd = osd.get_singleton()


# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


class Skin_Video:

    def __call__(self, menuw, settings):
        menu = menuw.menustack[-1]
        val = settings.e_menu[menu.item_types]

        up = menu.page_start            # 0 if first page
        if menu.page_start + (self.getCols(val) * self.getRows(val)) > \
           len(menu.choices):
            down = 0
        else:
            down = 1
        
        self.Clear(val)
        self.Listing((menu.selected, menuw.menu_items, (up, down)), settings)
        self.View(menu.selected, settings)
        self.Info(menu.selected, val)


    def Clear(self, settings):
        InitScreen(settings, (settings.background.mask, ))

        # Show title
        DrawTextFramed('Video Browser', settings.header)


    def View(self, item, settings):
        val = settings.e_menu['video'].view 

        if not val.visible:
            return

        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)

        if item:
            preview = getPreview(item, settings, val.width - 2*val.spacing,
                                 val.height - 2*val.spacing)
            if not preview:
                return
            
            w, h = preview.get_size()

            x = val.x + (val.width - w)/2
            y = val.y + (val.height - h)/2

            osd.drawsurface(preview, x, y)


    def Info(self, item, settings):
        val = settings.info

        if not val.visible:
            return

        
        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)
        if item:
            str_w, str_h = osd.stringsize('Ajg', val.font, val.size)

            x = val.x + val.spacing
            y = val.y + val.spacing
            w = val.width - val.spacing
            h = str_h
            
            if item.type == 'video':
                DrawTextFramed('Video: %s' % item.name, val, x, y, w, h)
                y += str_h
                
                if 'tagline' in item.info:
                    DrawTextFramed('Tagline: %s' % item.info["tagline"], val, x, y, w, h)
                    y += str_h

                text = ''
                if 'genre' in item.info:
                    if text: text += ', '
                    text += item.info['genre']

                if 'year' in item.info:
                    if text: text += ', '
                    text += item.info['year']

                if 'runtime' in item.info:
                    if text: text += ', '
                    text += item.info['runtime']

                if 'rating' in item.info:
                    if text: text += ', '
                    text += item.info['rating']

                if text:
                    DrawTextFramed(text, val, x, y, w, h)
                    y += str_h

                if item.available_audio_tracks:
                    text = 'Audio: '
                    for audio in item.available_audio_tracks:
                        if audio == item.selected_audio:
                            audio = '[%s]' % audio
                        text += audio
                    DrawTextFramed(text, val, x, y, w, h)
                    y+=str_h                

                if item.available_subtitles:
                    text = 'Subtitles: '
                    for subtitle in item.available_subtitles:
                        if subtitle == item.selected_subtitle:
                            subtitle = '[%s]' % subtitle
                        text += subtitle
                    DrawTextFramed(text, val, x, y, w, h)
                    y+=str_h                

                if 'plot' in item.info:
                    DrawTextFramed('Plot: %s' % item.info['plot'], val, x, y,
                                   w, (val.height-h), mode='soft')
                                    
                    
                    
            elif item.type == 'dir':
                DrawTextFramed('Folder: %s' %  item.name[1:-1], val, x, y, w, h)
                y += str_h
                DrawTextFramed('Path: %s' %  item.dir, val, x, y, w, h)
                

            elif item.type == 'playlist':
                DrawTextFramed('Slideshow: %s' %  item.name, val, x, y, w, h)
                y += str_h
                DrawTextFramed('There are %d videos in this playlist' %
                               len(item.playlist), val, x, y, w, h)



    def getCols(self, settings):
        val = settings.listing
        video_width = val.preview_width
        video_height = val.preview_height
        
        items = math.floor(float(val.width - val.spacing) / ( video_width + val.spacing ))
        return int(items)


    def getRows(self, settings):
        val = settings.listing
        video_width = val.preview_width
        video_height = val.preview_height

        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max ( str_h_selection, str_h_normal )

        
        items = math.floor(float(val.height - val.spacing) / \
                           ( video_height + str_h + val.spacing ))
        return int(items)


    def EmptyDir(self, settings):
        val = settings.listing
        conf_x = val.x
        conf_y = val.y
        conf_w = val.width
        conf_h = val.height
        DrawTextFramed('This directory is empty', val, conf_x, conf_y, conf_w, conf_h)
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)
        

    def Listing(self, to_listing, settings):
        val = settings.e_menu['video'].listing 

        if not val.visible:
            return

        video_width = val.preview_width
        video_height = val.preview_height

        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max( str_h_normal, str_h_selection )

        conf_x = val.x
        conf_y = val.y
        conf_w = val.width
        conf_h = val.height


        n_cols = self.getCols(settings.e_menu['video'])
        n_rows = self.getRows(settings.e_menu['video'])

        spacing_x = int((conf_w - ( video_width * n_cols )) / (n_cols+1))
        spacing_y = int((conf_h - ( (video_height + str_h) * n_rows )) / (n_rows+1))
        x0 = conf_x + spacing_x
        y0 = conf_y + spacing_y

        if not to_listing:
            self.EmptyDir(settings.e_menu['video'])
            return

        cols = self.getCols(settings.e_menu['video'])
        rows = self.getRows(settings.e_menu['video'])

        item_pos = 0
        for i in to_listing[1]:
            preview = getPreview(i, settings, video_width, video_height)
            text = i.name
                    
            cur_val = val

            if i == to_listing[0]:
                cur_val = val.selection
                pad = val.spacing
                drawroundbox(x0 - pad, y0 - pad,
                             x0 + video_width + pad, y0 + video_height + str_h + pad,
                             cur_val.bgcolor, 1, cur_val.border_color,
                             radius=cur_val.radius)
                    

            if preview:
                i_w, i_h = preview.get_size()
                cx = x0 + (video_width - i_w) / 2
                ch = y0 + (video_height - i_h) /2
                osd.drawsurface(preview, cx, ch)
            if text:
                DrawTextFramed(text, cur_val, x0, y0 + video_height, video_width,
                               str_h, ellipses=None)
                    
            x0 = x0 + video_width + spacing_x

            item_pos += 1
            if item_pos >= cols:
                item_pos = 0
                y0 = y0 + video_height + str_h + spacing_y
                x0 = conf_x + spacing_x



        # draw a border around the contents
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)

        # draw the up/down indicators
        up, down = to_listing[2]
        if up:
            w, h = osd.bitmapsize(val.indicator['up'])
            osd.drawbitmap(val.indicator['up'], conf_x + conf_w - w - val.spacing,
                           conf_y - h / 2)
            
        if down:
            w, h = osd.bitmapsize(val.indicator['down'])
            osd.drawbitmap(val.indicator['down'], conf_x + conf_w - w - val.spacing,
                           conf_y + conf_h - h / 2)
            
