# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mplayervis.py - Native Freevo MPlayer Audio Visualization Plugin
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id$
#
# Notes: - I'm no fan of all the skin.clear() being done :(
# Todo:  - Migrate with Gustavos pygoom when done and change name to mpav
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2004/07/22 21:21:47  dischi
# small fixes to fit the new gui code
#
# Revision 1.6  2004/07/10 12:33:38  dischi
# header cleanup
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


try:
    import pygoom
except:
    raise Exception('[audio.mplayervis]: Pygoom not available, please install '+
                    'or remove this plugin (http://freevo.sf.net/pygoom).')


# pygame  modules
from pygame import Rect, image, transform, Surface

# freevo modules
import plugin, config, rc, skin, osd, time

from event          import *
from gui.animation      import render, BaseAnimation

mmap_file = '/tmp/mpav'
skin = skin.get_singleton()
osd  = osd.get_singleton()


class mpv_Goom(BaseAnimation):
    message    = None
    coversurf  = None

    blend      = 255
    blend_step = -2
    max_blend  = 250
    c_timeout  = 8         # seconds on cover
    v_timeout  = 30        # seconds on visual
    timeout    = v_timeout # start waiting with cover

    def __init__(self, x, y, width, height, coverfile=None):
        self.coverfile = coverfile

        BaseAnimation.__init__(self, (x, y, width, height), fps=100,
                               bg_update=False, bg_redraw=False)
        pygoom.set_exportfile(mmap_file)
        pygoom.set_resolution(width, height, 0)



    def set_cover(self, coverfile):
        """
        Set a blend image to toggle between visual and cover
        Updated when resolution is changed
        """
        self.coverfile = coverfile


    def set_message(self, message, timeout=5):
        """
        Pass a message to the screen.

        @message: text to draw
        @timeout: how long to display
        """

        font = skin.get_font('detachbar')
        w = font.stringsize(message)
        h = font.height
        x = 10
        y = 10

        s = Surface((w,h), 0, 32)

        osd.drawstringframed(message, 0, 0, w, h, font,
                             mode='hard', layer=s)

        self.m_timer   = time.time()
        self.m_timeout = timeout
        self.message   = (s, x, y, w, h)


    def set_resolution(self, x, y, width, height, cinemascope=0, clear=False):
        r = Rect (x, y, width, height)
        if r == self.rect:
            return

        # clear message
        self.message = None

        self.rect = r
        pygoom.set_resolution(width, height, cinemascope)

        # change the cover if neceserry
        if self.coverfile:
            s = image.load(self.coverfile)

            # scale and fit to the rect
            w, h   = s.get_size()
            aspect = float(w)/float(h)

            if aspect < 1.0:
                w = self.rect.width
                h = float(w) / aspect
                x = 0
                y = (self.rect.height - h) / 2
            else:
                h = self.rect.height
                w = float(h) * aspect
                y = 0
                x = (self.rect.width - w)  / 2

            self.coversurf = (transform.scale(s,(w, h)), x, y)
            self.max_blend = 250
            self.c_timer   = time.time()


    def set_fullscreen(self):
        t_h = config.CONF.height-2*config.OSD_OVERSCAN_Y
        w   = config.CONF.width-2*config.OSD_OVERSCAN_X

        # ~16:9
        h   = int(9.0*float(w)/16.0)
        y   = ((t_h-h)/2) + config.OSD_OVERSCAN_Y
        x   = config.OSD_OVERSCAN_X

        self.set_resolution(x, y, w, h, 0)
        self.max_blend = 80


    def poll(self, current_time):
        """
        override to get extra performance
        """

        if self.next_update < current_time:

            self.next_update = current_time + self.interval
            gooms = pygoom.get_surface()

            # draw blending
            if self.coversurf:
                self.blend += self.blend_step

                if self.blend > self.max_blend:
                    self.blend = self.max_blend
                elif self.blend < 0:
                    self.blend     = 0
                    self.max_blend = 120

                if time.time() - self.c_timer > self.timeout:
                    if self.timeout == self.c_timeout:
                        self.timeout = self.v_timeout
                    else:
                        self.timeout = self.c_timeout

                    self.c_timer = time.time()
                    self.blend_step = - self.blend_step

                if self.blend > 0:
                    s, x, y = self.coversurf
                    s.set_alpha(self.blend)
                    gooms.blit(s, (x, y))

            # draw message
            if self.message:
                s, x, y, w, h = self.message

                if time.time() - self.m_timer > self.m_timeout:
                    self.message = False
                    s.fill(0)

                gooms.blit(s, (x,y))

            osd.putsurface(gooms, self.rect.left, self.rect.top)
            osd.update(self.rect)

