#if 0 /*
# -----------------------------------------------------------------------
# osd.py - Low level graphics routines
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.24  2003/03/20 19:27:19  dischi
# Fix drawstringframedhard: the ellipses must fit the width, too
#
# Revision 1.23  2003/03/15 10:15:43  dischi
# Faster caching and there is no need for fchksum anymore
#
# Revision 1.22  2003/03/11 20:24:06  dischi
# Fixed some return values
#
# Revision 1.21  2003/03/06 21:06:04  dischi
# catch empty strings first
#
# Revision 1.20  2003/03/01 17:27:29  dischi
# *** empty log message ***
#
# Revision 1.19  2003/03/01 17:26:40  dischi
# _getbitmap now generates and stores thumbnails for large images without
# EXIF header and thumb:// in the url. This speeds up the image menu
# (and most of it the extended version). This requires fchksum (should
# be added to the runtime)
#
# Revision 1.18  2003/02/24 06:00:30  outlyer
# Allow update to optionally use a screen region rather than flipping the whole
# display.
#
# Revision 1.17  2003/02/19 16:59:39  outlyer
# Changing a stray print into a 'debug' to match the rest of the OSD.
#
# Revision 1.16  2003/02/18 23:08:25  rshortt
# Hooking up the code in src/gui.  Added osd.focused_app to keep track of
# what should first receive the events.  In main this is set to be the
# menuwidget which is the parent UI object.  I also made MenuWidget into
# a subclass of GUIObject so that it can closely take advantage of the
# parent / child relationship therein.
#
# Revision 1.15  2003/02/18 07:27:23  gsbarbieri
# Corrected the misspelled 'elipses' -> 'ellipses'
# Now, main1_video uses osd.drawtext(mode='soft') to render text, so it should be better displayed
#
# Revision 1.14  2003/02/18 05:48:55  gsbarbieri
# osd.drawstring*() now has the elipses param, which will be used when the text doesn't fit.
# You can set it to None, so it doesn't show anything when the text doesn't fit.
# The default is '...'
#
# Revision 1.13  2003/02/15 20:48:41  dischi
# drawbitmap can now draw surfaces, too
#
# Revision 1.12  2003/02/12 10:38:51  dischi
# Added a patch to make the current menu system work with the new
# main1_image.py to have an extended menu for images
#
# Revision 1.11  2003/02/03 04:38:35  krister
# Made pygame init explicit to avoid mixer problems.
#
# Revision 1.10  2003/02/03 03:05:23  outlyer
# We raise an exception in _renderstring, but we don't seem to do anything
# with it, which of course equals horrifying crash. I'm trapping it, printing
# an error to the logs and skipping... it only seemed to happen with a few
# mp3s I have, but a crash is a crash...
#
# Revision 1.9  2003/01/31 02:09:00  krister
# Changed the X11 display option to automatically select between xv,x11,etc.
#
# Revision 1.8  2003/01/24 04:48:59  krister
# Changed keyboard volume +/- keys
#
# Revision 1.7  2003/01/17 03:50:21  krister
# Doh! The X11 menus were slow because of stupid SDL event handling, fixed!
#
# Revision 1.6  2003/01/13 00:34:20  krister
# Applied Thomas Schuppels patch for improved bitmap handling.
#
# Revision 1.5  2003/01/07 07:17:07  krister
# Added Thomas Sch¸ppels objectcache layer for the OSD objects.
#
# Revision 1.4  2002/12/21 17:26:52  dischi
# Added dfbmga support. This includes configure option, some special
# settings for mplayer and extra overscan variables
#
# Revision 1.3  2002/12/12 11:45:02  dischi
# Moved all icons to skins/icons
#
# Revision 1.2  2002/11/26 22:02:10  dischi
# Added key to enable/disable subtitles. This works only with mplayer pre10
# (maybe pre9). Keyboard: l (for language) or remote SUBTITLE
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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

import socket
import time
import sys
import os
import stat
import Image
import re
import traceback
from types import *
import urllib
import urlparse
import objectcache
import util
import md5

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The PyGame Python SDL interface.
import pygame
from pygame.locals import *

# Set to 1 for debug output. A lot of the debug statements are only
# printed if set to 3 or higher.
DEBUG = config.DEBUG

