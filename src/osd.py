#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# osd.py - Low level graphics routines
# -----------------------------------------------------------------------
# $Id$
#
# Notes: do not use the OSD object inside a thread
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.164  2004/07/08 12:44:40  rshortt
# Add directfb as a display option.
#
# Revision 1.163  2004/06/29 18:29:20  dischi
# auto repair broken thumbnails
#
# Revision 1.162  2004/06/13 18:40:37  dischi
# fix crash
#
# Revision 1.161  2004/06/10 10:01:31  dischi
# cleanup
#
# Revision 1.160  2004/06/09 19:50:17  dischi
# change thumbnail caching format to be much faster: do not use pickle and
# also reduce the image size from max 300x300 to 255x255
#
# Revision 1.159  2004/06/06 16:13:27  dischi
# handle missing surfarray (Python Numeric)
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

# Python modules
import time
import os
import stat
import Image
import re
import traceback
import threading, thread
from types import *
from fcntl import ioctl
import cStringIO

# Freevo modules
import config
import rc
import util


if __freevo_app__ == 'main':
    # The PyGame Python SDL interface.
    import pygame
    from pygame.locals import *

    # import animations
    import animation

        


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


# Module variable that contains an initialized OSD() object
_singleton = None

def get_singleton():
    global _singleton

    # don't start osd for helpers
    if config.HELPER:
        return
    
    # One-time init
    if _singleton == None:
        _singleton = OSD()
        
    return _singleton


def stop():
    """
    stop the osd because only one program can use the
    device, e.g. for DXR3 and dfbmga output,
    """
    get_singleton().stopdisplay()
    

def restart():
    """
    restart a stopped osd
    """
    get_singleton().restartdisplay()
    get_singleton().update()
    

class Font:
    def __init__(self, filename='', ptsize=0, font=None):
        print 'deprecated font object use'
        self.filename = filename
        self.ptsize   = ptsize
        self.font     = font


font_warning = []

class OSDFont:
    def __init__(self, name, ptsize):
        self.font   = self.__getfont__(name, ptsize)
        self.height = max(self.font.size('A')[1], self.font.size('j')[1])
        self.chars  = {}
        self.name   = name
        self.ptsize = ptsize
        
    def charsize(self, c):
        try:
            return self.chars[c]
        except:
            w = self.font.size(c)[0]
            self.chars[c] = w
            return w

    def stringsize(self, s):
        if not s:
            return 0
        w = 0
        for c in s:
            w += self.charsize(c)
        return w

    def __loadfont__(self, filename, ptsize):
        if os.path.isfile(filename):
            try:
                return pygame.font.Font(filename, ptsize)
            except (RuntimeError, IOError):
                return None
        return None
    
        
    def __getfont__(self, filename, ptsize):
        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies by 0.7 for some reason

        _debug_('Loading font "%s"' % filename, 2)
        font   = self.__loadfont__(filename, ptsize)
        if not font:
            
            # search OSD_EXTRA_FONT_PATH for this font
            fontname = os.path.basename(filename)
            for path in config.OSD_EXTRA_FONT_PATH:
                fname = os.path.join(path, fontname)
                font  = self.__loadfont__(fname, ptsize)
                if font:
                    break
                # deactivated: arialbd seems to be have a wrong height
                # font  = self.__loadfont__(fname.replace('_bold', 'bd'), ptsize)
                # if font:
                #     break
                
        if not font:
            _debug_('Couldnt load font "%s"' % os.path.basename(filename).lower())

            # Ok, see if there is an alternate font to use
            if fontname.lower() in config.OSD_FONT_ALIASES:
                alt_fname = os.path.join(config.FONT_DIR,
                                         config.OSD_FONT_ALIASES[fontname.lower()])
                _debug_('trying alternate: %s' % os.path.basename(alt_fname).lower())
                font = self.__loadfont__(alt_fname, ptsize)

        if not font:
            # not good
            global font_warning
            if not fontname in font_warning:
                print 'WARNING: No alternate found in the alias list!'
                print 'Falling back to default font, this may look very ugly'
                font_warning.append(fontname)
            font = self.__loadfont__(config.OSD_DEFAULT_FONTNAME, ptsize)

        if not font:
            print 'Couldnt load font "%s"' % config.OSD_DEFAULT_FONTNAME
            raise

        return font

        


