#if 0 /*
# -----------------------------------------------------------------------
# bmovl.py - bmovl plugin for Freevo MPlayer module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2004/07/09 21:12:18  dischi
# more bmovl fixes, still unstable
#
# Revision 1.9  2004/07/08 19:30:54  dischi
# o make some changes to make it look better
# o secure write with try except
# o add warning that this plugin is not stable
#
# Revision 1.8  2004/01/11 20:23:31  dischi
# move skin font handling to osd to avoid duplicate code
#
# Revision 1.7  2004/01/11 20:01:28  dischi
# make bmovl work again
#
# Revision 1.6  2003/12/07 19:40:30  dischi
# convert OVERSCAN variable names
#
# Revision 1.5  2003/12/03 21:52:08  dischi
# rename some skin function calls
#
# Revision 1.4  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.3  2003/11/19 05:41:30  krister
# Spelling fixes, usage note
#
# Revision 1.2  2003/11/04 17:57:50  dischi
# add doc
#
# Revision 1.1  2003/11/04 17:53:23  dischi
# Removed the unstable bmovl part from mplayer.py and made it a plugin.
# Even if we are in a code freeze, this is a major cleanup to put the
# unstable stuff in a plugin to prevent mplayer from crashing because of
# bmovl.
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



import os
import time

import config
import plugin
import osd
import skin
import pygame
import time

from osd import OSD
from event import *

osd = osd.get_singleton()

class OSDbmovl(OSD):
    """
    an OSD class for bmovl
    """
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.depth  = 32
        self.screen = pygame.Surface((width, height), pygame.SRCALPHA)

        # clear surface
        self.screen.fill((0,0,0,0))

        self.bmovl  = os.open('/tmp/bmovl', os.O_WRONLY)
        self.x0, self.y0, self.x1, self.y1 = self.width, self.height, 0, 0


    def load_scaled_image(self, filename, width, height):
        i = self.loadbitmap(filename)
        if not i:
            return None
        scale = max(float(i.get_width()) / width, float(i.get_height()) / height)
        return pygame.transform.scale(i, (int(i.get_width() / scale),
                                          int(i.get_height() / scale)))



    def calc_update_area(self, x0, y0, x1, y1):
        self.x0 = min(x0, self.x0)
        self.y0 = min(y0, self.y0)
        self.x1 = max(x1, self.x1)
        self.y1 = max(y1, self.y1)


    def screenblit(self, source, destpos, sourcerect=None):
        if sourcerect:
            w = sourcerect[2]
            h = sourcerect[3]
            ret = self.screen.blit(source, destpos, sourcerect)
        else:
            w, h = source.get_size()
            ret = self.screen.blit(source, destpos)
        self.calc_update_area(destpos[0], destpos[1], destpos[0] + w, destpos[1] + h)
        return ret


    def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0, layer=None):
        if layer == None:
            self.calc_update_area(x0, y0, x1, y1)
        return OSD.drawbox(self, x0, y0, x1, y1, width, color, fill, layer)


    def drawstringframed(self, string, x, y, width, height, font, fgcolor=None,
                         bgcolor=None, align_h='left', align_v='top', mode='hard',
                         layer=None, ellipses='...', dim=True):
        ret = OSD.drawstringframed(self, string, x, y, width, height, font, fgcolor,
                                   bgcolor, align_h, align_v, mode, layer, ellipses, dim)
        if not layer:
            self.calc_update_area(ret[1][0], ret[1][1], ret[1][2], ret[1][3])
        return ret
    
        
    def close(self):
        print 'close'
        os.close(self.bmovl)

        
    def show(self):
        try:
            os.write(self.bmovl, 'SHOW\n')
        except OSError:
            pass

    def hide(self):
        try:
            os.write(self.bmovl, 'HIDE\n')
        except OSError:
            pass
        

    def clearscreen(self, color=None):
        self.screen.fill((0,0,0,0))
        try:
            os.write(self.bmovl, 'CLEAR %s %s %s %s' % (self.width, self.height, 0, 0))
        except OSError:
            pass

        
    def update(self, rect=None):
        if not rect:
            if self.x0 > self.x1:
                return
            rect = self.x0, self.y0, self.x1 - self.x0, self.y1 - self.y0
            self.x0, self.y0, self.x1, self.y1 = self.width, self.height, 0, 0
        
        update = self.screen.subsurface(rect)

        try:
            os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
                     (update.get_width(), update.get_height(), rect[0], rect[1], 0, 0))
            os.write(self.bmovl, pygame.image.tostring(update, 'RGBA'))
        except OSError:
            pass