help_text = """\
h       HELP
z       Toggle Fullscreen
F1      SLEEP
HOME    MENU
g       GUIDE
ESCAPE  EXIT
UP      UP
DOWN    DOWN
LEFT    LEFT
RIGHT   RIGHT
SPACE   SELECT
RETURN  SELECT
F2      POWER
F3      MUTE
n/KEYP- VOL-
m/KEYP+ VOL+
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
F10     Screenshot
L       Subtitle
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
    K_RETURN      : 'SELECT',
    K_F2          : 'POWER',
    K_F3          : 'MUTE',
    K_KP_MINUS    : 'VOL-',
    K_n           : 'VOL-',
    K_KP_PLUS     : 'VOL+',
    K_m           : 'VOL+',
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
    K_F6          : 'REC',
    K_PERIOD      : 'EJECT',
    K_l           : 'SUBTITLE'
    }

# Module variable that contains an initialized OSD() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = SynchronizedObject(OSD())
        
    return _singleton

        
#
# Return a unicode representation of a String or Unicode object
#
def stringproxy(str):
    result = str
    try:
        if type(str) == StringType:
            result = unicode(str, 'unicode-escape')
    except:
        pass
    return result


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

    stringsize_cache = { }


    def __init__(self):

        self.focused_app = None

        self.fontcache = objectcache.ObjectCache(300, desc='font')
        self.stringcache = objectcache.ObjectCache(100, desc='string')
        self.bitmapcache = objectcache.ObjectCache(30, desc='bitmap')
        
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE

        self.width = config.CONF.width
        self.height = config.CONF.height

        if config.CONF.display== 'dxr3':
            os.environ['SDL_VIDEODRIVER'] = 'dxr3'

        if config.CONF.display == 'dfbmga':
            os.environ['SDL_VIDEODRIVER'] = 'directfb'

        # Initialize the PyGame modules.
        pygame.display.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)

        if config.CONF.display == 'x11' and config.START_FULLSCREEN_X == 1:
            pygame.display.toggle_fullscreen()

        help = ['z = Toggle Fullscreen']
        help += ['Arrow Keys = Move']
        help += ['Spacebar = Select']
        help += ['Escape = Stop/Prev. Menu']
        help += ['h = Help']
        help_str = '    '.join(help)
        pygame.display.set_caption('Freevo' + ' '*7 + help_str)
        icon = pygame.image.load('skins/icons/misc/freevo_app.png').convert()
        pygame.display.set_icon(icon)
        
        self.clearscreen(self.COL_BLACK)
        self.update()

        if config.OSD_SDL_EXEC_AFTER_STARTUP:
            if os.path.isfile(config.OSD_SDL_EXEC_AFTER_STARTUP):
                os.system(config.OSD_SDL_EXEC_AFTER_STARTUP)
            else:
                print "ERROR: %s: no such file" % config.OSD_SDL_EXEC_AFTER_STARTUP

        self.sdl_driver = pygame.display.get_driver()

        pygame.mouse.set_visible(0)
        self.mousehidetime = time.time()
        
        self._started = 1
        self._help = 0  # Is the helpscreen displayed or not
        self._help_saved = pygame.Surface((self.width, self.height), 0, 32)
        self._help_last = 0

        # Remove old screenshots
        os.system('rm -f /tmp/freevo_ss*.bmp')
        self._screenshotnum = 1
        

    def _cb(self):

        if not pygame.display.get_init():
            return None

        # Check if mouse should be visible or hidden
        mouserel = pygame.mouse.get_rel()
        mousedist = (mouserel[0]**2 + mouserel[1]**2) ** 0.5

        if mousedist > 4.0:
            pygame.mouse.set_visible(1)
            self.mousehidetime = time.time() + 1.0  # Hide the mouse in 2s
        else:
            if time.time() > self.mousehidetime:
                pygame.mouse.set_visible(0)

        # Return the next key event, or None if the queue is empty.
        # Everything else (mouse etc) is discarded.
        while 1:
            event = pygame.event.poll()

            if event.type == NOEVENT:
                return None

            if event.type == KEYDOWN:
                if event.key == K_h:
                    self._helpscreen()
                elif event.key == K_z:
                    pygame.display.toggle_fullscreen()
                elif event.key == K_F10:
                    # Take a screenshot
                    pygame.image.save(self.screen,
                                      '/tmp/freevo_ss%s.bmp' % self._screenshotnum)
                    self._screenshotnum += 1
                elif event.key in cmds_sdl.keys():
                    # Turn off the helpscreen if it was on
                    if self._help:
                        self._helpscreen()

                    return cmds_sdl[event.key]

    
    def _send(arg1, *arg, **args): # XXX remove
        pass

    
    def shutdown(self):
        pygame.quit()

    def restartdisplay(self):
        pygame.display.init()
        self.width = config.CONF.width
        self.height = config.CONF.height
        self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)

    def stopdisplay(self):
        pygame.display.quit()

    def clearscreen(self, color=None):
        if not pygame.display.get_init():
            return None

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
        return self._getbitmap(filename)
    
    # Zooms a Surface. It gets a Pygame Surface which is rotated and scaled according
    # to the parameters.
    def zoomsurface(self, image, scaling=None, bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
        if not image:
            return None
        
        if bbx or bby or bbw or bbh:
            imbb = pygame.Surface((bbw, bbh), 0, 32)
            imbb.blit(image, (0, 0), (bbx, bby, bbw, bbh))
            image = imbb

        if scaling:
            w, h = image.get_size()
            w = int(w*scaling)
            h = int(h*scaling)
            if rotation:
                image = pygame.transform.rotozoom(image, rotation, scaling)
            else:
                image = pygame.transform.scale(image, (w, h))

        elif rotation:
            image = pygame.transform.rotate(image, rotation)

        return image
    

    # Loads, zooms a bitmap and returns the surface. A cache is currently
    # missing, but maybe we don't need it, it's fast enough.
    def zoombitmap(self, filename, scaling=None, bbx=0, bby=0, bbw=0,
                   bbh=0, rotation = 0):
        if not pygame.display.get_init():
            return None
        image = self._getbitmap(filename)
        if not image: return
        return self.zoomimage(image, scaling, bbx, bby, bbw, bbh, rotation)

    
    # scales and rotates a surface and then draws it to the screen.
    def drawsurface(self, image, x=0, y=0, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0, rotation = 0, layer=None):
        if not pygame.display.get_init():
            return None
        image = self.zoomsurface(image, scaling, bbx,
                                 bby, bbw, bbh, rotation)
        if not image: return
        if layer:
            layer.blit(image, (x, y))
        else:
            self.screen.blit(image, (x, y))
            

    # Draw a bitmap on the OSD. It is automatically loaded into the cache
    # if not already there. The loadbitmap()/zoombitmap() functions can
    # be used to "pipeline" bitmap loading/drawing.
    def drawbitmap(self, image, x=0, y=0, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0, rotation = 0, layer=None):
        if not pygame.display.get_init():
            return None
        if not isinstance(image, pygame.Surface):
            image = self._getbitmap(image)
        self.drawsurface(image, x, y, scaling, bbx, bby, bbw,
                         bbh, rotation, layer)


    # returns the size of the bitmap given by a filename
    def bitmapsize(self, filename):
        if not pygame.display.get_init():
            return None
        image = self._getbitmap(filename)
        if not image:
            return 0, 0
        return image.get_size()


    def drawline(self, x0, y0, x1, y1, width=None, color=None):
        if not pygame.display.get_init():
            return None
        if width == None:
            width = 1

        if color == None:
            color = self.default_fg_color

        args1 = str(x0) + ';' + str(y0) + ';'
        args2 = str(x1) + ';' + str(y1) + ';' + str(width) + ';' + str(color)
        self._send('drawline;' + args1 + args2)


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0, layer=None):
        if not pygame.display.get_init():
            return None

        # Make sure the order is top left, bottom right
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
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
            if layer:
                layer.blit(box, (x0, y0))
            else:
                self.screen.blit(box, (x0, y0))
        else:
            r = (x0, y0, x1-x0, y1-y0)
            c = self._sdlcol(color)
            if layer:
                pygame.draw.rect(layer, c, r, width)
            else:
                pygame.draw.rect(self.screen, c, r, width)

    def getsurface(self, x, y, width, height):
        s = pygame.Surface((width, height))
        s.blit(self.screen, (0,0), (x, y, width, height))
        return s
    
    def putsurface(self, surface, x, y):
        self.screen.blit(surface, (x, y))


    # Gustavo:
    # drawstringframed: draws a string (text) in a frame. This tries to fit the
    #                   string in lines, if it can't, it truncates the text,
    #                   draw the part that fit and returns the other that doesn't.
    #                   This is a wrapper to drawstringframedsoft() and -hard()
    #                       
    # Parameters:
    #  - string: the string to be drawn. Supports '\n' and '\t' too.
    #  - x,y: the posistion
    #  - width, height: the frame dimensions (See TIPS above)
    #  - fgcolor, bgcolor: the color for the foreground and background
    #       respectively. (Supports the alpha channel: 0xAARRGGBB)
    #  - font, ptsize: font and font point size
    #  - align_h: horizontal align. Can be left, center, right, justified
    #  - align_v: vertical align. Can be top, bottom, center or middle
    #  - mode: the way we should break lines/truncate. Can be 'hard'(based on chars)
    #       or 'soft' (based on words)
    #
    # TIPS:
    #  - height = -1 defaults to the font height size
    #
    # TODO:
    #  - Test it
    #  - Debug it
    #  - Improve it
    def drawstringframed(self, string, x, y, width, height, fgcolor=None, bgcolor=None,
                         font=None, ptsize=0, align_h='left', align_v='top', mode='hard',
                         layer=None, ellipses='...'):
        if mode == 'hard':
            return self.drawstringframedhard(string,x,y,width, height, fgcolor, bgcolor,
                                             font, ptsize, align_h, align_v, layer, ellipses)
        elif mode == 'soft':
            return self.drawstringframedsoft(string,x,y,width, height, fgcolor, bgcolor,
                                             font, ptsize, align_h, align_v, layer, ellipses)

    # Gustavo:
    # drawstringframedsoft: draws a string (text) in a frame. This tries to fit the
    #                       string in lines, if it can't, it truncates the text,
    #                       draw the part that fit and returns the other that doesn't.
    #                       Different from drawstringframedhard from the way it truncates
    #                       the line. This one breaks based on words, not chars.
    #                       
    # Parameters:
    #  - string: the string to be drawn. Supports '\n' and '\t' too.
    #  - x,y: the posistion
    #  - width, height: the frame dimensions (See TIPS above)
    #  - fgcolor, bgcolor: the color for the foreground and background
    #       respectively. (Supports the alpha channel: 0xAARRGGBB)
    #  - font, ptsize: font and font point size
    #  - align_h: horizontal align. Can be left, center, right, justified
    #  - align_v: vertical align. Can be top, bottom, center or middle
    #
    # TIPS:
    #  - height = -1 defaults to the font height size
    #
    # TODO:
    #  - Test it
    #  - Debug it
    #  - Improve it
    def drawstringframedsoft(self, string, x, y, width, height, fgcolor=None, bgcolor=None,
                         font=None, ptsize=0, align_h='left', align_v='top', layer=None, ellipses='...'):

        if not pygame.display.get_init():
            return string

        return_x0 = 0
        return_y0 = 0
        return_x1 = 0
        return_y1 = 0

        if DEBUG >= 3:
            print 'drawstringframed (%d;%d; w=%d; h=%d) "%s"' % (x, y,
                                                                 width,
                                                                 height,
                                                                 string)
        
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE


        if DEBUG >= 3:
            print 'FONT: %s %s' % (font, ptsize)        

        #
        # calculate words per line
        #
        MINIMUM_SPACE_BETWEEN_WORDS, tmp = self.stringsize(' ',font,ptsize)
        line = []
        s = string.replace('\t',' \t ')
        s = s.replace('\n',' \n ')
        s = s.replace('  ',' ')
        s = re.sub(r'([ ]$)','',s)
        s = re.sub(r'(^[ ])','',s)
        if s == '': # string was only a space ' '
            return s, (0,0,0,0)
        words = s.split(' ')
        occupied_size = 0
        line_number = 0
        lines = []
        lines.append([])
        lines_size = []
        lines_size.append(0)
        len_words = len(words)
        word_size = 0
        word_height = 0
        occupied_height = 0
        next_word_size = 0
        next_word_height = 0
        # First case: height is fewer than the necessary        
        word_size, word_height = self.stringsize('Agj',font,ptsize)
        line_height = word_height
        occupied_height = line_height
        if height == -1:
            height = line_height
        if line_height > height:
            return string, (0,0,0,0)
        # Fit words in lines
        rest_words = ''
        for word_number in range(len_words):
            if words[word_number] == '\n' and len(lines[line_number]) > 0:
                line_number += 1
                lines.append([])
                lines_size.append(0)
                occupied_size = 0
                occupied_height += line_height
            else:
                if words[word_number] == '\t':
                    words[word_number] = '   '
                word_size, word_height = self.stringsize(words[word_number], font,ptsize)
                # This word fit in this line?                
                if (occupied_size + word_size) <= width and ( occupied_height ) <= height:
                    # Yes, add it to this line word's list
                    lines[line_number].append(words[word_number])
                    occupied_size += word_size
                    lines_size[line_number] = occupied_size
                    if word_number+1 < len_words:
                        next_word_size , next_word_height = self.stringsize(words[word_number+1], font,ptsize)
                    occupied_size += MINIMUM_SPACE_BETWEEN_WORDS
                elif ( occupied_height + line_height ) <= height:
                    # No, but we can add another line
                    # Is this word larger than the width?
                    if word_size > width:
                        tmp_occupied_size = 0
                        tmp_size, tmp_height = self.stringsize('-',font,ptsize)
                        # Yes, break it
                        tmp_pieces = words[word_number]
                        # The chars where we can split words (making it less ugly to read)
                        tmp_pieces = re.sub(r'(?P<str>[aeiouAEIOU·ÈÌÛ˙¡…Õ”⁄‡ËÏÚ˘¿»Ã“Ÿ„ı√’‰ÎÔˆ¸ƒÀœ÷‹‚ÍÓÙ˚¬ Œ‘€!@#$%\*\(\)\\/\-~`\'"\?\.,\[\]]+)',' \g<str> ',tmp_pieces)
                        tmp_pieces = tmp_pieces.replace('  ',' ')                     
                        tmp_pieces = re.sub(r'([ ]$)','',tmp_pieces)
                        tmp_pieces = re.sub(r'(^[ ])','',tmp_pieces)
                        pieces = []
                        tmp_pieces = tmp_pieces.split(' ')
                        # check if any pieces still is larger than the width
                        for i in range(len(tmp_pieces)):
                            next_word_size, next_word_height = self.stringsize(tmp_pieces[i],font,ptsize)
                            if next_word_size > (width - tmp_size):                                
                                for j in range(next_word_size / (width-tmp_size)):
                                    pieces.append(tmp_pieces[i][(j-1)*(width-tmp_size):j*(width-tmp_size)])
                            else:
                                pieces.append(tmp_pieces[i])
                        line_number += 1
                        occupied_height += line_height
                        lines.append([])                        
                        lines[line_number].append('')
                        lines_size.append(0)
                        for i in range(len(pieces)):
                            next_word_size, next_word_height = self.stringsize(pieces[i],font,ptsize)
                            if (next_word_size + tmp_occupied_size) < (width - tmp_size) and occupied_height <= height:
                                lines[line_number][0] += pieces[i]
                                tmp_occupied_size += next_word_size                                
                                lines_size[line_number] = tmp_occupied_size
                            elif (occupied_height + line_height) <= height:
                                # we can add another line
                                lines[line_number][0] += '-'
                                lines_size[line_number] += tmp_size + MINIMUM_SPACE_BETWEEN_WORDS
                                lines.append([])
                                line_number += 1
                                lines[line_number].append(pieces[i])
                                lines_size.append(tmp_occupied_size)
                                tmp_occupied_size = next_word_size
                                occupied_height += line_height
                            else:
                                # No, and we cannot add another line, truncate this text
                                # and save text that does not fit
                                next_word_size , next_word_height = self.stringsize('-', font,ptsize)
                                # We need to remove the last piece to place the '...' ?
                                if (occupied_size + next_word_size) <= width:
                                    # No, just add it
                                    lines[line_number][0] += '-'
                                    lines_size[line_number] += next_word_size
                                else:
                                    # Yes, put '-' in the last piece place
                                    lines[line_number][0][0:len(lines[line_number][0])-4] += '-'                           
                                    tmp_word_size , tmp_word_height = self.stringsize(lines[line_number][0], font,ptsize)
                                    lines_size[line_number] = tmp_word_size  + MINIMUM_SPACE_BETWEEN_WORDS
                                    # save the text that does not fit.
                                for tmp in range(word_number, len(pieces)):
                                    try:
                                        rest_words += words[tmp]
                                        if tmp < len_words: rest_words += ' '
                                    except IndexError:
                                        continue
                                    # quit the loop
                                break
                        occupied_size = lines_size[line_number]
                    else:
                        # No, just add it
                        line_number += 1
                        lines.append([])
                        lines[line_number].append(words[word_number])
                        lines_size.append(word_size)
                        occupied_size = word_size + MINIMUM_SPACE_BETWEEN_WORDS
                        occupied_height += line_height
                else:
                    # No, and we cannot add another line, truncate this text
                    # and save text that does not fit
                    next_word_size , next_word_height = self.stringsize(ellipses, font,ptsize)
                    if ellipses:
                        # We need to remove the last word to place the '...' ?
                        if (occupied_size + next_word_size) <= width:
                            # No, just add it
                            lines[line_number].append(ellipses)
                            lines_size[line_number] += next_word_size + MINIMUM_SPACE_BETWEEN_WORDS
                        else:
                            # Yes, put '...' in the last word place
                            if len(lines[line_number]) > 0:
                                lines[line_number][len(lines[line_number])-1] = '...'
                            else:
                                lines[line_number].append('...')

                            tmp_word_size , tmp_word_height = self.stringsize(lines[line_number][len(lines[line_number])-1], font,ptsize)                        
                            lines_size[line_number] += next_word_size - tmp_word_size  + MINIMUM_SPACE_BETWEEN_WORDS
                    # save the text that does not fit.
                    for tmp in range(word_number, len_words):
                        rest_words += words[tmp]                        
                        if tmp < len_words: rest_words += ' '
                    # quit the loop
                    break

        # now draw the string
        y0 = y
        if align_v == 'top':
            y0 = y
        elif align_v == 'center' or align_v == 'middle':
            y0 = y + (height - line_height * len(lines)) / 2
        elif align_v == 'bottom':
            y0 = y + (height - line_height * len(lines))


        if not return_y0:
            return_y0 = y0

        if DEBUG >= 3:
            print "osd.drawstringframed_soft():\n\n%s\n" % lines

        if bgcolor != None:
            self.drawbox(x,y, x+width, y+height, width=-1, color=bgcolor, layer=layer)
        for line_number in range(len(lines)):
            x0 = x
            #print "WORDS: %s" % lines[line_number]
            spacing = MINIMUM_SPACE_BETWEEN_WORDS
            if align_h == 'justified':
                # Calculate the space between words:
                ## Disconsider the minimum space
                x0 = x                    
                if not return_x0 or return_x0 > x0:
                    return_x0 = x0
                lines_size[line_number] -= MINIMUM_SPACE_BETWEEN_WORDS * \
                                           (len(lines[line_number]) -1 )
                if len(lines[line_number]) > 1:
                    spacing = (width - lines_size[line_number]) / \
                              ( len(lines[line_number]) -1 )
                else:
                    spacing = (width - lines_size[line_number]) / 2
                    x0 += spacing
                for word in lines[line_number]:
                    if word:
                        word_size, word_height = self.stringsize(word, font,ptsize)
                        self.drawstring(word, x0, y0, fgcolor, None, font, ptsize, layer=layer)
                        x0 += spacing
                        x0 += word_size
                    
            elif align_h == 'center':
                x0 = x + (width - lines_size[line_number]) / 2
                if not return_x0 or return_x0 > x0:
                    return_x0 = x0
                spacing = MINIMUM_SPACE_BETWEEN_WORDS                
                for word in lines[line_number]:
                    if word:
                        word_size, word_height = self.stringsize(word, font,ptsize)
                        self.drawstring(word, x0, y0, fgcolor, None, font, ptsize, layer=layer)
                        x0 += spacing
                        x0 += word_size
            elif align_h == 'left':
                x0 = x
                if not return_x0 or return_x0 > x0:
                    return_x0 = x0
        
                spacing = MINIMUM_SPACE_BETWEEN_WORDS
                for word in lines[line_number]:
                    if word:
                        word_size, word_height = self.stringsize(word, font,ptsize)
                        self.drawstring(word, x0, y0, fgcolor, None, font, ptsize, layer=layer)
                        x0 += spacing
                        x0 += word_size
            elif align_h == 'right':
                x0 = x + width
                if not return_x0 or return_x0 > x0:
                    return_x0 = x0
                spacing = MINIMUM_SPACE_BETWEEN_WORDS
                line_len = len(lines[line_number])
                for word_number in range(len(lines[line_number])):
                    if word:
                        pos = line_len - word_number -1
                        word_size, word_height = \
                                   self.stringsize(lines[line_number][pos], font,ptsize)
                        self.drawstring(lines[line_number][pos], x0, y0, fgcolor, \
                                        None, font, ptsize, 'right', layer=layer)
                        x0 -= spacing
                        x0 -= word_size
            # end if 
            # go down one line
            if not return_x1 or return_x1 < x0:
                return_x1 = x0
        
            y0 += line_height
            return_y1 = y0
        # end for

        #self.drawbox(return_x0,return_y0, return_x1, return_y1, width=3)

        return (rest_words, (return_x0,return_y0, return_x1, return_y1))



    # Gustavo:
    # drawstringframedhard: draws a string (text) in a frame. This tries to fit the
    #                       string in lines, if it can't, it truncates the text,
    #                       draw the part that fit and returns the other that doesn't.
    #                       Different from drawstringframedsoft from the way it truncates
    #                       the line. This one breaks based on chars, not words.
    # Parameters:
    #  - string: the string to be drawn. Supports '\n' and '\t' too.
    #  - x,y: the posistion
    #  - width, height: the frame dimensions (See TIPS above)
    #  - fgcolor, bgcolor: the color for the foreground and background
    #       respectively. (Supports the alpha channel: 0xAARRGGBB)
    #  - font, ptsize: font and font point size
    #  - align_h: horizontal align. Can be left, center, right
    #  - align_v: vertical align. Can be top, bottom, center or middle
    #
    # TIPS:
    #  - height = -1 defaults to the font height size
    #
    # TODO:
    #  - Test it
    #  - Debug it
    #  - Improve it
    def drawstringframedhard(self, string, x, y, width, height, fgcolor=None, bgcolor=None,
                             font=None, ptsize=0, align_h='left', align_v='top',
                             layer=None, ellipses='...'):

        if not pygame.display.get_init():
            return string

        return_x0 = 0
        return_y0 = 0
        return_x1 = 0
        return_y1 = 0

        if DEBUG >= 3:
            print 'drawstringframedhard (%d;%d; w=%d; h=%d) "%s"' % (x, y, width,
                                                                     height, string)

        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE


        if DEBUG >= 3:
            print 'FONT: %s %s' % (font, ptsize)        

        occupied_size = 0
        occupied_height = 0
        # First case: height is fewer than the necessary        
        word_size, word_height = self.stringsize('Agj',font,ptsize)
        line_height = word_height
        occupied_height = line_height
        if height == -1:
            height = line_height
        if line_height > height:
            return string
        
        # Fit chars in lines
        lines = [ '' ]
        line_number = 0
        ellipse_size = self.stringsize(ellipses, font, ptsize)[0]
        for i in range(len(string)):
            char_size, char_height = self.charsize(string[i], font, ptsize)
            if ((occupied_size + char_size + ellipse_size) <= width) and (string[i] != '\n'):
                occupied_size += char_size
                if string[i] == '\t':
                    lines[line_number] += '   '
                else:
                    lines[line_number] += string[i] 
            else:
                if (occupied_height + char_height) <= height:
                    occupied_height += word_height
                    line_number += 1
                    lines += [ '' ]
                    if string[i] == '\n':
                        # Linebreak due to CR
                        occupied_size = 0
                    else:
                        # Linebreak due to the last character didn't fit,
                        # put it on the next line
                        occupied_size = char_size
                        lines[line_number] = string[i]
                else:
                    j = 1
                    len_line = len(lines[line_number])
                    for j in range(len_line):
                        if (occupied_size + ellipse_size) <= width:
                            break
                        char_size = self.charsize(lines[line_number][len_line-j-1],
                                                  font, ptsize)[0]
                        occupied_size -= char_size
                    lines[line_number] = lines[line_number][0:len_line-j]
                    if ellipses:
                        while ellipses and ellipse_size >= width:
                            ellipses = ellipses[:-1]
                            ellipse_size = self.stringsize(ellipses, font, ptsize)[0]
                        lines[line_number] += ellipses
                    break
        rest_words = string[i:len(string)]

        if bgcolor != None:
            self.drawbox(x,y, x+width, y+height, width=-1, color=bgcolor, layer=layer)

        y0 = y
        if align_v == 'center' or align_v == 'middle':
            y0 = y + (height - (line_number+1) * word_height)/ 2
        elif align_v == 'bottom':
            y0 = y + (height - (line_number+1) * word_height)
        
        for line in lines:
            # FIXME:
            # shorten line, maybe it's too long. It may be ellipses, but
            # sometimes it also too long, don't know why.
            #while line and self.stringsize(line, font, ptsize)[0] > width:
            #    line = line[:-1]
            if align_h == 'left':
                x0 = x
            elif align_h == 'center' or align_h == 'justified':
                line_size, line_heigt = self.stringsize(line, font, ptsize)
                x0 = x + (width - line_size) / 2
            elif align_h == 'right':
                line_size, line_heigt = self.stringsize(line, font, ptsize)
                x0 = x + (width - line_size)
            self.drawstring(line, x0, y0, fgcolor, None, font, ptsize, layer=layer)
            y0 += word_height

        return (rest_words, (return_x0,return_y0, return_x1, return_y1))



                    

    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0, align='left', layer=None):

        if not pygame.display.get_init():
            return None

        if not string:
            return None

        # XXX Krister: Workaround for new feature that is only possible in the new
        # XXX SDL OSD, line up columns delimited by tabs. Here the tabs are just
        # XXX replaced with spaces
        s = string.replace('\t', '   ')  

        if DEBUG >= 3:
            print 'drawstring (%d;%d) "%s"' % (x, y, s)
        
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies by 0.7 for some reason

        if DEBUG >= 3:
            print 'FONT: %s %s' % (font, ptsize)

        try:        
            ren = self._renderstring(s, font, ptsize, fgcolor, bgcolor)
        except:
            print "Render failed, skipping..."    
            return None
        
        # Handle horizontal alignment
        w, h = ren.get_size()
        tx = x # Left align is default
        if align == 'center':
            tx = x - w/2
        elif align == 'right':
            tx = x - w
            
        if layer:
            layer.blit(ren, (tx, y))
        else:
            self.screen.blit(ren, (tx, y))


    # Render a string to an SDL surface. Uses a cache for speedup.
    def _renderstring(self, string, font, ptsize, fgcolor, bgcolor):

        if not pygame.display.get_init():
            return None

        f = self._getfont(font, ptsize)

        if not f:
            print 'Couldnt get font: "%s", size: %s' % (font, ptsize)
            return

        # Encode all the strings data into an url so we can enter it
        # nicely into our string-container
        # Format: 
        #  file://path/to/font.ttf?ptsize=55&fgcolor=123536&bgcolor=23142134&string=sometext
        parameters = urllib.urlencode( [('ptsize',ptsize),('fgcolor',fgcolor),
                                 ('bgcolor',bgcolor),('string',string)] )
        url = urlparse.urlunparse( ( 'file', '', font, '', parameters,  '' ) ) 
        surf = self.stringcache[url]
        if surf:
            return surf

        # Render string with anti-aliasing
        if bgcolor == None:
            try:
                surf = f.render(string, 1, self._sdlcol(fgcolor))
            except:
                print 'FAILED: str="%s" col="%s"' % (string, fgcolor)
                raise
        else:
            surf = f.render(string, 1, self._sdlcol(fgcolor), self._sdlcol(bgcolor))

        # Store the surface in the FIFO, Even if it's None?
        self.stringcache[url] = surf
        
        return surf

    # Return a (width, height) tuple for the given char, font, size. Use CACHE to speed up things
    # Gustavo: This function make use of dictionaries to cache values, so we don't have to calculate them all the time
    def charsize(self, char, font=None, ptsize=0):
        if self.stringsize_cache.has_key(font):
            if self.stringsize_cache[font].has_key(ptsize):
                if not self.stringsize_cache[font][ptsize].has_key(char):
                    self.stringsize_cache[font][ptsize][char] = self._stringsize(char,font,ptsize)
            else:
                self.stringsize_cache[font][ptsize] = {}
                self.stringsize_cache[font][ptsize][char] = self._stringsize(char,font,ptsize)
        else:
            self.stringsize_cache[font] = {}
            self.stringsize_cache[font][ptsize] = {}
            self.stringsize_cache[font][ptsize][char] = self._stringsize(char,font,ptsize)
        return self.stringsize_cache[font][ptsize][char]


    # Return a (width, height) tuple for the given string, font, size
    # Gustavo: use the charsize() to speed up things
    def stringsize(self, string, font=None, ptsize=0):
        size_w = 0
        size_h = 0
        if string == None:
            return (0, 0)
        
        for i in range(len(string)):
            size_w_tmp, size_h_tmp = self.charsize(string[i], font, ptsize)
            size_w += size_w_tmp
            if size_h_tmp > size_h:
                size_h = size_h_tmp
                
        return (size_w, size_h)
    

    # Return a (width, height) tuple for the given string, font, size
    # Gustavo: Don't use this function directly. Use stringsize(), it is faster (use cache)
    def _stringsize(self, string, font=None, ptsize=0):
        if not pygame.display.get_init():
            return None

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies with 0.7 for some reason

        f = self._getfont(font, ptsize)

        if string:
            return f.size(string)
        else:
            return (0, 0)

    # create a new layer for drawings
    def createlayer(self, width=0, height=0):
        if not width: width = self.width
        if not height: height = self.height
        
        l = pygame.Surface((width, height), SRCALPHA, 32)
        l.fill((0,0,0,0))
        return l


    # insert layer into the screen
    def putlayer(self, layer, x=0, y=0):
        self.screen.blit(layer, (x, y))


    # help functions to save and restore a pixel
    # for drawcircle
    def _savepixel(self, x, y, s):
        try:
            return (x, y, s.get_at((x,y)))
        except:
            return None
            
    def _restorepixel(self, save, s):
        if save:
            s.set_at((save[0],save[1]), save[2])

    # pygame.draw.circle has a bug: there are some pixels where
    # they don't belong. This function stores the values and
    # restores them
    def drawcircle(self, s, color, x, y, radius):
        p1 = self._savepixel(x-1, y-radius-1, s)
        p2 = self._savepixel(x,   y-radius-1, s)
        p3 = self._savepixel(x+1, y-radius-1, s)

        p4 = self._savepixel(x-1, y+radius, s)
        p5 = self._savepixel(x,   y+radius, s)
        p6 = self._savepixel(x+1, y+radius, s)

        pygame.draw.circle(s, color, (x, y), radius)
        
        self._restorepixel(p1, s)
        self._restorepixel(p2, s)
        self._restorepixel(p3, s)
        self._restorepixel(p4, s)
        self._restorepixel(p5, s)
        self._restorepixel(p6, s)
        
        
    def drawroundbox(self, x0, y0, x1, y1, color=None, border_size=0, border_color=None,
                     radius=0, layer=None):

        if not pygame.display.get_init():
            return None

        # Make sure the order is top left, bottom right
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        if color == None:
            color = self.default_fg_color

        if border_color == None:
            border_color = self.default_fg_color

        if layer:
            x = x0
            y = y0
        else:
            x = 0
            y = 0
            
        w = x1 - x0
        h = y1 - y0

        bc = self._sdlcol(border_color)
        c =  self._sdlcol(color)

        # make sure the radius fits the box
        radius = min(radius, h / 2, w / 2)
        
        if not layer:
            box = pygame.Surface((w, h), SRCALPHA, 32)

            # clear surface
            box.fill((0,0,0,0))
        else:
            box = layer
            
        r,g,b,a = self._sdlcol(color)
        
        if border_size:
            if radius >= 1:
                self.drawcircle(box, bc, x+radius, y+radius, radius)
                self.drawcircle(box, bc, x+w-radius, y+radius, radius)
                self.drawcircle(box, bc, x+radius, y+h-radius, radius)
                self.drawcircle(box, bc, x+w-radius, y+h-radius, radius)
            pygame.draw.rect(box, bc, (x+radius, y, w-2*radius, h))
            pygame.draw.rect(box, bc, (x, y+radius, w, h-2*radius))
        
            x += border_size
            y += border_size
            h -= 2* border_size
            w -= 2* border_size
            radius -= min(0, border_size)
        
        if radius >= 1:
            self.drawcircle(box, c, x+radius, y+radius, radius)
            self.drawcircle(box, c, x+w-radius, y+radius, radius)
            self.drawcircle(box, c, x+radius, y+h-radius, radius)
            self.drawcircle(box, c, x+w-radius, y+h-radius, radius)
        pygame.draw.rect(box, c, (x+radius, y, w-2*radius, h))
        pygame.draw.rect(box, c, (x, y+radius, w, h-2*radius))
        
        if not layer:
            self.screen.blit(box, (x0, y0))



    def update(self,rect=None):
        if not pygame.display.get_init():
            return None
        if rect:
            pygame.display.update(rect)
        else:
            pygame.display.flip()


    def _getfont(self, filename, ptsize):
        if not pygame.display.get_init():
            return None

        url = 'file://%s?%s' % ( filename, urllib.urlencode([('ptsize',ptsize)]) )
        f = self.fontcache[url]
        if f:
            return f.font

        if DEBUG >= 3:
            print 'OSD: Loading font "%s"' % filename
        try:
            font = pygame.font.Font(filename, ptsize)
        except RuntimeError:
            print 'Couldnt load font "%s"' % filename
            if DEBUG >= 2:
                print 'Call stack:'
                traceback.print_stack()
                
            # Are there any alternate fonts defined?
            if not 'OSD_FONT_ALIASES' in dir(config):
                print 'No font aliases defined!'
                raise # Nope
                
            # Ok, see if there is an alternate font to use
            fontname = os.path.basename(filename).lower()
            if fontname in config.OSD_FONT_ALIASES:
                alt_fname = './skins/fonts/' + config.OSD_FONT_ALIASES[fontname]
                print 'trying alternate: %s' % alt_fname
                try:
                    font = pygame.font.Font(alt_fname, ptsize)
                except RuntimeError:
                    print 'Couldnt load alternate font "%s"' % alt_fname
                    raise
            else:
                print 'No alternate found in the alias list!'
                raise
        f = Font()
        f.filename = filename
        f.ptsize = ptsize
        f.font = font
        
        self.fontcache[url] = f

        return f.font

        
    def _getbitmap(self, url):
        # EXIF parser
        from image import exif
        import cStringIO
        
        if not pygame.display.get_init():
            return None

        if url[:8] == 'thumb://':
            filename = url[8:]
        else:
            filename = url
            
        if not os.path.isfile(filename):
            print 'Bitmap file "%s" doesnt exist!' % filename
            return None
            
        image = self.bitmapcache[url]
        if image:
            return image
        
        try:
            thumb = None
            if DEBUG >= 3:
                print 'Trying to load file "%s"' % filename

            if url[:8] == 'thumb://':
                tmp = util.getExifThumbnail(filename)
                if tmp:
                    filename = tmp
                else:
                    sinfo = os.stat(filename)
                    if sinfo[stat.ST_SIZE] > 50000:
                        m = md5.new('%s/%s-%s' % (filename, sinfo[stat.ST_SIZE],
                                                  sinfo[stat.ST_MTIME]))
                        thumb = os.path.join('%s/thumbnails/%s.png' % \
                                             (config.FREEVO_CACHEDIR,
                                              util.hexify(m.digest())))
                    
                        if not os.path.isfile(thumb):
                            # convert with Imaging, pygame doesn't work
                            image = Image.open(filename)
                            width  = 300
                            height = 300

                            w, h = image.size
                            if int(float(width * h) / w) > height:
                                width = int(float(height * w) / h)
                            else:
                                height = int(float(width * h) / w)
                            image = image.resize((width, height), Image.BICUBIC)
                            image.save(thumb, 'PNG')

                        filename = thumb

                            
            tmp = pygame.image.load(filename)  # XXX Cannot load everything
            image = tmp.convert_alpha()  # XXX Cannot load everything

        except pygame.error, e:
            print 'SDL image load problem: %s' % e
            return None
        except:
            print 'Unknown Problem while loading image'
            return None

        # Update cache
        self.bitmapcache[url] = image

        return image

        
    def _helpscreen(self):
        if not pygame.display.get_init():
            return None

        self._help = {0:1, 1:0}[self._help]
        
        if self._help:
            if DEBUG: print 'Help on'
            # Save current display
            self._help_saved.blit(self.screen, (0, 0))
            self.clearscreen(self.COL_WHITE)
            lines = help_text.split('\n')

            row = 0
            col = 0
            for line in lines:
                x = 55 + col*250
                y = 50 + row*30

                ks = line[:8]
                cmd = line[8:]
                
                print '"%s" "%s" %s %s' % (ks, cmd, x, y)
                fname = 'skins/fonts/bluehigh.ttf'
                if ks: self.drawstring(ks, x, y, font=fname, ptsize=14)
                if cmd: self.drawstring(cmd, x+80, y, font=fname, ptsize=14)
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
            


s = ("/hdc/krister_mp3/mp3/rage_against_the_machine-the_battle_of_los_angeles" +
       "-1999-bkf/02-Rage_Against_the_Machine-Guerilla_Radio-BKF.mp3")
#
# Simple test...
#
if __name__ == '__main__':
    osd = OSD()
    osd.clearscreen()
    osd.drawstring(s, 10, 10, font='skins/fonts/bluehigh.ttf', ptsize=14)
    osd.update()
    time.sleep(5)


#
# synchronized objects and methods.
# By AndrÈ Bj‰rby
# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65202
# 
from types import *
def _get_method_names (obj):
    if type(obj) == InstanceType:
        return _get_method_names(obj.__class__)
    
    elif type(obj) == ClassType:
        result = []
        for name, func in obj.__dict__.items():
            if type(func) == FunctionType:
                result.append((name, func))

        for base in obj.__bases__:
            result.extend(_get_method_names(base))

        return result


class _SynchronizedMethod:

    def __init__ (self, method, obj, lock):
        self.__method = method
        self.__obj = obj
        self.__lock = lock

    def __call__ (self, *args, **kwargs):
        self.__lock.acquire()
        try:
            #print 'Calling method %s from obj %s' % (self.__method, self.__obj)
            return self.__method(self.__obj, *args, **kwargs)
        finally:
            self.__lock.release()


class SynchronizedObject:
    
    def __init__ (self, obj, ignore=[], lock=None):
        import threading

        self.__methods = {}
        self.__obj = obj
        lock = lock and lock or threading.RLock()
        for name, method in _get_method_names(obj):
            if not name in ignore:
                self.__methods[name] = _SynchronizedMethod(method, obj, lock)

    def __getattr__ (self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)



