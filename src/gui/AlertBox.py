#if 0 /*
# -----------------------------------------------------------------------
# AlertBox.py - simple alert popup box class
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/03/02 20:15:41  rshortt
# GUIObject and PopupBox now get skin settings from the new skin.  I put
# a test for config.NEW_SKIN in GUIObject because this object is used by
# MenuWidget, so I'll remove this case when the new skin is finished.
#
# PopupBox can not be used by the old skin so anywhere it is used should
# be inside a config.NEW_SKIN check.
#
# PopupBox -> GUIObject now has better OOP behaviour and I will be doing the
# same with the other objects as I make them skinnable.
#
# Revision 1.2  2003/02/24 12:14:57  rshortt
# Removed more unneeded self.parent.refresh() calls.
#
# Revision 1.1  2003/02/18 13:40:52  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
import config

from GUIObject import *
from PopupBox  import *
from Color     import *
from Button    import *
from Border    import *
from Label     import *
from types     import *

DEBUG = 1


class AlertBox(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    def __init__(self, text=" ", left=None, top=None, width=300, height=160, 
                 bg_color=None, fg_color=None, icon=None, border=None, 
                 bd_color=None, bd_width=None):


        PopupBox.__init__(self, text, left, top, width, height, bg_color, 
                          fg_color, icon, border, bd_color, bd_width)


        ((bg_type, skin_bg), skin_spacing, skin_color, skin_font, 
         skin_button_default, skin_button_selected) = \
         self.skin.GetPopupBoxStyle()

        print 'STYLE: %s, %s, %s, %s, %s, %s' % (skin_bg, skin_spacing, 
               skin_color, skin_font, skin_button_default, skin_button_selected)

# STYLE: ('rectangle', <xml_skin.XML_rectangle instance at 0x801b73ec>), 9, 16777215, <xml_skin.XML_font instance at 0x801b6c7c>, <xml_skin.XML_data instance at 0x80474974>, <xml_skin.XML_data instance at 0x80302e6c>



        self.set_h_align(Align.CENTER)

        self.label.top = self.top + 25

        b1 = Button('OK')
        bleft = self.left + self.width/2 - b1.width/2
        btop = self.top + self.height - b1.height - 25
        b1.set_position(bleft, btop) 
        b1.toggle_selected()
        self.add_child(b1)


    def eventhandler(self, event):
        if DEBUG: print 'AlertBox: EVENT = %s' % event

        trapped = [self.rc.UP, self.rc.DOWN, self.rc.LEFT, self.rc.RIGHT]
        if trapped.count(event) > 0:
            return
        elif [self.rc.ENTER, self.rc.SELECT, self.rc.EXIT].count(event) > 0:
            print 'HIT OK'
            self.destroy()
        else:
            return self.parent.eventhandler(event)