class PluginInterface(plugin.Plugin):
    """
    bmovl plugin for mplayer

    This plugin makes the OSD look much better in mplayer. It uses bmovl to show
    images from Freevo inside mplayer.

    This plugin is in an early development and may crash mplayer.
    To activate, you need to create a fifo /tmp/bmovl  (mkfifo /tmp/bmovl).
    """

    def __init__(self):
        """
        normal plugin init, but sets _type to 'mplayer_video'
        """
        print
        print 'Activating video.bmovl plugin'
        print 'Warning: this plugin is only an example and not working in any'
        print 'cases. If Freevo crashes, deactivate this plugin. Don\'t send'
        print 'bug reports for this plugin, we know it\'s broekn.'
        print
        plugin.Plugin.__init__(self)
        self._type = 'mplayer_video'

        
    def play(self, command, player):
        """
        called before playing is started to add some stuff to the command line
        """
        self.item        = player.item
        self.player      = player
        self.osd_visible = False
        self.bmovl = None

        self.start  = 0
        try:
            self.length = int(self.item.info['length'])
        except:
            self.lebgth = 0
        if self.player.item_info:
            length = int(self.player.item_info.length)
            if hasattr(self.player.item_info, 'ts_start'):
                self.start = self.player.item_info.ts_start

        self.last_timer = self.start
        
        self.bg  = None
        self.cbg = None

        self.height = 0
        self.width  = 0

        if os.path.exists('/tmp/bmovl'):
            return command + [ '-vf', 'bmovl=1:0:/tmp/bmovl' ]
        return command


    def show_osd(self):
        """
        bmovl: init bmovl osd and show it
        """
        _debug_('show osd')

        if not skin.get_singleton().settings.images.has_key('background'):
            _debug_('no background')
            return

        bg = self.bmovl.loadbitmap(skin.get_singleton().settings.images['background'])
        bg = pygame.transform.scale(bg, (self.bmovl.width, self.bmovl.height))

        self.clockfont = skin.get_singleton().get_font('bmovl timer')

        # bar at the bottom
        self.height  = config.OSD_OVERSCAN_Y + 100 + self.clockfont.height
        self.y0      = self.bmovl.height - self.height
        self.x0      = config.OSD_OVERSCAN_X + 10
        self.width   = self.bmovl.width - 2 * self.x0
        
        self.bmovl.screenblit(bg, (0, self.y0), (0, self.y0, self.bmovl.width,
                                                 self.bmovl.height - self.y0))

        self.bmovl.drawbox(0, self.y0 + 1, self.bmovl.width, self.y0 + 1,
                           width=1, color=0x000000)

        self.bmovl.drawbox(0, self.y0 + self.clockfont.height + 4, self.bmovl.width,
                           self.y0 + self.clockfont.height + 4, width=1, color=0x000000)


        # draw movie image
        f = os.path.join(config.IMAGE_DIR, 'gant/movie.png')
        i = self.bmovl.load_scaled_image(f, 90, 90)
        if i:
            self.bmovl.screenblit(i, (self.x0 + self.width - i.get_width(), self.y0 + 30))

        # draw movie image
        f = skin.get_singleton().settings.images['logo']
        i = self.bmovl.load_scaled_image(f, 200, 90)
        if i:
            self.bmovl.screenblit(i, (self.x0, self.y0 + 30))

        title   = self.item.name
        
        if self.item.tv_show:
            show     = config.VIDEO_SHOW_REGEXP_SPLIT(self.item.name)
            title    = String(show[0]) + " " + String(show[1]) + "x" + \
                       String(show[2]) + ' - ' + String(show[3])

        offset = 20 + i.get_width()

        font = skin.get_singleton().get_font('bmovl title')
        pos  = self.bmovl.drawstringframed(title, self.x0 + offset, self.y0 + 40,
                                           self.width - offset, -1, font)

        font = skin.get_singleton().get_font('bmovl text')
        pos  = self.bmovl.drawstringframed('%s min.' % (self.length / 60),
                                           self.x0 + offset, self.y0 + 80,
                                           self.width - offset, -1, font)

        self.elapsed(self.last_timer, update=False)

        self.bmovl.update()

        # and show it
        self.bmovl.show()


    def hide_osd(self):
        """
        bmovl: hide osd
        """
        _debug_('hide')
        self.player.app.refresh = None
        self.bmovl.clearscreen()
        self.bmovl.hide()
        
        
    def stop(self):
        """
        stop bmovl
        """
        if self.bmovl:
            self.bmovl.close()
            self.bmovl = None

        
    def eventhandler(self, event):
        """
        eventhandler to do our own osd toggle
        """
        if event == TOGGLE_OSD and self.bmovl:
            self.osd_visible = not self.osd_visible
            if not self.osd_visible:
                self.hide_osd()
            else:
                self.show_osd()
            return True


    def stdout(self, line):
        """
        get information from mplayer stdout
        """
        try:
            if line.find('SwScaler:') ==0 and line.find(' -> ') > 0 and \
                   line[line.find(' -> '):].find('x') > 0:
                width, height = line[line.find(' -> ')+4:].split('x')
                if self.height < int(height):
                    self.width  = int(width)
                    self.height = int(height)

            if line.find('Expand: ') == 0:
                width, height = line[7:line.find(',')].split('x')
                if self.height < int(height):
                    self.width  = int(width)
                    self.height = int(height)
        except:
            pass


    def time2str(self, timer):
        if timer / 3600:
            return '%d:%02d:%02d' % ( timer / 3600, (timer % 3600) / 60, timer % 60)
        else:
            return '%d:%02d' % (timer / 60, timer % 60)

        
    def elapsed(self, timer, update=True):
        """
        update osd
        """
        if not self.bmovl:
            self.bmovl = OSDbmovl(self.width, self.height)
            
        if self.osd_visible:
            start = self.start
            end   = self.start + self.length

            if not self.bg:
                self.bg = pygame.Surface((self.width, 30))
                self.bg.blit(self.bmovl.screen, (0, 0), (self.x0, self.y0, self.width, 30))
            else:
                self.bmovl.screenblit(self.bg, (self.x0, self.y0))

            # new calc the bar
            pos = (max(timer - start, 0) * (self.width - 200)) / (end - start)

            self.bmovl.drawbox(self.x0 + 120, self.y0 + 1,
                               self.x0 + self.width - 120,
                               self.y0 + self.clockfont.height + 4,
                               fill=1, color=0xa0ffffff)
            
            self.bmovl.drawbox(self.x0 + 120, self.y0 + 1,
                               self.x0 + 120 + pos,
                               self.y0 + self.clockfont.height + 4,
                               fill=1, color=0x164668)

            self.bmovl.drawbox(self.x0 + 120, self.y0 + 1,
                               self.x0 + self.width - 120,
                               self.y0 + self.clockfont.height + 4,
                               width=1, color=0x000000)


            font = self.clockfont
            self.bmovl.drawstringframed('%s' % self.time2str(start),
                                        self.x0, self.y0 + 3, 120, -1, font,
                                        align_v='center', align_h='center')

            self.bmovl.drawstringframed('%s' % self.time2str(timer),
                                        self.x0 + (self.width / 2) - 60,
                                        self.y0 + 3, 120, -1, font,
                                        align_v='center', align_h='center')

            self.bmovl.drawstringframed('%s' % self.time2str(end),
                                        self.x0 + self.width - 120,
                                        self.y0 + 3, 120, -1, font,
                                        align_v='center', align_h='center')

            if update:
                self.bmovl.update()

            font = skin.get_singleton().get_font('bmovl clock')
	    if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'

            if not self.cbg:
                self.cbg = pygame.Surface((200, 30))
                self.cbg.blit(self.bmovl.screen, (0, 0),
                              (self.x0 + self.width - 200, self.y0 + 78, 200, 30))
            else:
                self.bmovl.screenblit(self.cbg, (self.x0 + self.width - 200, self.y0 + 78))

            self.bmovl.drawstringframed(time.strftime(format),
                                        self.x0 + self.width - 200, self.y0 + 80,
                                        200, -1, font, align_h='right')

            if update:
                self.bmovl.update()

        else:
            self.last_timer = timer
