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

    expand = 0

    def __call__(self, menuw, settings):
        menu = menuw.menustack[-1]
        settings = settings.e_menu[menu.item_types]

        up = menu.page_start            # 0 if first page
        if menu.page_start + (self.getCols(settings) * self.getRows(settings)) > \
           len(menu.choices):
            down = 0
        else:
            down = 1
        
        self.Clear(settings)
        self.Listing((menu.selected, menuw.menu_items, (up, down)), settings)
        self.View(menu.selected, settings)
        self.Info(menu.selected, settings)

    def Clear(self, settings):
        InitScreen(settings, (settings.background.mask, ))

        # Show title
        DrawTextFramed('Video Browser', settings.header)

    def getFormatedVideo(self, filename, w, h):
        image = osd.loadbitmap('thumb://%s' % filename)

        if not image:
            return None
        
        i_w, i_h = image.get_size()

        # rotate:
        if h > w:
            orientation='vertical'
        else:
            orientation='horizontal'

        rotation = 0
        if i_h > i_w:
            i_orientation='vertical'
        else:
            i_orientation='horizontal'
            
        if orientation != i_orientation:
            rotation=90.0

        if rotation != 0:
            video = osd.zoomsurface(image,rotation=rotation)
            i_w, i_h = image.get_size()

        # scale:
        scale_y = float(h)/i_h
        scale_x = float(w)/i_w

        scale = min(scale_x, scale_y)
        
        image = osd.zoomsurface(image,scale)
    
        return image


    def getExpand(self, settings):
        return self.expand

    def setExpand(self, expand, settings):
        self.expand = expand

    def View(self, item, settings):
        val = settings.view

        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)

        if item:
            orientation = None
            if item.type == 'video':
                filename = item.image
                if not filename:
                    filename = val.img['default']
            elif item.type == 'dir':
                filename = val.img['dir']
            elif item.type == 'playlist':
                filename = val.img['playlist']
            
            preview = self.getFormatedVideo(filename,
                                            val.width - 2*val.spacing,
                                            val.height - 2*val.spacing)
            if not preview:
                return
            
            w, h = preview.get_size()

            x = val.x + (val.width - w)/2
            y = val.y + (val.height - h)/2

            osd.drawsurface(preview, x, y)


    def Info(self, item, settings):
        val = settings.info
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
                DrawTextFramed('File: %s' % item.filename, val, x, y, w, h)
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
        if self.getExpand(settings) == 0:
            conf_x = val.x
            conf_y = val.y
            conf_w = val.width
            conf_h = val.height
        else:
            conf_x = val.expand.x
            conf_y = val.expand.y
            conf_w = val.expand.width
            conf_h = val.expand.height

        DrawTextFramed('This directory is empty', val, conf_x, conf_y, conf_w, conf_h)
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)
        

    def Listing(self, to_listing, settings):
        val = settings.listing 

        if self.getExpand(settings) == 0:
            conf_x = val.x
            conf_y = val.y
            conf_w = val.width
            conf_h = val.height
        else:
            conf_x = val.expand.x
            conf_y = val.expand.y
            conf_w = val.expand.width
            conf_h = val.expand.height

        video_width = val.preview_width
        video_height = val.preview_height

        dir_preview = self.getFormatedVideo(val.img['dir'],
                                                      video_width, video_height)
        pl_preview = self.getFormatedVideo(val.img['playlist'],
                                                     video_width, video_height)

        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max( str_h_normal, str_h_selection )


        n_cols = self.getCols(settings)
        n_rows = self.getRows(settings)

        spacing_x = int((conf_w - ( video_width * n_cols )) / (n_cols+1))
        spacing_y = int((conf_h - ( (video_height + str_h) * n_rows )) / (n_rows+1))
        x0 = conf_x + spacing_x
        y0 = conf_y + spacing_y

        if not to_listing:
            self.EmptyDir(settings)
            return

        cols = self.getCols(settings)
        rows = self.getRows(settings)

        item_pos = 0
        for i in to_listing[1]:
            preview = None
            text = None

            if i.type == 'dir':
                preview = dir_preview
                text = i.name

            elif i.type == 'video':
                filename = i.image
                if not filename:
                    filename = val.img['default']
                preview = self.getFormatedVideo(filename, video_width, video_height)
                text = i.name

            elif i.type == 'playlist':
                preview = pl_preview
                text = i.name
                    
            cur_val = val

            if i == to_listing[0]:
                cur_val = val.selection
                pad = val.spacing
                drawroundbox(x0 - pad, y0 - pad,
                             x0 + video_width + pad, y0 + video_height + str_h + pad,
                             cur_val.bgcolor, 1, cur_val.border_color, radius=cur_val.radius)
                    

            if preview:
                i_w, i_h = preview.get_size()
                cx = x0 + (video_width - i_w) / 2
                ch = y0 + (video_height - i_h) /2
                osd.drawsurface(preview, cx, ch)
            if text:
                DrawTextFramed(text, cur_val, x0, y0 + video_height, video_width, str_h)
                    
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
            
