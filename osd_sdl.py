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
import pygame
from pygame.locals import *

# RPMs are available for most stuff (XXX devel needed too?):
# 
# SDL: http://www.libsdl.org/download-1.2.php
# SDL_image RPMs/debs: http://www.libsdl.org/projects/SDL_image/
# SDL_ttf RPMs/debs: http://www.libsdl.org/projects/SDL_ttf/
# PyGame: http://www.pygame.org/download.shtml
#    To build, make sure you have the correct sdl-config in your path! Then:
#    python setup.py build
#    python setup.py install

# Set to 1 for debug output
DEBUG = 1

print 'XXXXXX LOADING TEST OSD'

help_text = """
F1      SLEEP
HOME    MENU
g       GUIDE
ESCAPE  EXIT
UP      UP
DOWN    DOWN
LEFT    LEFT
RIGHT   RIGHT
SPACE   SELECT
F2      POWER
F3      MUTE
PLUS    VOL+
MINUS   VOL-
c       CH+
v       CH-
1       1
2       2
3       3
4       4
5       5
6       6
7       7
8       8
9       9
0       0
d       DISPLAY
e       ENTER
_       PREV_CH
o       PIP_ONOFF
w       PIP_SWAP
i       PIP_MOVE
F4      TV_VCR
r       REW
p       PLAY
f       FFWD
u       PAUSE
s       STOP
F6      REC
PERIOD  EJECT
"""


cmds_sdl = {
    K_F1          : 'SLEEP',
    K_HOME        : 'MENU',
    K_g           : 'GUIDE',
    K_ESCAPE      : 'EXIT',
    K_UP          : 'UP',
    K_DOWN        : 'DOWN',
    K_LEFT        : 'LEFT',
    K_RIGHT       : 'RIGHT',
    K_SPACE       : 'SELECT',
    K_F2          : 'POWER',
    K_F3          : 'MUTE',
    K_PLUS        : 'VOL+',
    K_MINUS       : 'VOL-',
    K_c           : 'CH+',
    K_v           : 'CH-',
    K_1           : '1',
    K_2           : '2',
    K_3           : '3',
    K_4           : '4',
    K_5           : '5',
    K_6           : '6',
    K_7           : '7',
    K_8           : '8',
    K_9           : '9',
    K_0           : '0',
    K_d           : 'DISPLAY',
    K_e           : 'ENTER',
    K_UNDERSCORE  : 'PREV_CH',
    K_o           : 'PIP_ONOFF',
    K_w           : 'PIP_SWAP',
    K_i           : 'PIP_MOVE',
    K_F4          : 'TV_VCR',
    K_r           : 'REW',
    K_p           : 'PLAY',
    K_f           : 'FFWD',
    K_u           : 'PAUSE',
    K_s           : 'STOP',
    K_F6           : 'REC',
    K_PERIOD      : 'EJECT'
    }

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

    _started = 0
    
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
        self.bitmapcache = []
        
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE
        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 0, 32)

        self.clearscreen(self.COL_WHITE)
        self.update()

        self._started = 1
        self._help = 0  # Is the helpscreen displayed or not
        self._help_saved = pygame.Surface((width, height), 0, 32)
        self._help_last = 0
        

    def _cb(self):
        event = pygame.event.poll()
        if event.type == NOEVENT:
            return None
        
        #print 'SDL: Got event %s' % event

        #if event.type == MOUSEBUTTONDOWN:
        #    self._helpscreen()
            
        if event.type == KEYDOWN:
            if event.key in cmds_sdl:
                return cmds_sdl[event.key]

    
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
        self._getbitmap(filename)
    

    # Loads and zooms a bitmap without copying it to the OSD drawing
    # buffer.
    def zoombitmap(self, filename, scaling=None, bbx=0, bby=0, bbw=0, bbh=0):
        pass # XXX Fix later
    
        
    # Draw a bitmap on the OSD. It is automatically loaded into the cache
    # if not already there. The loadbitmap()/zoombitmap() functions can
    # be used to "pipeline" bitmap loading/drawing.
    def drawbitmap(self, filename, x=0, y=0, scaling=None,   # XXX scale, zoom, tile not supported yet!
                   bbx=0, bby=0, bbw=0, bbh=0):

        image = self._getbitmap(filename)

        if not image: return

        if bbx or bby:
            imbb = pygame.Surface((bbw, bbh), 0, 32)
            imbb.blit(image, (0, 0), (bbx, bby, bbw, bbh))
            image = imbb
            
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
        
        if color == None:
            color = self.default_fg_color
            
        if width == None:
            width = 1

        if width == -1 or fill:
            r,g,b,a = self._sdlcol(color)
            w = x1 - x0
            h = y1 - y0
            box = pygame.Surface((w, h), 0, 32)
            box.fill((r,g,b))
            box.set_alpha(a)
            self.screen.blit(box, (x0, y0))
        else:
            r = (x0, y0, x1-x0, y1-y0)
            c = self._sdlcol(color)
            pygame.draw.rect(self.screen, c, r, width)
            

    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0):

        print 'drawstring "%s"' % string
        
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize * 1.3333)  # XXX The osd_sdl.py fonts are smaller,
        # I think that is because the osd_server screenres is 100 dpi, and here
        # it is 75.

        f = self._getfont(font, ptsize)

        # Render string with anti-aliasing
        if bgcolor == None:
            ren = f.render(string, 1, self._sdlcol(fgcolor))
        else:
            ren = f.render(string, 1, self._sdlcol(fgcolor), self._sdlcol(bgcolor))

        self.screen.blit(ren, (x, y))


    # Return a (width, height) tuple for the given string, font, size
    def stringsize(self, string, font=None, ptsize=0):
        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize * 1.3333)  # XXX The osd_sdl.py fonts are smaller,
        # I think that is because the osd_server screenres is 100 dpi, and here
        # it is 75.

        f = self._getfont(font, ptsize)

        if string:
            return f.size(string)
        else:
            return (0, 0)
        

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

        
    def _getbitmap(self, filename):
        for i in range(len(self.bitmapcache)):
            fname, image = self.bitmapcache[i]
            if fname == filename:
                # Move to front of FIFO
                del self.bitmapcache[i]
                self.bitmapcache.append((fname, image))
                return image

        try:
            image = pygame.image.load(filename).convert_alpha()  # XXX Cannot load everything
        except:
            print 'SDL image load problem!'
            return None

        # FIFO for images
        self.bitmapcache.append((filename, image))
        if len(self.bitmapcache) > 30:
            del self.bitmapcache[0]

        return image

    
    def _helpscreen(self):

        if time.time() > self._help_last + 1:
            self._help = {0:1, 1:0}[self._help]
        else:
            return

        self._help_last = time.time()
        
        if self._help:
            if DEBUG: print 'Help on'
            # Save current display
            self._help_saved.blit(self.screen, (0, 0))
            self.clearscreen(self.COL_WHITE)
            self.drawstring('FREEVO keyboard commands will be added here later on....', 10, 10)

            self.update()
            return # XXX Test, crashes below
            lines = help_text.split('\n')

            row = 0
            col = 0
            for line in lines:
                x = 30 + col*200
                y = 50 + row*30

                ks = line[:8]
                cmd = line[8:]
                
                print '"%s" "%s" %s %s' % (ks, cmd, x, y)
                if ks: self.drawstring(ks, x, y)
                if cmd: self.drawstring(cmd, x+100, y)
                row += 1
                if row >= 15:
                    row = 0
                    col += 1

            self.update()
        else:
            if DEBUG: print 'Help off'
            self.screen.blit(self._help_saved, (0, 0))
            self.update()

        
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

