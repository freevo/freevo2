# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# renderer.py - interface to output using pygame
# -----------------------------------------------------------------------
# $Id$
#
# Note: Work in Progress
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/24 12:21:06  dischi
# move renderer into backend subdir
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
# -----------------------------------------------------------------------


# Python modules
import os
import stat
import Image
import re
import traceback

from types import *
from fcntl import ioctl

# Freevo modules
import config


# SDL modules
import pygame
from pygame.locals import *
from font import Font


class Renderer:
    """
    The basic render engine for gygame
    """
    # Some default colors (deprecated)
    COL_BLACK  = 0x000000
    COL_WHITE  = 0xffffff
    COL_ORANGE = 0xFF9028

    def __init__(self):
        """
        init the osd
        """
        import util
        self.fullscreen = 0 # Keep track of fullscreen state

        self.bitmapcache = util.objectcache.ObjectCache(5, desc='bitmap')
        self.font_info_cache = {}
        
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE

        self.width  = config.CONF.width
        self.height = config.CONF.height

        if config.CONF.display == 'dxr3':
            os.environ['SDL_VIDEODRIVER'] = 'dxr3'
        elif config.CONF.display in ( 'directfb', 'dfbmga' ):
            os.environ['SDL_VIDEODRIVER'] = 'directfb'

        # sometimes this fails
        if not os.environ.has_key('SDL_VIDEODRIVER') and \
               config.CONF.display == 'x11':
            os.environ['SDL_VIDEODRIVER'] = 'x11'


        # disable term blanking for mga and fbcon and restore the
        # tty so that sdl can use it
        if config.CONF.display in ('mga', 'fbcon'):
            for i in range(0,7):
                try:
                    fd = os.open('/dev/tty%s' % i, os.O_RDONLY | os.O_NONBLOCK)
                    try:
                        # set ioctl (tty, KDSETMODE, KD_TEXT)
                        ioctl(fd, 0x4B3A, 0)
                    except:
                        pass
                    os.close(fd)
                    os.system('%s -term linux -cursor off -blank 0 -clear -powerdown 0 ' \
                              '-powersave off </dev/tty%s > /dev/tty%s 2>/dev/null' % \
                              (config.CONF.setterm, i,i))
                except:
                    pass
            
        # Initialize the PyGame modules.
        pygame.display.init()
        pygame.font.init()

	self.depth = 32
	self.hw    = 0

        if config.CONF.display == 'dxr3':
            self.depth = 32

        try:
            self.screen = pygame.display.set_mode((self.width, self.height),
                                                  self.hw, self.depth)
        except:
            self.screen = pygame.display.set_mode((self.width, self.height))

        self.depth     = self.screen.get_bitsize()
        self.must_lock = self.screen.mustlock()
        
        if config.CONF.display == 'x11' and config.START_FULLSCREEN_X == 1:
            self.toggle_fullscreen()

        help = [ _('z = Toggle Fullscreen'),
                 _('Arrow Keys = Move'),
                 _('Spacebar = Select'),
                 _('Escape = Stop/Prev. Menu'),
                 _('h = Help') ]

        help_str = '    '.join(help)

        pygame.display.set_caption('Freevo' + ' '*7 + String( help_str ) )
        icon = pygame.image.load(os.path.join(config.ICON_DIR,
                                              'misc/freevo_app.png')).convert()
        pygame.display.set_icon(icon)
        
        self.clearscreen(self.COL_BLACK)
        self.update()

        if config.OSD_SDL_EXEC_AFTER_STARTUP:
            os.system(config.OSD_SDL_EXEC_AFTER_STARTUP)

        self.sdl_driver = pygame.display.get_driver()
        _debug_('SDL Driver: %s' % (str(self.sdl_driver)),2)

        pygame.mouse.set_visible(0)
        pygame.key.set_repeat(500, 30)
        
        # Remove old screenshots
        os.system('rm -f /tmp/freevo_ss*.bmp')
        self._screenshotnum = 1
        self.active = True

        # some functions from pygame
        self.Surface = pygame.Surface
        self.polygon = pygame.draw.polygon

        pygame.time.delay(10)   # pygame.time.get_ticks don't seem to
                                # work otherwise


    def shutdown(self):
        """
        shutdown the display
        """
        pygame.quit()
        if config.OSD_SDL_EXEC_AFTER_CLOSE:
            os.system(config.OSD_SDL_EXEC_AFTER_CLOSE)
        self.active = False


    def stopdisplay(self):
        """
        stop the display to give other apps the right to use it
        """
        # backup the screen
        self.__stop_screen__ = pygame.Surface((self.width, self.height))
        self.__stop_screen__.blit(self.screen, (0,0))
        pygame.display.quit()


    def restartdisplay(self):
        """
        restores a stopped display
        """
        pygame.display.init()
        self.width  = config.CONF.width
        self.height = config.CONF.height
        self.screen = pygame.display.set_mode((self.width, self.height), self.hw,
                                              self.depth)
        if hasattr(self, '__stop_screen__'):
            self.screen.blit(self.__stop_screen__, (0,0))
            del self.__stop_screen__
            
        # We need to go back to fullscreen mode if that was the mode before the shutdown
        if self.fullscreen:
            pygame.display.toggle_fullscreen()
            
        
    def toggle_fullscreen(self):
        """
        toggle between window and fullscreen mode
        """
        self.fullscreen = (self.fullscreen+1) % 2
        if pygame.display.get_init():
            pygame.display.toggle_fullscreen()
        _debug_('Setting fullscreen mode to %s' % self.fullscreen)


    def get_fullscreen(self):
        """
        return 1 is fullscreen is running
        """
        return self.fullscreen
    

    def clearscreen(self, color=None):
        """
        clean the complete screen
        """
        if not pygame.display.get_init():
            return None

        if color == None:
            color = self.default_bg_color
        self.screen.fill(self._sdlcol(color))
        
    
    def loadbitmap(self, url, cache=False, width=None, height=None, vfs_save=False):
        """
        Load a bitmap and return the pygame image object.
        If width and height are given, the image is scaled to that. Setting
        only width or height will keep aspect ratio.
        If vfs_save is true, the so scaled bitmap will be stored in the vfs for
        future use.
        """
        if cache:
            # first check the cache
            if cache == True:
                cache = self.bitmapcache
            if width != None or height != None:
                key = 'scaled://%s-%s-%s' % (url, width, height)
            else:
                key = url

            s = cache[key]
            if s:
                return s
                
        if vfs_save and (width == None or height == None):
            vfs_save = False

        if not pygame.display.get_init():
            return None

        # not in cache, load it

        try:
            image = pygame.image.fromstring(url.tostring(), url.size, url.mode)
        except:

            if url[:8] == 'thumb://':
                filename = os.path.abspath(url[8:])
                thumbnail = True
            else:
                filename = os.path.abspath(url)
                thumbnail = False
            
            if vfs_save:
                vfs_save = vfs.getoverlay('%s.raw-%sx%s' % (filename, width, height))
                try:
                    if os.stat(vfs_save)[stat.ST_MTIME] > \
                           os.stat(filename)[stat.ST_MTIME]:
                        f = open(vfs_save, 'r')
                        image = pygame.image.fromstring(f.read(), (width, height), 'RGBA')
                        f.close()
                        if cache:
                            cache[key] = image
                        return image
                except:
                    pass
                
            if not os.path.isfile(filename):
                filename = os.path.join(config.IMAGE_DIR, url[8:])

            if not os.path.isfile(filename):
                print 'osd.py: Bitmap file "%s" doesnt exist!' % filename
                return None
            
            try:
                import util
                if isstring(filename) and filename.endswith('.raw'):
                    # load cache
                    data  = util.read_thumbnail(filename)
                    # convert to pygame image
                    image = pygame.image.fromstring(data[0], data[1], data[2])

                elif thumbnail:
                    # load cache or create it
                    data = util.cache_image(filename)
                    # convert to pygame image
                    try:
                        image = pygame.image.fromstring(data[0], data[1], data[2])
                    except:
                        data = util.create_thumbnail(filename)
                        image = pygame.image.fromstring(data[0], data[1], data[2])
                else:
                    try:
                        image = pygame.image.load(filename)
                    except pygame.error, e:
                        print 'SDL image load problem: %s - trying Imaging' % e
                        i = Image.open(filename)
                        image = pygame.image.fromstring(i.tostring(), i.size, i.mode)
            
            except:
                print 'Unknown Problem while loading image %s' % String(url)
                if config.DEBUG:
                    traceback.print_exc()
                return None

        # scale the image if needed
        if width != None or height != None:
            image = self.resizebitmap(image, width, height)

        # convert the surface to speed up blitting later
        if image and image.get_alpha():
            image.set_alpha(image.get_alpha(), RLEACCEL)

        if vfs_save:
            f = vfs.open(vfs_save, 'w')
            f.write(pygame.image.tostring(image, 'RGBA'))
            f.close()
            
        if cache:
            cache[key] = image
        return image


    def resizebitmap(self, image, width=None, height=None):
        image_w, image_h = image.get_size()
        if width == None:
            # calculate width
            width = (height * float(image_w)) / float(image_h)
        if height == None:
            # calculate width
            height = (width * float(image_h)) / float(image_w)

        return pygame.transform.scale(image, (width, height))

        
    def zoombitmap(self, image, scaling=None, bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
        """
        Zooms a Surface. It gets a Pygame Surface which is rotated and scaled according
        to the parameters.
        """
        if not image:
            return None
        
        if bbx or bby or bbw or bbh:
            imbb = pygame.Surface((bbw, bbh))
            imbb.blit(image, (0, 0), (bbx, bby, bbw, bbh))
            image = imbb

        if scaling:
            w, h = image.get_size()
            w = int(w * scaling)
            h = int(h * scaling)

            if rotation:
                image = pygame.transform.rotozoom(image, rotation, scaling)
            else:
                image = pygame.transform.scale(image, (w, h))

        elif rotation:
            image = pygame.transform.rotate(image, rotation)

        return image


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0, layer=None):
        """
        draw a normal box
        """
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
            box = pygame.Surface((int(w), int(h)))
            box.fill((r,g,b))
            box.set_alpha(a)
            if layer:
                layer.blit(box, (x0, y0))
            else:
                self.screen.blit(box, (x0, y0))
        else:
            c = self._sdlcol(color)
            if not layer:
                layer = self.screen
            for i in range(0, width):
                # looks strange, but sometimes thinkness doesn't work
                pygame.draw.rect(layer, c, (x0+i, y0+i, x1-x0-2*i, y1-y0-2*i), 1)


    def screenblit(self, source, destpos, sourcerect=None):
        """
        blit the source to the screen
        """
        if sourcerect:
            w    = sourcerect[2]
            h    = sourcerect[3]
            ret  = self.screen.blit(source, destpos, sourcerect)
        else:
            w, h = source.get_size()
            ret  = self.screen.blit(source, destpos)

        return ret



    def getfont(self, font, ptsize):
        """
        return cached font
        """
        key = (font, ptsize)
        try:
            return self.font_info_cache[key]
        except:
            fi = Font(font, ptsize)
            self.font_info_cache[key] = fi
            return fi


    def drawstringframed(self, string, x, y, width, height, font, fgcolor=None,
                         bgcolor=None, align_h='left', align_v='top', mode='hard',
                         layer=None, ellipses='...', dim=True):
        """
        draws a string (text) in a frame. This tries to fit the
        string in lines, if it can't, it truncates the text,
        draw the part that fit and returns the other that doesn't.
        This is a wrapper to drawstringframedsoft() and -hard()

        Parameters:
        - string: the string to be drawn, supports also '\n'. \t is not supported
          by pygame, you need to replace it first
        - x,y: the posistion
        - width, height: the frame dimensions,
          height == -1 defaults to the font height size
        - fgcolor, bgcolor: the color for the foreground and background
          respectively. (Supports the alpha channel: 0xAARRGGBB)
        - font, ptsize: font and font point size
        - align_h: horizontal align. Can be left, center, right, justified
        - align_v: vertical align. Can be top, bottom, center or middle
        - mode: the way we should break lines/truncate. Can be 'hard'(based on chars)
          or 'soft' (based on words)

        font can also be a skin font object. If so, this functions also supports
        shadow and border. fgcolor and bgcolor will also be taken from the skin
        font if set to None when calling this function.

        THIS FUNCTION IS DEPRECATED
        """
        from gui.base import Text
        t = Text(x, y, x+width, y+height, string, font, height, align_h, align_v, mode,
                 ellipses, dim, fgcolor, bgcolor)
        t.layer = layer
        if layer == None:
            t.layer = self.screen
        return t.__render__()

    
    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0, align='left', layer=None):
        """
        draw a string

        THIS FUNCTION IS DEPRECATED
        """
        if not pygame.display.get_init():
            return None

        if not string:
            return None

        if fgcolor == None:
            fgcolor = self.default_fg_color

        if font == None:
            font = config.OSD_DEFAULT_FONTNAME

        if not ptsize:
            ptsize = config.OSD_DEFAULT_FONTSIZE

        tx = x
        width = self.width - tx

        if align == 'center':
            tx -= width/2
        elif align == 'right':
            tx -= width
            
        self.drawstringframed(string, x, y, width, -1, self.getfont(font, ptsize),
                              fgcolor, bgcolor, align_h = align, layer=layer,
                              ellipses='')


    def _savepixel(self, x, y, s):
        """
        help functions to save and restore a pixel
        for drawcircle
        """
        try:
            return (x, y, s.get_at((x,y)))
        except:
            return None

            
    def _restorepixel(self, save, s):
        """
        restore the saved pixel
        """
        if save:
            s.set_at((save[0],save[1]), save[2])


    def drawcircle(self, s, color, x, y, radius):
        """
        draws a circle to the surface s and fixes the borders
        pygame.draw.circle has a bug: there are some pixels where
        they don't belong. This function stores the values and
        restores them
        """
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
        """
        draw a round box
        """
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
            box = pygame.Surface((w, h), SRCALPHA)

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



    def update(self, rect=None, blend_surface=None, blend_speed=0,
               blend_steps=0, blend_time=None, stop_busyicon=True):
        """
        update the screen
        """
        if not pygame.display.get_init():
            return None

        if config.OSD_UPDATE_COMPLETE_REDRAW:
            rect = None

        if rect:
            try:
                pygame.display.update(rect)
            except:
                _debug_('osd.update(rect) failed, bad rect? - %s' % str(rect), 1)
                _debug_('updating whole screen')
                pygame.display.flip()
        else:
            pygame.display.flip()

        

    # Convert a 32-bit TRGB color to a 4 element tuple for SDL
    def _sdlcol(self, col):
        if col==None:
            return (0,0,0,255)
        a = 255 - ((col >> 24) & 0xff)
        r = (col >> 16) & 0xff
        g = (col >> 8) & 0xff
        b = (col >> 0) & 0xff
        c = (r, g, b, a)
        return c