### MODE definitions
DOCK = 0 # dock ( default )
FULL = 1 # fullscreen
NOVI = 2 # no view

class PluginInterface(plugin.Plugin):
    """
    Native mplayer audiovisualization for Freevo.
    Dependant on the pygoom module. Available at
    the freevo addons page.

    Activate with:
     plugin.activate('audio.mplayervis')

    When activated one can change between view-modes
    with the 0 (zero) button.
    """
    player = None
    visual = None
    view   = DOCK
    passed_event = False
    detached = False

    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type    = 'mplayer_audio'
        self.app_mode = 'audio'

        # Event for changing between viewmodes
        config.EVENTS['audio']['0'] = Event('CHANGE_MODE')

        self.plugin_name = 'audio.mplayervis'
        plugin.register(self, self.plugin_name)

        self.view_func = [self.dock,
                          self.fullscreen,
                          self.noview]


    def play( self, command, player ):
        self.player = player
        self.item   = player.playerGUI.item

        return command + [ "-af", "export=" + mmap_file ]


    def toggle_view(self):
        """
        Toggle between view modes
        """
        self.view += 1
        if self.view > 2:
            self.view = DOCK

        if not self.visual:
            self.start_visual()
        else:
            self.view_func[self.view]()


    def eventhandler( self, event=None, arg=None ):
        """
        eventhandler to simulate hide/show of mpav
        """

        if event == 'CHANGE_MODE':
            self.toggle_view()
            return True

        if self.visual and self.view == FULL:

            if event == OSD_MESSAGE:
                self.visual.set_message(event.arg)
                return True

            if self.passed_event:
                self.passed_event = False
                return False

            self.passed_event = True

            if event != PLAY_END:
                return self.player.eventhandler(event)

        return False


    def item_info(self, fmt=None):
        """
        Returns info about the current running song
        """

        if not fmt:
            fmt = u'%(a)s : %(l)s  %(n)s.  %(t)s (%(y)s)   [%(s)s]'

        item    = self.item
        info    = item.info
        name    = item.name
        length  = None
        elapsed = '0'

        if info['title']:
            name = info['title']

        if item.elapsed:
            elapsed = '%i:%02i' % (int(item.elapsed/60), int(item.elapsed%60))

        if item.length:
            length = '%i:%02i' % (int(item.length/60), int(item.length%60))

        song = { 'a' : info['artist'],
                 'l' : info['album'],
                 'n' : info['trackno'],
                 't' : name,
                 'e' : elapsed,
                 'i' : item.image,
                 'y' : info['year'],
                 's' : length }

        return fmt % song


    def fullscreen(self):
        if self.player.playerGUI.visible:
            self.player.playerGUI.hide()

        self.visual.set_fullscreen()
        self.visual.set_message(self.item_info())
        skin.clear()
        rc.app(self)

    def noview(self):

        if rc.app() != self.player.eventhandler:
            rc.app(self.player)

        if self.visual:
            self.stop_visual()

        if not self.player.playerGUI.visible:
            self.player.playerGUI.show()


    def dock(self):
        if rc.app() != self.player.eventhandler:
            rc.app(self.player)

        # get the rect from skin
        #  XXX someone with better knowlegde of the
        #      skin code should take a look at this
        imgarea = skin.areas['view']
        c = imgarea.calc_geometry(imgarea.layout.content, copy_object=True)
        w = c.width   - 2*c.spacing
        h = c.height  - 2*c.spacing
        x = c.x + c.spacing
        y = c.y + c.spacing

        # check if the view-area has a rectangle
        try:
            r = c.types['default'].rectangle
            x -= r.x
            y -= r.y
            w += 2*r.x
            h += 2*r.y
        except:
            pass

        self.visual.set_resolution(x, y, w, h, 0, False)



    def start_visual(self):
        if self.visual or self.view == NOVI:
            return

        if rc.app() == self.player.eventhandler:

            self.visual = mpv_Goom(300, 300, 150, 150, self.item.image)

            if self.view == FULL:
                self.visual.set_message(self.item.name, 10)

            self.view_func[self.view]()
            self.visual.start()


    def stop_visual(self):
        if self.visual:
            self.visual.remove()
            self.visual = None
            pygoom.quit()


    def stop(self):
        self.stop_visual()


    def stdout(self, line):
        """
        get information from mplayer stdout

        It should be safe to do call start() from here
        since this is now a callback from main.
        """
        if self.visual:
            return

        if line.find( "[export] Memory mapped to file: " + mmap_file ) == 0:
            _debug_( "Detected MPlayer 'export' audio filter! Using MPAV." )
            self.start_visual()
