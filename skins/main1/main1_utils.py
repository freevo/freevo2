#if 0 /*
# -----------------------------------------------------------------------
# main1_util.py - skin utility functions
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2003/02/19 14:54:02  dischi
# Some cleanups:
# utils has a function to return a preview image based on the item and
# possible files in mimetypes. image and video now use this and the
# extend function is gone -- it should be an extra section in the skin xml
# file.
#
# Revision 1.11  2003/02/18 07:27:23  gsbarbieri
# Corrected the misspelled 'elipses' -> 'ellipses'
# Now, main1_video uses osd.drawtext(mode='soft') to render text, so it should be better displayed
#
# Revision 1.10  2003/02/18 06:05:21  gsbarbieri
# Bug fixes and new UI features.
#
# Revision 1.9  2003/02/15 20:45:30  dischi
# speedup
#
# Revision 1.8  2002/12/02 21:41:17  dischi
# Small fix
#
# Revision 1.7  2002/10/28 19:34:55  dischi
# The tv info area now shows info and description with the extra words info
# and description. The title will be writen in a larger font than the
# description. to_info now is a string (e.g. no data loaded) or a tuple
# (title, description)
#
# Revision 1.6  2002/10/21 20:30:50  dischi
# The new alpha layer support slows the system down. For that, the skin
# now saves the last background/alpha layer combination and can reuse it.
# It's quite a hack, the main skin needs to call drawroundbox in main1_utils
# to make the changes to the alpha layer. Look in the code, it's hard to
# explain, but IMHO it's faster now.
#
# Revision 1.5  2002/10/20 09:19:12  dischi
# bugfix
#
# Revision 1.4  2002/10/19 15:09:55  dischi
# added alpha mask support
#
# Revision 1.3  2002/10/16 20:00:00  dischi
# use mode='soft' for drawstringframed for info
#
# Revision 1.2  2002/10/16 19:40:34  dischi
# some cleanups
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

# The OSD class, used to communicate with the OSD daemon
import osd
import util
import pygame
import os

# Create the OSD object
osd = osd.get_singleton()



# Draws a text based on the settings in the XML file
def DrawText(text, settings, x=-1, y=-1, align=''):
    if x == -1: x = settings.x
    if y == -1: y = settings.y
    if not align: align = settings.align

    if settings.shadow_visible:
        osd.drawstring(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                       settings.shadow_color, None, settings.font,
                       settings.size, align)
    osd.drawstring(text, x, y, settings.color, None, settings.font,
                   settings.size, align)


# Draws a text inside a frame based on the settings in the XML file
def DrawTextFramed(text, settings, x=-1, y=-1, width=None, height=None, size=0, mode='hard', ellipses='...'):
    if x == -1: x = settings.x
    if y == -1: y = settings.y

    if width == None: width  = settings.width
    if height == None: height = settings.height

    if size == 0: size = settings.size

    if settings.shadow_visible:
        osd.drawstringframed(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                             width, height, settings.shadow_color, None,
                             font=settings.font, ptsize=size,
                             align_h=settings.align, align_v=settings.valign, mode=mode, ellipses=ellipses)
    osd.drawstringframed(text, x, y, width, height, settings.color, None,
                         font=settings.font, ptsize=size,
                         align_h=settings.align, align_v=settings.valign, mode=mode, ellipses=ellipses)





last_screen_id = None
last_screen = pygame.Surface((osd.width, osd.height), 0, 32)

last_bg = pygame.Surface((osd.width, osd.height), 0, 32)
last_bg_name = None
last_alpha = None

def InitScreen(settings, masks, cover_visible = 0):
    global last_screen
    global last_screen_id
    global last_bg
    global last_bg_name
    global last_alpha


    # generate an id of the screen to draw: background+masks,logo
    screen_id = [ settings.background.image ]
    
    for i in masks:
        if i:
            if isinstance(i, list):
                for r in i:
                    visible = r.visible

                    if visible=='cover':
                        visible = cover_visible
                    
                    if visible:
                        screen_id += [ r.x, r.y, r.width, r.height ]
            else:
                screen_id += [ i ]


    val = settings.logo
    if val.image and val.visible:
        screen_id += [val.image, val.width, val.height, val.x, val.y ]


    # is the new screen to draw the same as the last one?
    if screen_id == last_screen_id:
        # re-use background
        osd.screen.blit(last_screen, (0,0))


    else:
        # generate new background
        last_screen_id = screen_id

        osd.clearscreen(osd.COL_BLACK)

        # same background?
        if last_bg_name == settings.background.image:
            #re-use
            osd.screen.blit(last_bg, (0,0))

        # no? than load the image and save the background
        elif settings.background.image:
            apply(osd.drawbitmap, (settings.background.image, -1, -1))

            # save background
            last_bg.blit(osd.screen, (0,0))
            last_bg_name = settings.background.image

        # draw all the alpha layer
        layer = None

        for i in masks:
            if i:
                if not layer:
                    layer = osd.createlayer()

                if isinstance(i, list):

                    for r in i:
                        visible = r.visible

                        if visible=='cover':
                            visible = cover_visible

                        if visible:
                            osd.drawroundbox(r.x, r.y, r.x+r.width, r.y+r.height, r.color,
                                             r.border_size, r.border_color, r.radius, layer)

                else:
                    osd.drawbitmap(i,-1,-1, layer=layer)

        # draw the logo
        val = settings.logo
        if val.image and val.visible:
            if val.width and val.height:
                osd.drawbitmap(util.resize(val.image, val.width, val.height),
                               val.x, val.y)
            else:
                osd.drawbitmap(val.image, val.x, val.y)


        # save everything for re-use
        if layer:
            last_alpha = layer
            osd.putlayer(layer)
        else:
            last_alpha = None
            
        last_screen.blit(osd.screen, (0,0))
        
    return None


# mapper to draw the round box into the alpha layer
def drawroundbox(x0, y0, x1, y1, color=None, border_size=0, border_color=None, radius=0):
    if last_alpha:
        # Make sure the order is top left, bottom right
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        h = y1 - y0
        w = x1 - x0

        # load old background
        bg = pygame.Surface((w,h), 0, 32)
        bg.blit(last_bg, (0,0), (x0,y0, w, h))

        # load old alpha layer
        a = osd.createlayer(w,h)
        a.blit(last_alpha, (0,0), (x0,y0, w, h))

        # draw the round box
        osd.drawroundbox(0, 0, w, h, color, border_size, border_color, radius, layer=a)

        # put it all back
        bg.blit(a, (0, 0))
        osd.screen.blit(bg, (x0, y0))
    else:
        osd.drawroundbox(x0, y0, x1, y1, color, border_size, border_color, radius)

    
def getPreview(item, settings, w, h):
    if not settings.icon_dir:
        return ""

    if item.image:
        image = osd.loadbitmap('thumb://%s' % item.image)
        return pygame.transform.scale(image, (w,h))

    image = None
    
    if item.type == 'dir':
        if os.path.isfile('%s/mimetypes/folder_%s.png' % \
                          (settings.icon_dir, item.display_type)):
            image = '%s/mimetypes/folder_%s.png' % \
                    (settings.icon_dir, item.display_type)
        else:
            image = '%s/mimetypes/folder.png' % settings.icon_dir
    
    elif os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.type)):
        image = '%s/mimetypes/%s.png' % (settings.icon_dir, item.type)

    if image:
        image = osd.loadbitmap('thumb://%s' % image)
        i_w, i_h = image.get_size()
        scale = min(float(w)/i_w, float(h)/i_h)
        image = osd.zoomsurface(image,scale)

    return image
