#if 0 /*
# -----------------------------------------------------------------------
# osd.py - Low level graphics routines
#
# This is the class for using the SDL OSD functions. It will eventually
# replace the current osd.py
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.31  2002/10/09 04:54:22  krister
# Removed the workaround for the missing encodings modules in the old runtime.
#
# Revision 1.30  2002/10/08 22:04:28  krister
# Added an error message for when a font cannot be loaded.
#
# Revision 1.29  2002/10/06 14:33:26  dischi
# log message cleanup and fixed a nasty bug in stringproxy
#
# Revision 1.28  2002/10/03 17:34:37  dischi
# Small update to support more resolutions. I tried to get 720x576 working,
# but for some reason I can't see a freevo on my tv, mplayer works fine.
# Strange....
#
# Revision 1.27  2002/09/30 09:28:02  dischi
# small ugly fix to work around the unicode-escape problem. The is only
# a temporal fix to make freevo working again.
#
# Revision 1.26  2002/09/28 04:36:09  krister
# Bugfix for 8-bit chars in bitmap filenames by Alex Polite
#
# Revision 1.25  2002/09/25 01:41:09  gsbarbieri
# Updated osd.drawstringframed() with new break points to words that are
# larger than the width.
# Corrected some bugs in stringsize()
#
# Revision 1.24  2002/09/24 16:33:52  gsbarbieri
# osd.drawstringframed() now supports words larger than width.
#
# Revision 1.23  2002/09/24 06:52:03  gsbarbieri
# Added the new function drawstringframed(). It can draw a string (supporting
# even '\n' and '\t') in the determinated area, with both horizontal and
# vertical alignment. If the string doesn't fit, it's truncated and the part
# that doesn't fit is returned.
# Note: This function was designated to work with *words*, that is, when
# truncating or wrapping, it brokes the string where it find spaces ' '.
# ('\t' is considered a word '   ')
# BUGS: It doesn't work fully when we have a word that is larger than width,
# It overflows the area.
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
import re
from types import *

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The PyGame Python SDL interface.
import pygame
from pygame.locals import *

