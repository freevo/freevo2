#
# osd_sdl.py
#
# This is the class for using the SDL OSD functions. It will eventually
# replace the current osd.py
#
# $Id$

import socket, time, sys

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The PyGame Python SDL interface.
# Dependencies: Freetype2 (already in Freevo!), SDL, SDL_ttf, SDL_image, PyGame
# The PyGame+SDL websites has good install instructions.


# RPMs are available for most stuff (XXX devel needed too?):
# 
# SDL: http://www.libsdl.org/download-1.2.php
# SDL_image RPMs/debs: http://www.libsdl.org/projects/SDL_image/
# SDL_ttf RPMs/debs: http://www.libsdl.org/projects/SDL_ttf/
# PyGame: http://www.pygame.org/download.shtml
#    To build, make sure you have the correct sdl-config in your path! Then:
#    python setup.py build
#    python setup.py install



import pygame
from pygame.locals import *

# Set to 1 for debug output
DEBUG = 1

print 'XXXXXX LOADING TEST OSD'

# Module variable that contains an initialized OSD() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = OSD()
        
    return _singleton


class Font:

    filename = ''
    ptsize = 0
    font = None

    
class OSD:

    # The colors
    # XXX Add more
    COL_RED = 0xff0000
    COL_GREEN = 0x00ff00
    COL_BLUE = 0x0000ff
    COL_BLACK = 0x000000
    COL_WHITE = 0xffffff
    COL_SOFT_WHITE = 0xEDEDED
    COL_MEDIUM_YELLOW = 0xFFDF3E
    COL_SKY_BLUE = 0x6D9BFF
    COL_DARK_BLUE = 0x0342A0
    COL_ORANGE = 0xFF9028
    COL_MEDIUM_GREEN = 0x54D35D
    COL_DARK_GREEN = 0x038D11


    # XXX width, height from config.OSD_WIDTH etc
    def __init__(self, width=768, height=576):

        self.fontcache = []
        
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE
        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 0, 32)

        self.clearscreen(self.COL_WHITE)
        self.update()



    def _send(arg1, *arg, **args): # XXX remove
        pass

    
    def shutdown(self):
        pass


    def clearscreen(self, color=None):
        if color == None:
            color = self.default_bg_color
        self.screen.fill(self._sdlcol(color))
        

    def setpixel(self, x, y, color):
        pass # XXX Not used anywhere


    # Bitmap buffers in Freevo:
    #
    # There are 4 different bitmap buffers in the system.
    # 1) The load bitmap buffer
    # 2) The zoom bitmap buffer
    # 3) The OSD drawing buffer
    # 4) The screen (fb/x11/sdl) buffer
    #
    # Drawing operations (text, line, etc) operate on the
    # OSD drawing buffer, and are copied to the screen buffer
    # using update().
    #
    # The drawbitmap() operation is time-consuming for larger
    # images, which is why the load, zoom, and draw operations each
    # have their own buffer. This can speed up things if the
    # application is pipelined to preload/prezoom the bitmap
    # where the next bitmap file is known in advance, or the same
    # portions of the same bitmap is zoomed repeatedly.
    # 

    # Caches a bitmap in the OSD without displaying it.
    def loadbitmap(self, filename):
        pass # XXX Fix later
    

    # Loads and zooms a bitmap without copying it to the OSD drawing
    # buffer.
    def zoombitmap(self, filename, scaling=None, bbx=0, bby=0, bbw=0, bbh=0):
        pass # XXX Fix later
    
        
    # Draw a bitmap on the OSD. It is automatically loaded into the cache
    # if not already there. The loadbitmap()/zoombitmap() functions can
    # be used to "pipeline" bitmap loading/drawing.
    def drawbitmap(self, filename, x=0, y=0, scaling=None,   # XXX scale, zoom, tile not supported yet!
                   bbx=0, bby=0, bbw=0, bbh=0):

        try:
            image = pygame.image.load(filename).convert_alpha()  # XXX Cannot load everything
        except:
            print 'SDL image load problem!'
            return

        if scaling:
            w, h = image.get_size()
            w = int(w*scaling)
            h = int(h*scaling)
            #image = pygame.transform.rotozoom(image, 0, scaling) # XXX incorporate rotation too
            image = pygame.transform.scale(image, (w, h))
        self.screen.blit(image, (x, y))


    def drawline(self, x0, y0, x1, y1, width=None, color=None):
        if width == None:
            width = 1

        if color == None:
            color = self.default_fg_color

        args1 = str(x0) + ';' + str(y0) + ';'
        args2 = str(x1) + ';' + str(y1) + ';' + str(width) + ';' + str(color)
        self._send('drawline;' + args1 + args2)


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0):
        print 'drawbox: %s 0x%08x %s' % (width, color, fill)
        
        if width == None:
            width = 1

        if width == -1:
            fill = 1
            width = 4 # XXX TEST for now!
            
        if color == None:
            color = self.default_fg_color

        r = (x0, y0, x1-x0, y1-y0)
        #c = self._sdlcol(color)
        c = (0, 0, 255, 5)
        if fill:
            #self.screen.fill(c, r)
            pygame.draw.rect(self.screen, c, r, width)
            
        
    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0):
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME
            ptsize = config.OSD_DEFAULT_FONTSIZE

        f = self._getfont(font, ptsize)

        # Render string with anti-aliasing
        if bgcolor == None:
            ren = f.render(string, 1, self._sdlcol(fgcolor))
        else:
            ren = f.render(string, 1, self._sdlcol(fgcolor), self._sdlcol(bgcolor))
        
        self.screen.blit(ren, (x, y))
        

    def update(self):
        pygame.display.flip()


    def _getfont(self, filename, ptsize):
        for font in self.fontcache:
            if font.filename == filename and font.ptsize == ptsize:
                return font.font

        font = pygame.font.Font(filename, ptsize)
        f = Font()
        f.filename = filename
        f.ptsize = ptsize
        f.font = font
        
        self.fontcache.append(f)

        return f.font

        
    # Convert a 32-bit TRGB color to a 4 element tuple for SDL
    def _sdlcol(self, col):
        a = 255 - ((col >> 24) & 0xff)
        r = (col >> 16) & 0xff
        g = (col >> 8) & 0xff
        b = (col >> 0) & 0xff
        c = (r, g, b, a)
        return c
            

#
# Simple test...
#
if __name__ == '__main__':
    osd = OSD()
    osd.clearscreen()

