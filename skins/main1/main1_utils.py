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

# Create the OSD object
osd = osd.get_singleton()



# Draws a text based on the settings in the XML file
def DrawText(text, settings, x=-1, y=-1, align='', layer=None):
    if x == -1: x = settings.x
    if y == -1: y = settings.y
    if not align: align = settings.align

    if settings.shadow_visible:
        osd.drawstring(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                       settings.shadow_color, None, settings.font,
                       settings.size, align, layer)
    osd.drawstring(text, x, y, settings.color, None, settings.font,
                   settings.size, align, layer)


# Draws a text inside a frame based on the settings in the XML file
def DrawTextFramed(text, settings, x=-1, y=-1, width=-1, height=-1, mode='hard'):
    if x == -1: x = settings.x
    if y == -1: y = settings.y

    if width  == -1: width  = settings.width
    if height == -1: height = settings.height

    if settings.shadow_visible:
        osd.drawstringframed(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                             width, height, settings.shadow_color, None,
                             font=settings.font, ptsize=settings.size,
                             align_h=settings.align, align_v=settings.valign, mode=mode)
    osd.drawstringframed(text, x, y, width, height, settings.color, None,
                         font=settings.font, ptsize=settings.size,
                         align_h=settings.align, align_v=settings.valign, mode=mode)


def InitScreen(settings, masks, cover_visible = 0):
    osd.clearscreen(osd.COL_BLACK)

    if settings.background.image:
        apply(osd.drawbitmap, (settings.background.image, -1, -1))

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

    val = settings.logo
    if val.image and val.visible:
        if val.width and val.height:
            osd.drawbitmap(util.resize(val.image, val.width, val.height),
                           val.x, val.y)
        else:
            osd.drawbitmap(val.image, val.x, val.y)

    return layer


def DrawBox(x0, y0, x1, y1, color = None, border_size = 0, border_color = None):
    osd.drawbox(x0, y0, x1, y1, width=-1, color=color)
    if border_size >= 0:
        osd.drawbox(x0, y0, x1, y1, width=border_size, color=border_color)
    


def PutLayer(layer):
    if layer:
        osd.putlayer(layer)
    return None
    
def ShowScreen(layer):
    if layer:
        osd.putlayer(layer)
    osd.update()
