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
        self.screen = pygame.Surface((width, height), SRCALPHA)

        # clear surface
        self.screen.fill((0,0,0,0))

        self.bmovl  = os.open('/tmp/bmovl', os.O_WRONLY)


    def close(self):
        os.close(self.bmovl)

        
    def show(self):
        os.write(self.bmovl, 'SHOW\n')
        

    def hide(self):
        os.write(self.bmovl, 'HIDE\n')
        

    def clearscreen(self, color=None):
        self.screen.fill((0,0,0,0))
        os.write(self.bmovl, 'CLEAR %s %s %s %s' % (self.width, self.height, 0, 0))

        
    def update(self, rect):
        _debug_('update bmovl')
        update = self.screen.subsurface(rect)
        os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
                 (update.get_width(), update.get_height(), rect[0], rect[1], 0, 0))
        os.write(self.bmovl, pygame.image.tostring(update, 'RGBA'))




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
        plugin.Plugin.__init__(self)
        self._type = 'mplayer_video'

        
    def play(self, command, player):
        """
        called before playing is started to add some stuff to the command line
        """
        self.item = player.item
        self.player = player
        self.osd_visible = False
        self.bmovl = None
        if os.path.exists('/tmp/bmovl'):
            return command + [ '-vf', 'bmovl=1:0:/tmp/bmovl' ]
        return command


    def show_osd(self):
        """
        bmovl: init bmovl osd and show it
        """
        _debug_('show osd')

        height = config.OSD_OSD_OVERSCAN_Y + 60
        if not skin.get_singleton().settings.images.has_key('background'):
            _debug_('no background')
            return
        
        bg = self.bmovl.loadbitmap(skin.get_singleton().settings.images['background'])
        bg = pygame.transform.scale(bg, (self.bmovl.width, self.bmovl.height))

        self.bmovl.screen.blit(bg, (0,0))

        # bar at the top:
        self.bmovl.drawbox(0, height-1, osd.width, height-1, width=1, color=0x000000)

        clock       = time.strftime('%a %I:%M %P')
        clock_font  = skin.get_singleton().get_font('clock')
        clock_width = clock_font.font.stringsize(clock)
        
        self.bmovl.drawstringframed(clock, self.bmovl.width-config.OSD_OVERSCAN_X-10-clock_width,
                                    config.OSD_OVERSCAN_Y+10, clock_width, -1,
                                    clock_font.font, clock_font.color)

        self.bmovl.update((0, 0, self.bmovl.width, height))

        # bar at the bottom
        height += 40
        x0      = config.OSD_OVERSCAN_X+10
        y0      = self.bmovl.height + 5 - height
        width   = self.bmovl.width - 2 * config.OSD_OSD_OVERSCAN_X
        
        self.bmovl.drawbox(0, self.bmovl.height + 1 - height, self.bmovl.width,
                           self.bmovl.height + 1 - height, width=1, color=0x000000)

        if self.item.image:
            image = pygame.transform.scale(self.bmovl.loadbitmap(self.item.image), (65, 90))
            self.bmovl.screen.blit(image, (x0, y0))
            x0    += image.get_width() + 10
            width -= image.get_width() + 10
            
        title   = self.item.name
        tagline = self.item.getattr('tagline')

        if self.item.tv_show:
            show    = config.VIDEO_SHOW_REGEXP_SPLIT(self.item.name)
            title   = show[0] + " " + show[1] + "x" + show[2]
            tagline = show[3]
        
        title_font   = skin.get_singleton().get_font('title')
        tagline_font = skin.get_singleton().get_font('info tagline')

        pos = self.bmovl.drawstringframed(title, x0, y0, width, -1, title_font.font,
                                          title_font.color)
        if tagline:
            self.bmovl.drawstringframed(tagline, x0, pos[1][3]+5, width, -1,
                                        tagline_font.font, tagline_font.color)
            
        self.bmovl.update((0, self.bmovl.height-height, self.bmovl.width, height))

        # and show it
        self.bmovl.show()


    def hide_osd(self):
        """
        bmovl: hide osd
        """
        _debug_('hide')
        self.player.thread.app.refresh = None
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
            if self.osd_visible:
                self.player.thread.app.write('osd 1\n')
                self.hide_osd()
            else:
                self.show_osd()
                self.player.thread.app.write('osd 3\n')
            self.osd_visible = not self.osd_visible
            return True


    def stdout(self, line):
        """
        get information from mplayer stdout
        """
        if self.bmovl:
            return

        try:
            if line.find('SwScaler:') ==0 and line.find(' -> ') > 0 and \
                   line[line.find(' -> '):].find('x') > 0:
                width, height = line[line.find(' -> ')+4:].split('x')
                self.bmovl = OSDbmovl(int(width), int(height))
            if line.find('Expand: ') == 0:
                width, height = line[7:line.find(',')].split('x')
                self.bmovl = OSDbmovl(int(width), int(height))
        except:
            pass

