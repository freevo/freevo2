#if 0 /*
# -----------------------------------------------------------------------
# detachbar.py - AudioBar plugin
# by: Viggo Fredriksen <viggo@katatonic.org>
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

# python specific
import time

# freevo specific
import skin,audio.player,plugin
from event import *

# barstates
BAR_HIDE=0 # timedout, reset and change poll interval
BAR_SHOW=1 # show the bar
BAR_IDLE=2 # wait for new track

class PluginInterface(plugin.DaemonPlugin):
    """
    detachbar plugin.
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)

        # tunables
        self.TimeOut  = 3  # 3 seconds till we hide the bar
        self.reset()
        
        # register in list (is this necessery?)
        self.plugin_name = 'audio.detachbar'       
        plugin.register(self, self.plugin_name)

    def reset(self):
        self.status=BAR_HIDE
        self.render = []
        self.player = None
        self.Timer = None
        self.bar = None
        self.setPoll(999999)

    def eventhandler(self, event, menuw=None):
        """
        Needed to catch the PLAY_START event,
        since it now integrates with player.py, 
        this should probably be removed in the future
        (don't have to many dependencies)
        """
        print event
        if self.player and event == PLAY_START:
            if self.status == BAR_IDLE:
                self.refresh()
            else:
                self.show()
        return False

    def timer(self):
        """
        internal timer
        returns status based on idletime
        """
        if self.Timer:
            diff = time.time() - self.Timer
            if diff>self.TimeOut:
                return BAR_HIDE
            else:
                return BAR_IDLE
    
    def hide(self):
        """
        used when hiding the bar
        """
        self.reset()
    
    def show(self):
        """
        used when showing for the first time
        """
        self.player = audio.player.get().player
        self.setPoll(10)       
        self.refresh()
    
    def refresh(self):
        """
        used when updating new songinfo
        """
        self.getInfo()
        self.status = BAR_SHOW
    
    def stop(self):
        """
        stops the player, waiting for timeout
        """
        self.status = BAR_IDLE
        self.Timer = time.time()

    def poll(self):
        """
        update the bar according to showstatus
        """
        if self.status == BAR_SHOW:
            skin.get_singleton().redraw()
        elif self.status == BAR_IDLE:
            self.status = self.timer()
            if self.status == BAR_HIDE:
                self.reset()
            skin.get_singleton().redraw()
    
    def draw(self, (type, object), osd):
        """
        draws the bar
        """
        if self.status == BAR_SHOW:
            font = osd.get_font('detachbar')

            if font==osd.get_font('default'):
                font = osd.get_font('info value')
            
            self.calculatesizes(osd,font)
            osd.drawroundbox(self.x, self.y , self.w, osd.height, (0xf0000000L, 1, 0xb0000000L, 10))

            y = self.t_y
        
            for r in self.render:
                osd.write_text( r, font, None, self.t_x, y, self.t_w, self.font_h, 'center', 'center')
                y+=self.font_h

            progress = '%s/%s' % ( self.formattime(self.player.item.elapsed), self.formattime(self.player.item.length))
            osd.write_text( progress, font, None, self.t_x, y, self.t_w, self.font_h , 'center', 'center')

        return 0
   
    def getInfo(self):
        """
        sets an array of things to draw
        """
        self.render = []
        self.calculate = True
        info = self.player.item.info
        
        # artist : album
        if info['artist'] and info['album']:
            self.render += [ '%s : %s' % ( info['artist'], info['album']) ]
        elif info['album']:
            self.render += [ info['album'] ]
        elif info['artist']:
            self.render += [ info['artist'] ]
        
        # trackno - title
        if info['trackno'] and info['title']:
            self.render += [ '%s - %s' % ( info['trackno'], info['title'] ) ]
        elif info['title']:
            self.render += [ info['title'] ]
        
        # no info available
        if len(self.render)==0:
            self.render += [ self.player.item.name ]
    
    def calculatesizes(self,osd,font):
        """
        sizecalcs is not necessery on every pass
        """
        if self.calculate:
            self.calculate = False
            self.font_h = font.font.height
            
            total_width = osd.width + 2*osd.x
            total_height = osd.height + 2*osd.y
            pad = 10 # padding for safety (overscan may not be 100% correct)
            pad_internal = 5 # internal padding for box vs text
            bar_height = self.font_h
            bar_width = 0
    
            for r in self.render:
                bar_height += self.font_h
                bar_width = self.longest(bar_width,font.font.stringsize(r))
                
            self.y = (total_height - bar_height) - osd.y - pad - pad_internal
            self.x = (total_width - bar_width) - osd.x - pad - pad_internal
            self.w = bar_width + pad + pad_internal + 10
            self.t_y = self.y + pad_internal
            self.t_x = self.x + pad_internal
            self.t_w = bar_width + 5 # incase of shadow
            
    def setPoll(self,interval):
        """
        helper to set the poll_interval
        """
        self.poll_counter = 0
        self.poll_interval = interval
    
    def longest(self,a,b):
        if a>b:
            return a
        return b
        
    def formattime(self,seconds):
        """
        returns string formatted as mins:seconds
        """
        mins = 0
        mins = seconds / 60
        secs = seconds % 60
        
        if secs<10:
            secs = '0%s' % secs
        else:
            secs = '%s' % secs
        return '%i:%s' % (mins,secs)