class BusyIcon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.mode_flag   = threading.Event()
        threading.Thread.start(self)
        self.timer  = 0
        self.active = False
        self.lock   = thread.allocate_lock()
        self.rect   = None
        
    def wait(self, timer):
        self.lock.acquire()
        self.active = True
        self.timer  = timer
        self.mode_flag.set()
        self.lock.release()
        
    def stop(self):
        self.lock.acquire()
        self.active = False
        self.lock.release()
    
    def run(self):
        while (1):
            self.mode_flag.clear()
            self.mode_flag.wait()
            while self.active and self.timer > 0.01:
                self.timer -= 0.01
                time.sleep(0.01)
            if self.active:
                import skin
                self.lock.acquire()
                osd = get_singleton()
                icon = skin.get_icon('misc/osd_busy')
                if icon:
                    image  = osd.loadbitmap(icon)
                    width  = image.get_width()
                    height = image.get_height()
                    x = osd.width  - config.OSD_OVERSCAN_X - 20 - width
                    y = osd.height - config.OSD_OVERSCAN_Y - 20 - height

                    self.rect = (x,y,width,height)
                    # backup the screen
                    screen = pygame.Surface((width,height))
                    screen.blit(osd.screen, (0,0), self.rect)
                    # draw the icon
                    osd.drawbitmap(image, x, y)
                    osd.update(rect=self.rect, stop_busyicon=False)

                    # restore the screen
                    osd.screen.blit(screen, (x,y))
                self.lock.release()
                
            while self.active:
                time.sleep(0.01)


