# -*- coding: iso-8859-1 -*-
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
# Revision 1.18  2004/07/24 12:24:03  dischi
# reflect gui changes
#
# Revision 1.17  2004/07/23 19:44:00  dischi
# move most of the settings code out of the skin engine
#
# Revision 1.16  2004/07/17 08:56:12  dischi
# fix typo in variable
#
# Revision 1.15  2004/07/16 19:39:00  dischi
# smaller cleanups, still alpha
#
# Revision 1.14  2004/07/11 19:39:47  dischi
# reflect mmpython changes
#
# Revision 1.13  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.12  2004/07/10 10:36:53  dischi
# fix more crashes
#
# Revision 1.11  2004/07/10 08:44:20  dischi
# fix crash
#
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


import os
import time

import config
import plugin
import osd
import skin
import pygame
import time

# from osd import OSD
# from event import *

# osd = osd.get_singleton()

# class Surface:
#     def __init__(self, x, y, width, height):
#         self.screen = pygame.Surface((width, height), pygame.SRCALPHA)
#         self.pos    = x, y
#         self.width  = width
#         self.height = height

        
#     def blit(self, *arg1, **arg2):
#         self.screen.blit(*arg1, **arg2)


# class OSDbmovl(OSD):
#     """
#     an OSD class for bmovl
#     """
#     def __init__(self, width, height):
#         self.width  = width
#         self.height = height
#         self.depth  = 32
#         print 'new bmovl interface: %s, %s' % (width, height)
#         self.screen = pygame.Surface((width, height), pygame.SRCALPHA)

#         # clear surface
#         self.screen.fill((0,0,0,0))

#         self.bmovl  = os.open('/tmp/bmovl', os.O_WRONLY)
#         self.x0, self.y0, self.x1, self.y1 = self.width, self.height, 0, 0


#     def load_scaled_image(self, filename, width, height):
#         i = self.loadbitmap(filename)
#         if not i:
#             return None
#         scale = max(float(i.get_width()) / width, float(i.get_height()) / height)
#         return pygame.transform.scale(i, (int(i.get_width() / scale),
#                                           int(i.get_height() / scale)))



#     def calc_update_area(self, x0, y0, x1, y1):
#         self.x0 = min(x0, self.x0)
#         self.y0 = min(y0, self.y0)
#         self.x1 = max(x1, self.x1)
#         self.y1 = max(y1, self.y1)


#     def screenblit(self, source, destpos, sourcerect=None):
#         if sourcerect:
#             w = sourcerect[2]
#             h = sourcerect[3]
#             ret = self.screen.blit(source, destpos, sourcerect)
#         else:
#             w, h = source.get_size()
#             ret = self.screen.blit(source, destpos)
#         self.calc_update_area(destpos[0], destpos[1], destpos[0] + w, destpos[1] + h)
#         return ret


#     def drawbox(self, x0, y0, x1, y1, width=None, color=None, fill=0, layer=None):
#         if layer == None:
#             self.calc_update_area(x0, y0, x1, y1)
#             return OSD.drawbox(self, x0, y0, x1, y1, width, color, fill, layer)
#         return OSD.drawbox(self, x0, y0, x1, y1, width, color, fill, layer.screen)


#     def drawstringframed(self, string, x, y, width, height, font, fgcolor=None,
#                          bgcolor=None, align_h='left', align_v='top', mode='hard',
#                          layer=None, ellipses='...', dim=True):
#         if layer:
#             layer = layer.screen
#         ret = OSD.drawstringframed(self, string, x, y, width, height, font, fgcolor,
#                                    bgcolor, align_h, align_v, mode, layer, ellipses, dim)
#         if not layer:
#             self.calc_update_area(ret[1][0], ret[1][1], ret[1][2], ret[1][3])
#         return ret
    
        
#     def close(self):
#         print 'close'
#         os.close(self.bmovl)

        
#     def show(self):
#         try:
#             os.write(self.bmovl, 'SHOW\n')
#         except OSError:
#             pass

#     def hide(self):
#         try:
#             os.write(self.bmovl, 'HIDE\n')
#         except OSError:
#             pass
        

#     def clearscreen(self, color=None):
#         self.screen.fill((0,0,0,0))
#         try:
#             os.write(self.bmovl, 'CLEAR %s %s %s %s' % (self.width, self.height, 0, 0))
#         except OSError:
#             pass

        
#     def update(self, rect=None):
#         if not rect:
#             if self.x0 > self.x1:
#                 return
#             rect = self.x0, self.y0, self.x1 - self.x0, self.y1 - self.y0
#             self.x0, self.y0, self.x1, self.y1 = self.width, self.height, 0, 0
        
#         try:
#             update = self.screen.subsurface(rect)
#         except Exception, e:
#             print e
#             print rect, self.screen
#             return
        
