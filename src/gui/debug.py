#!/usr/bin/env python
#-----------------------------------------------------------------------
# debug
#-----------------------------------------------------------------------
# $Id$
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

import time 
import pygame

from pygame.locals  import *

import util

DEBUG = 1

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
    
    osd.drawbitmap( 'share/images/aubin_bg1.png' )
    osd.drawstring('Hello Sailor' + str(time.time()), 10, 10,
                   font='share/fonts/Vera.ttf',ptsize=14)
    
    osd.update()

    pb  = util.SynchronizedObject( PopupBox(100, 100, 300, 150,
                                               'Hello again sailor',
                                               bg_color=Color((255,0,0,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=1)
                                      )

    pb2 = util.SynchronizedObject( PopupBox(200, 150, 300, 150,
                                               'Hello twice sailor',
                                               bg_color=Color((0,255,0,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=2)
                                      )
                                      
    pb3 = util.SynchronizedObject( PopupBox(300, 200, 300, 150,
                                               'Hello trice sailor',
                                               bg_color=Color((0,0,192,128)),
                                               border=Border.BORDER_FLAT,
                                               bd_width=3) )
    
    pb4 = util.SynchronizedObject( PopupBox(200, 200, 300, 150,
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

