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
def DrawText(text, settings, x=-1, y=-1, align=''):
    if x == -1:
        x = settings.x
    if y == -1:
        y = settings.y
    if not align:
        align = settings.align

    if settings.shadow_visible:
        osd.drawstring(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                       settings.shadow_color, None, settings.font,
                       settings.size, align)
    osd.drawstring(text, x, y, settings.color, None, settings.font,
                   settings.size, align)


# Draws a text inside a frame based on the settings in the XML file
def DrawTextFramed(text, settings, x=-1, y=-1, width=-1, height=-1):
    if x == -1:
        x = settings.x
    if y == -1:
        y = settings.y

    if width == -1:
        width = settings.width

    if settings.shadow_visible:
        osd.drawstringframed(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                             width, height, settings.shadow_color, None,
                             font=settings.font, ptsize=settings.size,
                             align_h=settings.align, align_v=settings.valign)
    osd.drawstringframed(text, x, y, width, height, settings.color, None,
                         font=settings.font, ptsize=settings.size,
                         align_h=settings.align, align_v=settings.valign)


def DrawLogo(settings):
    if settings.image and settings.visible:
        if settings.width and settings.height:
            osd.drawbitmap(util.resize(settings.image, settings.width, settings.height),
                           settings.x, settings.y)
        else:
            osd.drawbitmap(settings.image, settings.x, settings.y)
    
