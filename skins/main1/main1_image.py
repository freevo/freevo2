#if 0 /*
# -----------------------------------------------------------------------
# main1_image.py - skin Image support functions
# -----------------------------------------------------------------------
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

import sys, os, copy, re, math
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


class Skin_Image:

    imagebrowser_expand = 0

    def DrawImage(self, settings):
        self.DrawImage_Clear(settings)


    def DrawImage_Clear(self, settings):
        InitScreen(settings, (settings.background.mask, ))

        # Show title
        DrawTextFramed('Image Browser', settings.header)

    def DrawImage_getFormatedImage(self, filename, w, h, i_orientation=None):
        image = osd.loadbitmap(filename)
        i_w, i_h = image.get_size()

        # rotate:
        if h > w:
            orientation='vertical'
        else:
            orientation='horizontal'

        rotation = 0
        if i_orientation:
            if i_orientation == 'right_top':
                rotation=-90.0
            elif i_orientation == 'right_bottom':
                rotation=-180.0
            elif i_orientation == 'left_top':
                rotation=0
            elif i_orientation == 'left_bottom':
                rotation=-270.0
        else:
            if i_h > i_w:
                i_orientation='vertical'
            else:
                i_orientation='horizontal'

            if orientation != i_orientation:
                rotation=90.0

        if rotation != 0:
            image = osd.zoomsurface(image,rotation=rotation)
            i_w, i_h = image.get_size()

        # scale:
        scale_y = float(h)/i_h
        scale_x = float(w)/i_w

        scale = min(scale_x, scale_y)
        
        image = osd.zoomsurface(image,scale)
    
        return image


    def DrawImage_getExpand(self, settings):
        return self.imagebrowser_expand

    def DrawImage_setExpand(self, expand, settings):
        self.imagebrowser_expand = expand

    def DrawImage_View(self, to_view, settings):
        val = settings.view

        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)

        if to_view != None:
            orientation = None
            if to_view[0] == 'image':
                filename = to_view[1]
                orientation = to_view[2]
            elif to_view[0] == 'dir':
                filename = val.img['dir']
            elif to_view[0] == 'playlist':
                filename = val.img['playlist']
            
            preview = self.DrawImage_getFormatedImage(filename,
                                                      val.width - 2*val.spacing,
                                                      val.height - 2*val.spacing, orientation)
            w, h = preview.get_size()

            x = val.x + (val.width - w)/2
            y = val.y + (val.height - h)/2

            osd.drawsurface(preview, x, y)
            

            



    def DrawImage_Info(self, to_info, settings):
        val = settings.info
        osd.drawroundbox(val.x, val.y, val.x+val.width, val.y+val.height,
                         color=val.bgcolor, radius=val.radius)
        if to_info:
            str_w, str_h = osd.stringsize('Ajg', val.font, val.size)

            x = val.x + val.spacing
            y = val.y + val.spacing
            w = val.width - val.spacing
            h = str_h
            
            if to_info[0] == 'image':
                DrawTextFramed('Image: %s' %  to_info[1], val, x, y, w, h)
                y += str_h
                DrawTextFramed('Path: %s' %  to_info[2], val, x, y, w, h)
                y += str_h
                if u'title' in to_info[3]:
                    DrawTextFramed('Title: %s' %  to_info[3]['title'], val, x, y, w, h)
                    y += str_h
                if u'description' in to_info[3]:
                    DrawTextFramed('Description: %s' % to_info[3]['description'], val, x, y, w, h)
                    y += str_h
                                
            elif to_info[0] == 'dir':
                DrawTextFramed('Folder: %s' %  to_info[1], val, x, y, w, h)
                y += str_h
                DrawTextFramed('Path: %s' %  to_info[2], val, x, y, w, h)
                

            elif to_info[0] == 'playlist':
                DrawTextFramed('Slideshow: %s' %  to_info[1], val, x, y, w, h)
                y += str_h
                DrawTextFramed('Path: %s' %  to_info[2], val, x, y, w, h)
                y += str_h
                DrawTextFramed('There are %d images in this slideshow' %  len(to_info[2]), val, x, y, w, h)
                


    def DrawImage_getCols(self, settings):
        val = settings.listing
        image_height = 100
        image_width = 160

        items = math.floor(float(val.width - val.spacing) / ( image_width + val.spacing ))
        return int(items)


    def DrawImage_getRows(self, settings):
        val = settings.listing
        image_height = 100
        image_width = 160

        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max ( str_h_selection, str_h_normal )

        
        items = math.floor(float(val.height - val.spacing) / ( image_height + str_h + val.spacing ))
        return int(items)

    def DrawImage_EmptyDir(self, settings):
        val = settings.listing
        if self.DrawImage_getExpand(settings) == 0:
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
        


    def DrawImage_Listing(self, to_listing, settings):
        val = settings.listing 

        if self.DrawImage_getExpand(settings) == 0:
            conf_x = val.x
            conf_y = val.y
            conf_w = val.width
            conf_h = val.height
        else:
            conf_x = val.expand.x
            conf_y = val.expand.y
            conf_w = val.expand.width
            conf_h = val.expand.height

        image_width = 160
        image_height = 100

        dir_preview = self.DrawImage_getFormatedImage(val.img['dir'],
                                                      image_width, image_height)
        pl_preview = self.DrawImage_getFormatedImage(val.img['playlist'],
                                                     image_width, image_height)

        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max( str_h_normal, str_h_selection )


        n_cols = self.DrawImage_getCols(settings)
        n_rows = self.DrawImage_getRows(settings)

        spacing_x = int((conf_w - ( image_width * n_cols )) / (n_cols+1))
        spacing_y = int((conf_h - ( (image_height + str_h) * n_rows )) / (n_rows+1))
        x0 = conf_x + spacing_x
        y0 = conf_y + spacing_y

        if not to_listing:
            self.DrawImage_EmptyDir(settings)
            return

        for row in to_listing[1]:
            x0 = conf_x + spacing_x

            for i in row:
                preview = None
                text = None

                if i.type == 'dir':
                    preview = dir_preview
                    text = i.name
                elif i.type == 'image':
                    orientation = None
                    if 'Orientation' in i.binsexif:
                        orientation = i.binsexif['Orientation']
                        
                    preview = self.DrawImage_getFormatedImage(i.filename, image_width, image_height,
                                                              orientation)
                    text = i.name
                elif i.type == 'playlist':
                    preview = pl_preview
                    text = i.name
                    
                cur_val = val
                if i == to_listing[0]:
                    cur_val = val.selection
                    pad = val.spacing
                    drawroundbox(x0 - pad, y0 - pad,
                                 x0 + image_width + pad, y0 + image_height + str_h + pad,
                                 cur_val.bgcolor, 1, cur_val.border_color, radius=cur_val.radius)
                    

                if preview:
                    i_w, i_h = preview.get_size()
                    cx = x0 + (image_width - i_w) / 2
                    ch = y0 + (image_height - i_h) /2
                    osd.drawsurface(preview, cx, ch)
                if text:
                    DrawTextFramed(text, cur_val, x0, y0 + image_height, image_width, str_h)
                    
                x0 = x0 + image_width + spacing_x

            y0 = y0 + image_height + str_h + spacing_y


        # draw a border around the contents
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)

        # draw the up/down indicators
        up, down = to_listing[2]
        if up:
            w, h = osd.bitmapsize(val.indicator['up'])
            osd.drawbitmap(val.indicator['up'], conf_x + conf_w - w - val.spacing, conf_y - h / 2)
            
        if down:
            w, h = osd.bitmapsize(val.indicator['down'])
            osd.drawbitmap(val.indicator['down'], conf_x + conf_w - w - val.spacing, conf_y + conf_h - h / 2)
            
