#if 0 /*
# -----------------------------------------------------------------------
# mplayervis.py - Native Freevo MPlayer Audio Visualization Plugin
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# Notes: - I'm no fan of all the skin.clear() being done :(
# Todo:  - Migrate with Gustavos pygoom when done and change name to mpav
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
try:
    import pygoom
except:
    raise Exception('[audio.mplayervis]: Pygoom not available, please install or remove this plugin.')


# pygame  modules
from pygame import Rect, image, transform, Surface

# freevo modules
import plugin, config, rc, skin, osd, time

from event          import *
from animation      import render, BaseAnimation

mmap_file = '/tmp/mpav'
skin = skin.get_singleton()
osd = osd.get_singleton()


class mpv_Goom(BaseAnimation):
    message    = None
    coversurf  = None

    blend      = 122
    blend_step = -2
    max_blend  = 120
    c_timeout  = 8         # seconds on cover
    v_timeout  = 30        # seconds on visual
    timeout    = v_timeout # start waiting with cover

    def __init__(self, x, y, width, height, coverfile=None):
        self.coverfile = coverfile

        BaseAnimation.__init__(self, (x, y, width, height), fps=40,
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
        x = config.OSD_OVERSCAN_X + 10
        y = config.OSD_OVERSCAN_Y + 10

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
            self.coversurf = transform.scale(image.load(self.coverfile),
                                             (self.rect.width, self.rect.height))
        self.max_blend = 120

        self.c_timer = time.time()

        if clear:
            skin.clear()


    def set_fullscreen(self):
        self.set_resolution(config.OSD_OVERSCAN_X, config.OSD_OVERSCAN_Y,
                            config.CONF.width-2*config.OSD_OVERSCAN_X,
                            config.CONF.height-2*config.OSD_OVERSCAN_Y,
                            1, False)
        self.max_blend = 80


    def poll(self, current_time):
        """
        override to get extra performance
        """

        if self.next_update < current_time:# and not self.wait:

            self.next_update = current_time + self.interval
            gooms = pygoom.get_surface()

            # draw blending
            if self.coversurf:
                self.blend += self.blend_step

                if self.blend > self.max_blend:
                    self.blend = self.max_blend
                elif self.blend < 0:
                    self.blend = 0

                if time.time() - self.c_timer > self.timeout:
                    if self.timeout == self.c_timeout:
                        self.timeout = self.v_timeout
                    else:
                        self.timeout = self.c_timeout

                    self.c_timer = time.time()
                    self.blend_step = - self.blend_step

                if self.blend > 0:
                    self.coversurf.set_alpha(self.blend)
                    gooms.blit(self.coversurf, (0,0))

            # draw message
            if self.message:
                s, x, y, w, h = self.message

                if time.time() - self.m_timer > self.m_timeout:
                    self.message = False
                    s.fill(0)

                gooms.blit(s, (x,y))

            osd.putsurface(gooms, self.rect.left, self.rect.top)
            osd.update(self.rect)


class PluginInterface(plugin.Plugin):
    """
    Native mplayer audiovisualization for Freevo.
    Dependant on the pygoom module. Available at
    the freevo addons page.

    Activate with:
     plugin.activate('audio.mplayervis')
    """

    start  = False
    player = None
    visual = None
    view   = 0
    passed_event = False
    detached = False

    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type    = "mplayer_audio"

        # Event for changing between viewmodes
        config.EVENTS['audio']['0'] = TOGGLE_OSD

        self.plugin_name = "audio.mplayervis"
        plugin.register(self, self.plugin_name)


    def play( self, command, player ):
        self.player = player

        return command + [ "-af", "export=" + mmap_file ]


    def eventhandler( self, event=None, arg=None ):
        """
        eventhandler to simulate hide/show of mpav
        """
        if self.visual and self.player and self.player.playerGUI.visible:
            if event == TOGGLE_OSD and self.view in [0, 1]:
                if self.view == 1:
                    self.dock()

                elif self.view == 0:
                    self.fullscreen()

            elif event == OSD_MESSAGE and self.view == 1:
                self.visual.set_message(event.arg)

            elif self.player:
                if self.passed_event:
                    self.passed_event = False
                    return False
                self.passed_event = True

                # XXX Sending MIXER stuff messes up fullscreen
                if self.view == 1 and event in (STOP, PLAY_END, USER_END, PAUSE,
                                                AUDIO_SEND_MPLAYER_CMD, PLAY,
                                                SEEK,PLAYLIST_PREV, PLAYLIST_NEXT ):

                    return self.player.eventhandler(event)

                else:
                    return self.player.eventhandler(event)

            return True


    def check_image(self):
        if self.player:
            img = self.player.item.image

        if img:
            self.visual.set_cover(img)


    def fullscreen(self):
        if self.player:
            self.player.playerGUI.hide()

        self.visual.set_fullscreen()

        rc.app(self)
        rc.set_context('audio')
        self.view = 1


    def dock(self):
        if self.player:
            rc.app(self.player)

        # get the rect from skin
        imgarea = skin.areas['view']
        c = imgarea.calc_geometry(imgarea.layout.content, copy_object=True)
        w = c.width  - 2*c.spacing
        h = c.height - 2*c.spacing
        x = c.x - c.spacing
        y = c.y - c.spacing

        if self.view == 1:
            self.player.playerGUI.show()
            self.visual.set_resolution(x, y, w, h, 0, True)

        else:
            self.visual.set_resolution(x, y, w, h, 0, False)

        self.view = 0


    def detach(self):
        rc.app(None)
        self.view = 3


    def stdout(self, line):
        """
        get information from mplayer stdout
        """
        if self.visual:
            return

        try:
            if line.find( "[export] Memory mapped to file: "+mmap_file ) == 0:
                self.start = True
                _debug_( "Detected MPlayer 'export' audio filter! Using MPAV." )
        except:
            pass


    def elapsed(self, elapsed):
        # Be sure mplayer started playing, it need to setup mmap first.
        if self.start and elapsed > 0 and self.player and self.player.playerGUI.visible:
            self.start_visual()
            self.start = False


    def start_visual(self):
        if not self.visual:
            self.visual = mpv_Goom(300, 300, 150, 150)

            if self.player and self.view == 1:
                self.visual.set_message(self.player.item.name, 10)

            self.check_image()

            # plain docked in playergui
            if self.view == 0:
                self.dock()

            # plain fullscreen
            elif self.view == 1:
                self.fullscreen()

            # previously detached
            elif self.view == 3 and self.player.playerGUI.visible:
                skin.clear()
                self.view = 0
                self.dock()

            render.get_singleton().set_realtime(True)
            self.visual.start()

    def stop_visual(self):
        if self.visual:
            self.visual.remove()
            render.get_singleton().set_realtime(False)
            pygoom.quit()
            self.visual = None

            # XXX this is hackish()
            if self.view == 3 and self.player.playerGUI.visible:
                skin.clear()

    def stop(self):
        self.stop_visual()