# Set to 1 for debug output
DEBUG = 0

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
F10     Screenshot
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
    K_F6          : 'REC',
    K_PERIOD      : 'EJECT'
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
    if type(str) == StringType:
        result = unicode(str, 'unicode-escape')
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

        self.fontcache = []
        self.stringcache = []
        self.bitmapcache = []
        
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE

        self.width = config.CONF.width
        self.height = config.CONF.height

        # Initialize the PyGame modules.
        pygame.init()

        # The mixer module must not be running, it will
        # prevent sound from working.
        try:
            pygame.mixer.quit()
        except NotImplementedError, MissingPygameModule:
            pass # Ok, we didn't have the mixer module anyways

        self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)

        help = ['z = Toggle Fullscreen']
        help += ['Arrow Keys = Move']
        help += ['Spacebar = Select']
        help += ['Escape = Stop/Prev. Menu']
        help += ['h = Help']
        help_str = '    '.join(help)
        pygame.display.set_caption('Freevo' + ' '*7 + help_str)
        icon = pygame.image.load('icons/freevo_app.png').convert()
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
        self._getbitmap(filename)
    

    # Loads and zooms a bitmap and return the surface. A cache is currently
    # missing, but maybe we don't need it, it's fast enough.
    def zoombitmap(self, filename, scaling=None, bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
        if not pygame.display.get_init():
            return None

        image = self._getbitmap(filename)

        if not image: return

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

    
        
    # Draw a bitmap on the OSD. It is automatically loaded into the cache
    # if not already there. The loadbitmap()/zoombitmap() functions can
    # be used to "pipeline" bitmap loading/drawing.
    def drawbitmap(self, filename, x=0, y=0, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
        if not pygame.display.get_init():
            return None
        image = self.zoombitmap(filename, scaling, bbx, bby, bbw, bbh, rotation)
        if not image: return
        self.screen.blit(image, (x, y))


    def bitmapsize(self, filename):
        if not pygame.display.get_init():
            return None
        image = self._getbitmap(filename)
        if not image: return 0,0
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


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0):
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
            self.screen.blit(box, (x0, y0))
        else:
            r = (x0, y0, x1-x0, y1-y0)
            c = self._sdlcol(color)
            pygame.draw.rect(self.screen, c, r, width)


    # Gustavo:
    # drawstringframed: draws a string (text) in a frame. This tries to fit the
    #                   string in lines, if it can't, it truncates the text,
    #                   draw the part that fit and returns the other that doesn't
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
    def drawstringframed(self, string, x, y, width, height, fgcolor=None, bgcolor=None,
                         font=None, ptsize=0, align_h='left', align_v='top'):

        if not pygame.display.get_init():
            return string

        if DEBUG: print 'drawstringframed (%d;%d; w=%d; h=%d) "%s"' % (x, y, w, h, s)
        
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies by 0.7 for some reason

        if DEBUG: print 'FONT: %s %s' % (font, ptsize)        

        #
        # calculate words per line
        #
        MINIMUM_SPACE_BETWEEN_WORDS, tmp = self.stringsize(' ',font,ptsize)
        line = []
        s = string.replace('\t',' \t ')
        s = s.replace('\n',' \n ')
        s = s.replace('  ',' ')        
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
            return string
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
                        tmp_pieces = re.sub(r'(?P<str>[aeiou!@#$%\*\(\)\\/\-~`\'"\?\.,\[\]]+)',' \g<str> ',tmp_pieces)
                        tmp_pieces = tmp_pieces.replace('  ',' ')                        
                        tmp_pieces = tmp_pieces.split(' ')
                        pieces = []
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
                                    rest_words += words[tmp]
                                    if tmp < len_words: rest_words += ' '
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
                    next_word_size , next_word_height = self.stringsize('...', font,ptsize)
                    # We need to remove the last word to place the '...' ?
                    if (occupied_size + next_word_size) <= width:
                        # No, just add it
                        lines[line_number].append('...')
                        lines_size[line_number] += next_word_size + MINIMUM_SPACE_BETWEEN_WORDS
                    else:
                        # Yes, put '...' in the last word place
                        tmp_word_size , tmp_word_height = self.stringsize(lines[line_number][len(lines[line_number])-1], font,ptsize)
                        lines[line_number][len(lines[line_number])-1] = '...'
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
        
        if bgcolor != None:
            self.drawbox(x,y, x+width, y+height, width=-1, color=bgcolor)
        for line_number in range(len(lines)):
            x0 = x
            spacing = MINIMUM_SPACE_BETWEEN_WORDS
            if align_h == 'justified':
                # Calculate the space between words:
                ## Disconsider the minimum space
                x0 = x                    
                lines_size[line_number] -= MINIMUM_SPACE_BETWEEN_WORDS * (len(lines[line_number]) -1 )
                if len(lines[line_number]) > 1:
                    spacing = (width - lines_size[line_number]) / ( len(lines[line_number]) -1 )
                else:
                    spacing = (width - lines_size[line_number]) / 2
                    x0 += spacing
                for word in lines[line_number]:
                    word_size, word_height = self.stringsize(word, font,ptsize)
                    self.drawstring(word, x0, y0, fgcolor, None, font, ptsize)
                    x0 += spacing
                    x0 += word_size
                    
            elif align_h == 'center':
                x0 = x + (width - lines_size[line_number]) / 2
                spacing = MINIMUM_SPACE_BETWEEN_WORDS                
                for word in lines[line_number]:
                    word_size, word_height = self.stringsize(word, font,ptsize)
                    self.drawstring(word, x0, y0, fgcolor, None, font, ptsize)
                    x0 += spacing
                    x0 += word_size
            elif align_h == 'left':
                x0 = x
                spacing = MINIMUM_SPACE_BETWEEN_WORDS
                for word in lines[line_number]:
                    word_size, word_height = self.stringsize(word, font,ptsize)
                    self.drawstring(word, x0, y0, fgcolor, None, font, ptsize)
                    x0 += spacing
                    x0 += word_size
            elif align_h == 'right':
                x0 = x + width
                spacing = MINIMUM_SPACE_BETWEEN_WORDS
                line_len = len(lines[line_number])
                for word_number in range(len(lines[line_number])):
                    pos = line_len - word_number -1
                    word_size, word_height = self.stringsize(lines[line_number][pos], font,ptsize)
                    self.drawstring(lines[line_number][pos], x0, y0, fgcolor, None, font, ptsize, 'right')
                    x0 -= spacing
                    x0 -= word_size
            # end if 
            # go down one line
            y0 += line_height
        # end for
        return rest_words

                    

    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0, align='left'):

        if not pygame.display.get_init():
            return None

        # XXX Krister: Workaround for new feature that is only possible in the new
        # XXX SDL OSD, line up columns delimited by tabs. Here the tabs are just
        # XXX replaced with spaces
        s = string.replace('\t', '   ')  

        if DEBUG: print 'drawstring (%d;%d) "%s"' % (x, y, s)
        
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies by 0.7 for some reason

        if DEBUG: print 'FONT: %s %s' % (font, ptsize)
        
        ren = self._renderstring(s, font, ptsize, fgcolor, bgcolor)
        
        # Handle horizontal alignment
        w, h = ren.get_size()
        tx = x # Left align is default
        if align == 'center':
            tx = x - w/2
        elif align == 'right':
            tx = x - w
            
        self.screen.blit(ren, (tx, y))


    # Render a string to an SDL surface. Uses a cache for speedup.
    def _renderstring(self, string, font, ptsize, fgcolor, bgcolor):

        if not pygame.display.get_init():
            return None

        f = self._getfont(font, ptsize)

        if not f:
            print 'Couldnt get font: "%s", size: %s' % (font, ptsize)
            return
        
        for i in range(len(self.stringcache)):
            csurf, cstring, cfont, cfgcolor, cbgcolor = self.stringcache[i]
            if (f == cfont and string == cstring and fgcolor == cfgcolor
                and bgcolor == cbgcolor):
                # Move to front of FIFO
                del self.stringcache[i]
                self.stringcache.append((csurf, cstring, cfont, cfgcolor, cbgcolor))
                return csurf

        # Render string with anti-aliasing
        if bgcolor == None:
            try:
                surf = f.render(string, 1, self._sdlcol(fgcolor))
            except:
                print 'FAILED: str="%s" col="%s"' % (string, fgcolor)
                raise
        else:
            surf = f.render(string, 1, self._sdlcol(fgcolor), self._sdlcol(bgcolor))

        # Store the surface in the FIFO
        self.stringcache.append((surf, string, f, fgcolor, bgcolor))
        if len(self.stringcache) > 100:
            del self.stringcache[0]

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
        

    def update(self):

        if not pygame.display.get_init():
            return None

        pygame.display.flip()


    def _getfont(self, filename, ptsize):
        if not pygame.display.get_init():
            return None

        for font in self.fontcache:
            if font.filename == filename and font.ptsize == ptsize:
                return font.font

        if DEBUG: print 'OSD: Loading font "%s"' % filename
        try:
            font = pygame.font.Font(filename, ptsize)
        except RuntimeError:
            print 'Couldnt load font "%s"' % filename
            raise
        f = Font()
        f.filename = filename
        f.ptsize = ptsize
        f.font = font
        
        self.fontcache.append(f)

        return f.font

        
    def _getbitmap(self, filename):
        if not pygame.display.get_init():
            return None

        if not os.path.isfile(filename):
            print 'Bitmap file "%s" doesnt exist!' % filename
            return None

        for i in range(len(self.bitmapcache)):
            fname, image = self.bitmapcache[i]
            if stringproxy(fname) == stringproxy(filename):
                # Move to front of FIFO
                del self.bitmapcache[i]
                self.bitmapcache.append((fname, image))
                return image

        try:
            if DEBUG: print 'Trying to load file "%s"' % filename
            tmp = pygame.image.load(filename)  # XXX Cannot load everything
            image = tmp.convert_alpha()  # XXX Cannot load everything
        except:
            print 'SDL image load problem!'
            return None

        # FIFO for images
        self.bitmapcache.append((filename, image))
        if len(self.bitmapcache) > 30:
            del self.bitmapcache[0]

        return image


    def _deletefromcache(self, filename):
        for i in range(len(self.bitmapcache)):
            fname, image = self.bitmapcache[i]
            if stringproxy(fname) == stringproxy(filename):
                del self.bitmapcache[i]

        
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
# By André Bjärby
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