#         try:
#             os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
#                      (update.get_width(), update.get_height(), rect[0], rect[1], 0, 0))
#             os.write(self.bmovl, pygame.image.tostring(update, 'RGBA'))
#         except OSError:
#             pass




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
        self.reason = 'not working while gui rebuild'
        return
    
        print
        print 'Activating video.bmovl plugin'
        print 'Warning: this plugin is only an example and not working in any'
        print 'cases. If Freevo crashes, deactivate this plugin. Don\'t send'
        print 'bug reports for this plugin, we know it\'s broken.'
        print
        plugin.Plugin.__init__(self)
        self._type  = 'mplayer_video'
        self.status = 'waiting'
        self.background = None

        
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
            self.length = 0
        if self.player.item_info:
            length = int(self.player.item_info.length)
            if hasattr(self.player.item_info, 'start'):
                self.start = self.player.item_info.start

        self.last_timer = self.start
        
        self.bg  = None
        self.cbg = None

        self.height = 0
        self.width  = 0

        self.status = 'playing'

        if os.path.exists('/tmp/bmovl'):
            return command + [ '-vf', 'bmovl=1:0:/tmp/bmovl' ]
        return command


    def create_background(self, x, y, width, height):
        self.background = Surface(x, y, width, height)
        
        wallpaper = skin.get_singleton().settings.images['background']
        if wallpaper:
            wallpaper = self.bmovl.loadbitmap(wallpaper)
        if wallpaper:
            wallpaper = pygame.transform.scale(wallpaper, (self.bmovl.width,
                                                           self.bmovl.height))
            self.background.blit(wallpaper, (0, 0), (x, y, width, height))
        else:
            print 'Strange, no background, this will look bad!'

        self.clockfont = skin.get_singleton().get_font('bmovl timer')

        self.bmovl.drawbox(0, 1, self.background.width, 1, width=1, color=0x000000,
                           layer=self.background)

        self.bmovl.drawbox(0, self.clockfont.height + 4, self.background.width,
                           self.clockfont.height + 4, width=1, color=0x000000,
                           layer=self.background)

        self.y0     = self.clockfont.height + 10
        self.x0     = config.OSD_OVERSCAN_X
        self.height = self.background.height - config.OSD_OVERSCAN_Y - self.y0
        self.width  = self.background.width  - 2 * config.OSD_OVERSCAN_X
        
        # draw movie image
        f = skin.get_singleton().settings.images['logo']
        i = self.bmovl.load_scaled_image(f, self.width / 4, self.height)
        if i:
            self.background.blit(i, (self.x0, self.y0))
            self.x0   += i.get_width() + 10
            self.width = self.background.width - self.x0 - config.OSD_OVERSCAN_X

        title   = self.item.name
        
        if self.item.tv_show:
            show     = config.VIDEO_SHOW_REGEXP_SPLIT(self.item.name)
            title    = String(show[0]) + " " + String(show[1]) + "x" + \
                       String(show[2]) + ' - ' + String(show[3])

        font = skin.get_singleton().get_font('bmovl title')
        pos  = self.bmovl.drawstringframed(title, self.x0, self.y0, self.width, -1,
                                           font, layer=self.background)

        self.y0 += font.height * 1.5
        
        font = skin.get_singleton().get_font('bmovl text')
        pos  = self.bmovl.drawstringframed('%s min.' % (self.length / 60),
                                           self.x0, self.y0 , self.width, -1, font,
                                           layer=self.background)

        

    def show_osd(self):
        """
        bmovl: init bmovl osd and show it
        """
        _debug_('show osd')

        self.bmovl.screenblit(self.background.screen, self.background.pos)
        
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
        if self.bmovl and self.status == 'playing':
            self.status = 'waiting'
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
        except Exception, e:
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
        if not self.bmovl and self.status == 'playing' and self.height and self.width:
            self.bmovl = OSDbmovl(self.width, self.height)
            self.create_background(0, self.height - self.height / 5 - config.OSD_OVERSCAN_Y,
                                   self.width, self.height / 5 + config.OSD_OVERSCAN_Y)


        if self.osd_visible and self.bmovl:
            start = self.start
            end   = max(self.start + self.length, timer)

            self.bmovl.screenblit(self.background.screen, self.background.pos,
                                  (0, 0, self.background.width, self.clockfont.height + 6))

            # new calc the bar
            box  = (self.background.width - 2 * config.OSD_OVERSCAN_X) / 4
            x0   = config.OSD_OVERSCAN_X
            y0   = self.background.pos[1]

            mpos = self.background.width - 2 * (x0 + box)
            pos  = (max(timer - start, 0) * (mpos)) / (end - start)

            self.bmovl.drawbox(x0 + box - 1, y0 + 1, self.background.width - x0 - box + 1,
                               y0 + self.clockfont.height + 4,
                               fill=0, color=0x000000)
            
            self.bmovl.drawbox(x0 + box, y0 + 2, self.background.width - x0 - box,
                               y0 + self.clockfont.height + 3,
                               fill=1, color=0xa0ffffff)
            
            self.bmovl.drawbox(x0 + box, y0 + 2, x0 + box + pos,
                               y0 + self.clockfont.height + 3,
                               fill=1, color=0x164668)
            
            font = self.clockfont
            y0   = self.background.pos[1] + 3
            
            self.bmovl.drawstringframed('%s' % self.time2str(start),
                                        x0, y0, box, -1, font,
                                        align_v='center', align_h='center')

            self.bmovl.drawstringframed('%s' % self.time2str(timer),
                                        (self.background.width / 2) - box, y0, 2*box,
                                        -1, font, align_v='center', align_h='center')

            self.bmovl.drawstringframed('%s' % self.time2str(end),
                                        self.background.width - config.OSD_OVERSCAN_X - box,
                                        y0, box, -1, font, align_v='center', align_h='center')

            if update:
                self.bmovl.update()

            font = skin.get_singleton().get_font('bmovl clock')
	    if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'

            format = time.strftime(format)

            x0 = self.background.width - 2 * config.OSD_OVERSCAN_X
            s  = font.stringsize(format) * 5

            self.bmovl.screenblit(self.background.screen,
                                  (self.background.pos[0] + x0 - s - 10,
                                   self.background.pos[1] + self.y0),
                                  (x0 - s - 10, self.y0,
                                   s, self.clockfont.height + 6))

            self.bmovl.drawstringframed(format,
                                        self.background.pos[0] + x0 - s - 10,
                                        self.background.pos[1] + self.y0, s,
                                        -1, font, align_h='right')

            if update:
                self.bmovl.update()

        else:
            self.last_timer = timer
