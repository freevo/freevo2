#
# osd.py
#
# This is the class for using the OSD server. It sends simple text commands
# over UDP/IP to the OSD server.
#
# $Id$

import socket, time, sys

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Set to 1 for debug output
DEBUG = 0


# Module variable that contains an initialized OSD() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = OSD()
        
    return _singleton


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

    
    def __init__(self, host='127.0.0.1', port=config.OSD_PORT):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send('clearscreen;' + str(self.COL_BLACK))
        self.default_fg_color = self.COL_BLACK
        self.default_bg_color = self.COL_WHITE
        self.width = 768                # XXX hardcoded, fix
        self.height = 576               # XXX hardcoded, fix


    def _send(self, str):
        while 1:
            try:
                self.s.sendto(str, (self.host, self.port))
                break # out of the while 1 loop
            except:
                if DEBUG: print 'OSD server (%s:%s) gone, '
                'trying again in a second...' % (self.host, self.port),
                #print 'Reason %s' % sys.exc_info()
                print sys.exc_info()[0]
                time.sleep(1)
                
        
    def shutdown(self):
        self._send('quit')


    def clearscreen(self, color=None):
        if color == None:
            color = self.default_bg_color
        args = str(color)
        self._send('clearscreen;' + args)


    def setpixel(self, x, y, color):
        args = str(x) + ';' + str(y) + ';' + str(color)
        self._send('setpixel;' + args)


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
        args = filename
        self._send('loadbitmap;' + args)


    # Loads and zooms a bitmap without copying it to the OSD drawing
    # buffer.
    def zoombitmap(self, filename, scaling=None, bbx=0, bby=0, bbw=0, bbh=0):
        if scaling == None:
            zoom = 1000
        else:
            zoom = int(scaling * 1000)
            
        args = [filename, str(bbx), str(bby), str(bbw), str(bbh), str(zoom)]
        self._send('zoombitmap;' + ';'.join(args))

        
    # Draw a bitmap on the OSD. It is automatically loaded into the cache
    # if not already there. The loadbitmap()/zoombitmap() functions can
    # be used to "pipeline" bitmap loading/drawing.
    def drawbitmap(self, filename, x=-1, y=-1, scaling=None,
                   bbx=0, bby=0, bbw=0, bbh=0):
        if scaling == None:
            zoom = 1000
        else:
            zoom = int(scaling * 1000)
            
        args = [filename, str(x), str(y), str(bbx), str(bby), str(bbw),
                str(bbh), str(zoom)]
        self._send('drawbitmap;' + ';'.join(args))


    def bitmapsize(self, file):
        if not os.path.isfile(file):
            return 0,0
        import Image
        image = Image.open(file)
        return image.size

        
    def drawline(self, x0, y0, x1, y1, width=None, color=None):
        if width == None:
            width = 1

        if color == None:
            color = self.default_fg_color

        args1 = str(x0) + ';' + str(y0) + ';'
        args2 = str(x1) + ';' + str(y1) + ';' + str(width) + ';' + str(color)
        self._send('drawline;' + args1 + args2)


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0):
        if width == None:
            width = 1

        if fill:
            width = -1   # This means that the box should be filled
            
        if color == None:
            color = self.default_fg_color
            
        args1 = str(x0) + ';' + str(y0) + ';'
        args2 = str(x1) + ';' + str(y1) + ';' + str(width) + ';'
        args3 = str(color)
        self._send('drawbox;' + args1 + args2 + args3)

        
    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0):
        # XXX Krister: Workaround for new feature that is only possible in the new
        # XXX SDL ODS, line up columns delimited by tabs. Here the tabs are just
        # XXX replaced with spaces
        s = string.replace('\t', '   ')  
                                  
        if fgcolor == None:
            fgcolor = self.default_fg_color
        if bgcolor == None:
            bgcolor = 0xff000000   # Transparent background
        if font == None:
            font = config.OSD_DEFAULT_FONTNAME
            ptsize = config.OSD_DEFAULT_FONTSIZE
        # Args: fontfilename;pointsize;string;x;y;fgcol
        args1 = font + ';' + str(ptsize) + ';' + s + ';'
        args2 = str(x) + ';' + str(y) + ';' + str(fgcolor)
        self._send('drawstring;' + args1 + args2)


    def update(self):
        self._send('update')

    def popup_box(self, text):
        """
        Trying to make a standard popup/dialog box for various usages.
        Currently it just draws itself in the middle of the screen.

        Arguments: Text, the text to print.
        Returns:   None
        Todo:      Should be able to calculate size of box to draw.
                   Maybe be able to set size manually aswell.
                   It'd look nice to have an icon drawn for some events
                   such as ejects.
        """
        start_x = self.width/2 - 180
        start_y = self.height/2 - 30
        end_x   = self.width/2 + 180
        end_y   = self.height/2 + 30

        # XXX This is a hack to get a border around a white box to look
        # XXX nicer.
        self.drawbox(start_x-2, start_y-2, end_x+2, end_y+2, width=2,
                     color=self.COL_BLACK)
        self.drawbox(start_x, start_y, end_x, end_y, width=-1,
                     color=((60 << 24) | self.COL_WHITE))
        self.drawstring(text, start_x+20, start_y+10,
                        fgcolor=self.COL_BLACK, bgcolor=self.COL_WHITE)
        

# XXX TEST CODE BY KRISTER! This code fragment will load the experimental OSD SDL module
# if the symbol OSD_SDL is in the config module namespace, but will work fine if it is not.
# This is used to load my new version of the OSD module without messing around in the source
# too much...
if 'OSD_SDL' in dir(config):
    from osd_sdl import *


#
# Simple test...
#
if __name__ == '__main__':
    osd = OSD()
    osd.clearscreen()

