#!/usr/bin/env python
#-----------------------------------------------------------------------
# gui - First attempt at a freevo gui library
#-----------------------------------------------------------------------
# $Id$
#
# The goal is to make a OO GUI library for use with freevo. The main
# idea is that skins can use or inherit from this class and override
# when needed.
#
# Todo:  - Implement "listbox" for selections with different styles
#          for showing what is selected (glow, bg_color, etc)
#             ListItem -> Label -> Text
#        - Make GraphBar class.
#        - Split classes into separate files.
#        - Make more expetions.
#        * Find a way to do Z-index handling.
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/08/15 22:45:42  tfmalt
# o Inital commit of Freevo GUI library. Files are put in directory 'gui'
#   under Freevo.
# o At the moment the following classes are implemented (but still under
#   development):
#     Border, Color, Label, GUIObject, PopupBox, ZIndexRenderer.
# o These classes are fully workable, any testing and feedback will be
#   appreciated.
#
# Revision 1.2  2002/08/13 12:46:48  tfmalt
# o Implemented ZIndexRenderer to keep track of what is under objects and
#   redrawing supporting N levels of transparency (for example copy gui_sdl
#   to main freevo catalog and run standalone.
#
#-----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------
"""
A Object Oriented GUI Widget library for Freevo

This is aimed at being a general library for GUI programming with Freevo.
It is built directly on top of SDL with pygame, and it's aimed at being
fairly fast.

Event though the library is built from the ground the design is heavy
influenced by other GUI toolkits, such as Java JDK and QT.

Currently not many classes are in place, but hopefully we will add more
in time.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


# XXX Hack to import modules placed above us.
import sys
import os.path
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))


import time 
import gui.ZIndexRenderer

from pygame.locals  import *
from gui.Border     import *
from gui.Color      import *
from gui.GUIObject  import *
from gui.PopupBox   import *
from gui.Label      import *
from gui.exceptions import *

DEBUG = 0

osd = osd_sdl.get_singleton()
zir = gui.ZIndexRenderer.get_singleton()



# ======================================================================
# XXX These functions are here for debug.. I'll remove them in time.
# ======================================================================
clock = pygame.time.Clock()
def wait_loop():
    while 1:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                return


def save_images( pb1, pb2, pb3 ):
    if pb1.bg_image:
        pygame.image.save( pb1.bg_image, '/tmp/bp1.bmp' )
    if pb2.bg_image:
        pygame.image.save( pb2.bg_image, '/tmp/bp2.bmp' )
    if pb3.bg_image:
        pygame.image.save( pb3.bg_image, '/tmp/bp3.bmp' )

def save_image( obj ):
    if obj.bg_image:
        pygame.image.save( obj.bg_image,
                           '/tmp/'+str(obj.__class__.__name__)+'.bmp')
    elif obj.parent.bg_image:
        pygame.image.save( obj.parent.bg_image,
                           '/tmp/parent'+str(obj.__class__.__name__)+'.bmp')
        

# ======================================================================
# Main: used for testing.
# ======================================================================

if __name__ == '__main__':
    
    osd.clearscreen()
    
    osd.drawbitmap( 'skins/images/aubin_bg1.png' )
    osd.drawstring('Hello Sailor' + str(time.time()), 10, 10,
                   font='skins/fonts/Arial_Bold.ttf',ptsize=14)
    
    osd.update()

    pb  = osd_sdl.SynchronizedObject( PopupBox(100, 100, 300, 150,
                                               'Hello again sailor',
                                               bg_color=Color((255,0,0,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=1)
                                      )

    pb2 = osd_sdl.SynchronizedObject( PopupBox(200, 150, 300, 150,
                                               'Hello twice sailor',
                                               bg_color=Color((0,255,0,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=2)
                                      )
                                      
    pb3 = osd_sdl.SynchronizedObject( PopupBox(300, 200, 300, 150,
                                               'Hello trice sailor',
                                               bg_color=Color((0,0,192,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=3) )
    
    pb4 = osd_sdl.SynchronizedObject( PopupBox(200, 200, 300, 150,
                                               'Hello trice sailor',
                                               bg_color=Color((255,128,0,128)),
                                               border=Border.BORDER_FLAT) )
    

    print "Showing first rectangle..."
    pb.show()
    save_images( pb, pb2, pb3 )
    osd.update()
                                      
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing second rectangle..."
    pb2.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing third rectangle..."
    pb3.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing fourth rectangle..."
    pb4.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Hiding second rectangle..."
    pb2.hide()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing second rectangle..."
    pb2.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Hiding first rectangle..."
    pb.hide()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing first rectangle..."
    pb.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Hiding second rectangle..."
    pb2.hide()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Showing second rectangle..."
    pb2.show()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Hiding first rectangle..."
    pb.hide()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

    print "Hiding SECOND rectangle..."
    pb2.hide()
    save_images( pb, pb2, pb3 )
    osd.update()
    print "  Waiting at bottom of cycle..."
    wait_loop()