class OSD:

    # Some default colors
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

    def __init__(self):
        """
        init the osd
        """
        self.fullscreen = 0 # Keep track of fullscreen state
        self.app_list = []

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
            
        self.busyicon = BusyIcon()

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
        self.mousehidetime = time.time()
        
        self._help       = 0  # Is the helpscreen displayed or not
        self._help_saved = pygame.Surface((self.width, self.height))
        self._help_last  = 0

        # Remove old screenshots
        os.system('rm -f /tmp/freevo_ss*.bmp')
        self._screenshotnum = 1
        self.active = True

        # some functions from pygame
        self.Surface = pygame.Surface
        self.polygon = pygame.draw.polygon

        # starts the render and it's thread
        self.render = animation.render.get_singleton()

        pygame.time.delay(10)   # pygame.time.get_ticks don't seem to
                                # work otherwise


    def focused_app(self):
        if len(self.app_list):
            return self.app_list[-1]
        else:
            return None


    def add_app(self, app):
        self.app_list.append(app)


    def remove_app(self, app):
        _times = self.app_list.count(app)
        for _time in range(_times):
            self.app_list.remove(app)
        if _times and hasattr(self.focused_app(), 'event_context'):
            _debug_('app is %s' % self.focused_app(),2)
            _debug_('Setting context to %s' % self.focused_app().get_event_context(),2)
            rc.set_context(self.focused_app().get_event_context())


    def _cb(self, map=True):
        """
        callback for SDL event (not Freevo events)
        """
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
                return
            
            if event.type == KEYDOWN:
                if not map and event.key > 30:
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        pass
                    
                if event.key in config.KEYMAP.keys():
                    # Turn off the helpscreen if it was on
                    if self._help:
                        self._helpscreen()
                    return config.KEYMAP[event.key]

                elif event.key == K_h:
                    self._helpscreen()

                elif event.key == K_z:
                    self.toggle_fullscreen()

                elif event.key == K_F10:
                    # Take a screenshot
                    pygame.image.save(self.screen,
                                      '/tmp/freevo_ss%s.bmp' % self._screenshotnum)
                    self._screenshotnum += 1

                else:
                    # don't know what this is, return it as it is
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        return None
    
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
        # stop all animations
        self.render.suspendall()

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
            
        # restart all animations
        self.render.restartall()

        
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
        
    
    def loadbitmap(self, url, cache=False):
        """
        Load a bitmap and return the pygame image object.
        """
        if cache:
            if cache == True:
                cache = self.bitmapcache
            s = cache[url]
            if s:
                return s

        if not pygame.display.get_init():
            return None

        try:
            image = pygame.image.fromstring(url.tostring(), url.size, url.mode)
        except:

            if url[:8] == 'thumb://':
                filename = os.path.abspath(url[8:])
                thumbnail = True
            else:
                filename = os.path.abspath(url)
                thumbnail = False
            
            if not os.path.isfile(filename):
                filename = os.path.join(config.IMAGE_DIR, url[8:])

            if not os.path.isfile(filename):
                print 'osd.py: Bitmap file "%s" doesnt exist!' % filename
                return None
            
            try:
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

        # convert the surface to speed up blitting later
        if image and image.get_alpha():
            image.set_alpha(image.get_alpha(), RLEACCEL)

        if cache:
            cache[url] = image
        return image

    
    def drawbitmap(self, image, x=0, y=0, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0, rotation = 0, layer=None):
        """           
        Draw a bitmap on the OSD. It is automatically loaded into the cache
        if not already there.
        """
        if not pygame.display.get_init():
            return None
        if not isinstance(image, pygame.Surface):
            image = self.loadbitmap(image, True)
        self.drawsurface(image, x, y, scaling, bbx, bby, bbw, bbh, rotation, layer)


    def drawsurface(self, image, x=0, y=0, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0, rotation = 0, layer=None):
        """
        scales and rotates a surface and then draws it to the screen.
        """
        if not pygame.display.get_init():
            return None
        image = self.zoomsurface(image, scaling, bbx, bby, bbw, bbh, rotation)
        if not image:
            return
        if layer:
            layer.blit(image, (x, y))
        else:
            self.screen.blit(image, (x, y))


    def zoomsurface(self, image, scaling=None, bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
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
            w = int(w*scaling)
            h = int(h*scaling)
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


    def getsurface(self, x=0, y=0, width=0, height=0, rect=None):
        """
        returns a copy of the given area of the current screen
        """
        if  rect != None:
            return self.screen.subsurface(rect).convert()
        else:
            return self.screen.subsurface( (x, y, width, height) ).convert()
    

    def putsurface(self, surface, x, y):
        """
        copy a surface to the screen
        """
        self.screen.blit(surface, (x, y))


    def screenblit(self, source, destpos, sourcerect=None):
        """
        blit the source to the screen
        """
        if sourcerect:
            w = sourcerect[2]
            h = sourcerect[3]
            ret = self.screen.blit(source, destpos, sourcerect)
        else:
            w, h = source.get_size()
            ret = self.screen.blit(source, destpos)

        if self.render:
            self.render.damage( [(destpos[0], destpos[1], w, h)] )

        return ret



    def getfont(self, font, ptsize):
        """
        return cached font
        """
        key = (font, ptsize)
        try:
            return self.font_info_cache[key]
        except:
            fi = OSDFont(font, ptsize)
            self.font_info_cache[key] = fi
            return fi


    def __drawstringframed_line__(self, string, max_width, font, hard,
                                  ellipses, word_splitter):
        """
        calculate _one_ line for drawstringframed. Returns a list:
        width used, string to draw, rest that didn't fit and True if this
        function stopped because of a \n.
        """
        c = 0                           # num of chars fitting
        width = 0                       # width needed
        ls = len(string)
        space = 0                       # position of last space
        last_char_size = 0              # width of the last char
        last_word_size = 0              # width of the last word

        if ellipses:
            # check the width of the ellipses
            ellipses_size = font.stringsize(ellipses)
            if ellipses_size > max_width:
                # if not even the ellipses fit, we have not enough space
                # until the text is shorter than the ellipses
                width = font.stringsize(string)
                if width <= max_width:
                    # ok, text fits
                    return (width, string, '', False)
                # ok, only draw the ellipses, shorten them first
                while(ellipses_size > max_width):
                    ellipses = ellipses[:-1]
                    ellipses_size = font.stringsize(ellipses)
                return (ellipses_size, ellipses, string, False)
        else:
            ellipses_size = 0
            ellipses = ''

        data = None
        while(True):
            if width > max_width - ellipses_size and not data:
                # save this, we will need it when we have not enough space
                # but first try to fit the text without ellipses
                data = c, space, width, last_char_size, last_word_size
            if width > max_width:
                # ok, that's it. We don't have any space left
                break
            if ls == c:
                # everything fits
                return (width, string, '', False)
            if string[c] == '\n':
                # linebreak, we have to stop
                return (width, string[:c], string[c+1:], True)
            if not hard and string[c] in word_splitter:
                # rememeber the last space for mode == 'soft' (not hard)
                space = c
                last_word_size = 0

            # add a char
            last_char_size = font.charsize(string[c])
            width += last_char_size
            last_word_size += last_char_size
            c += 1

        # restore to the pos when the width was one char to big and
        # incl. ellipses_size
        c, space, width, last_char_size, last_word_size = data

        if hard:
            # remove the last char, than it fits
            c -= 1
            width -= last_char_size

        else:
            # go one word back, than it fits
            c = space
            width -= last_word_size

        # calc the matching and rest string and return all this
        return (width+ellipses_size, string[:c]+ellipses, string[c:], False)

            

    def __draw_transparent_text__(self, surface, pixels=30):
        """
        Helper for drawing a transparency gradient end for strings
        which don't fit it's content area.
        """
        try:
            opaque_mod = float(1)
            opaque_stp = opaque_mod/float(pixels)
            w, h       = surface.get_size()
            alpha      = pygame.surfarray.pixels_alpha(surface)

            # transform all the alpha values in x,y range
            # any speedup could help alot
            for x in range(max(w-pixels, 1), w):
                for y in range(1, h):
                    if alpha[x,y][0] != 0:
                        alpha[x,y] = int(alpha[x,y][0]*opaque_mod)
                opaque_mod -= opaque_stp
        except Exception, e:
            print e


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
        """
        if not pygame.display.get_init():
            return '', (x,y,x,y)

        if not string:
            return '', (x,y,x,y)

        shadow_x      = 0
        shadow_y      = 0
        border_color  = None
        border_radius = 0

        dim = config.OSD_DIM_TEXT and dim
        # XXX pixels to dim, this should probably be tweaked
        dim_size = 25
            
        if hasattr(font, 'shadow'):
            # skin font
            if font.shadow.visible:
                if font.shadow.border:
                    border_color  = font.shadow.color
                    border_radius = int(font.font.ptsize/10)
                else:
                    shadow_x     = font.shadow.y
                    shadow_y     = font.shadow.x
                    shadow_color = self._sdlcol(font.shadow.color)
            if not fgcolor:
                fgcolor = font.color
            if not bgcolor:
                bgcolor = font.bgcolor
            font    = font.font

        if height == -1:
            height = font.height
        elif border_color != None:
            height -= border_radius * 2
        else:
            height -= abs(shadow_y)

        width = width - (abs(shadow_x) + border_radius * 2)
        if shadow_x < 0:
            x -= shadow_x
        if shadow_y < 0:
            y -= shadow_y
        x += border_radius
        y += border_radius

        line_height = font.height * 1.1
        if int(line_height) < line_height:
            line_height = int(line_height) + 1

        if width <= 0 or height < font.height:
            return string, (x,y,x,y)
            
        num_lines_left   = int((height+line_height-font.height) / line_height)
        lines            = []
        current_ellipses = ''
        hard = mode == 'hard'

        if num_lines_left == 1 and dim:
            ellipses = ''
            mode = hard = 'hard'
        else:
            dim = False
            
        while(num_lines_left):
            # calc each line and put the rest into the next
            if num_lines_left == 1:
                current_ellipses = ellipses
            #
            # __drawstringframed_line__ returns a list:
            # width of the text drawn (w), string which is drawn (s),
            # rest that does not fit (r) and True if the breaking was because
            # of a \n (n)
            #
            (w, s, r, n) = self.__drawstringframed_line__(string, width, font, hard,
                                                          current_ellipses, ' ')
            if s == '' and not hard:
                # nothing fits? Try to break words at ' -_' and no ellipses
                (w, s, r, n) = self.__drawstringframed_line__(string, width, font, hard,
                                                              None, ' -_')
                if s == '':
                    # still nothing? Use the 'hard' way
                    (w, s, r, n) = self.__drawstringframed_line__(string, width, font,
                                                                  'hard', None, ' ')
            lines.append((w, s))
            while r and r[0] == '\n':
                lines.append((0, ' '))
                num_lines_left -= 1
                r = r[1:]
                n = True

            if n:
                string = r
            else:
                string = r.strip()

            num_lines_left -= 1

            if not r:
                # finished, everything fits
                break

        if len(r) == 0 and dim:
            dim = False

        # calc the height we want to draw (based on different align_v)
        height_needed = (len(lines) - 1) * line_height + font.height
        if align_v == 'bottom':
            y += (height - height_needed)
        elif align_v == 'center':
            y += int((height - height_needed)/2)

        y0    = y
        min_x = 10000
        max_x = 0

        if not layer and layer != '':
            layer = self.screen

        fgcolor  = self._sdlcol(fgcolor)
        if border_color != None:
            border_color = self._sdlcol(border_color)

        for w, l in lines:
            if not l:
                continue

            x0 = x
            if layer:
                try:
                    # render the string. Ignore all the helper functions for that
                    # in here, it's faster because he have more information
                    # in here. But we don't use the cache, but since the skin only
                    # redraws changed areas, it doesn't matter and saves the time
                    # when searching the cache
                    render = font.font.render(l, 1, fgcolor)

                    # calc x/y positions based on align
                    if align_h == 'right':
                        x0 = x + width - render.get_size()[0]
                    elif align_h == 'center':
                        x0 = x + int((width - render.get_size()[0]) / 2)

                    if bgcolor:
                        # draw a box around the text if we have a bgcolor
                        self.drawbox(x0, y0, x0+render.get_size()[0],
                                     y0+render.get_size()[1], color=bgcolor, fill=1,
                                     layer=layer)

                    if border_color:
                        # draw the text 8 times with the border_color to get
                        # the border effect
                        re = font.font.render(l, 1, border_color)
                        if dim:
                            # draw on a tmp surface if we need to dim. It looks
                            # bad if we don't do that
                            tmp = pygame.Surface((render.get_size()[0] + \
                                                  2 * border_radius,
                                                  render.get_size()[1] + \
                                                  2 * border_radius)).convert_alpha()
                            tmp.fill((255, 0, 0, 0))
                            
                            for ox in (0, border_radius, border_radius*2):
                                for oy in (0, border_radius, border_radius*2):
                                    if ox or oy:
                                        tmp.blit(re, (ox, oy))
                            tmp.blit(render, (border_radius, border_radius))
                            self.__draw_transparent_text__(tmp,dim_size)
                            layer.blit(tmp, (x0-border_radius, y0-border_radius))

                        else:
                            for ox in (-border_radius, 0, border_radius):
                                for oy in (-border_radius, 0, border_radius):
                                    if ox or oy:
                                        layer.blit(re, (x0+ox, y0+oy))
                                    
                    if shadow_x or shadow_y:
                        # draw the text in the shadow_color to get a shadow
                        re = font.font.render(l, 1, shadow_color)
                        if dim:
                            self.__draw_transparent_text__(re, dim_size)
                        layer.blit(re, (x0+shadow_x, y0+shadow_y))

                    # draw the text in the fgcolor
                    if not (border_color and dim):
                        if dim:
                            self.__draw_transparent_text__(render, dim_size)
                        layer.blit(render, (x0, y0))

                except Exception, e:
                    print 'Render failed, skipping \'%s\'...' % l
                    print e
                    if config.DEBUG:
                        traceback.print_exc()
                    
            if x0 < min_x:
                min_x = x0
            if x0 + w > max_x:
                max_x = x0 + w
            y0 += line_height


        # change max_x, min_x, y and height_needed to reflect the
        # changes from shadow
        if shadow_x:
            if shadow_x < 0:
                min_x += shadow_x
            else:
                max_x += shadow_x
        if shadow_y:
            if shadow_y < 0:
                y += shadow_y
                height_needed -= shadow_y
            else:
                height_needed += shadow_y

        # add border radius for each line
        if border_color:
            max_x += border_radius
            min_x -= border_radius
            y     -= border_radius
            height_needed += border_radius * 2

        return r, (min_x, y, max_x, y+height_needed)
    



    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0, align='left', layer=None):
        """
        draw a string. This function is obsolete, please use drawstringframed
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

        if self.busyicon.active and stop_busyicon:
            self.busyicon.stop()

        if config.OSD_UPDATE_COMPLETE_REDRAW:
            rect = None

        if rect and not (stop_busyicon and self.busyicon.rect):
            try:
                pygame.display.update(rect)
            except:
                _debug_('osd.update(rect) failed, bad rect? - %s' % str(rect), 1)
                _debug_('updating whole screen')
                pygame.display.flip()
        else:
            pygame.display.flip()

        if stop_busyicon:
            self.busyicon.rect = None
        



    def _helpscreen(self):
        if not pygame.display.get_init():
            return None

        self._help = {0:1, 1:0}[self._help]
        
        if self._help:
            _debug_('Help on')
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
                fname = config.OSD_DEFAULT_FONTNAME
                if ks: self.drawstring(ks, x, y, font=fname, ptsize=14)
                if cmd: self.drawstring(cmd, x+80, y, font=fname, ptsize=14)
                row += 1
                if row >= 15:
                    row = 0
                    col += 1

            self.update()
        else:
            _debug_('Help off')
            self.screen.blit(self._help_saved, (0, 0))
            self.update()

        
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
