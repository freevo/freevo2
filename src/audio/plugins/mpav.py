#if 0 /*
# -----------------------------------------------------------------------
# mpav.py - MPlayer Audio Visualization Plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/02/23 05:38:05  gsbarbieri
# i18n: help translators job.
#
# Revision 1.2  2004/02/21 03:19:54  gsbarbieri
# Improvements and bug fixes:
#   - now use path from freevo.conf;
#   - support for new mpav render plugins;
#   - be sure mplayer is playing, just start after 1 second music is playing.
#     It's still annoying, but avoids some locks.
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
import childapp   # Handle child applications
import config
import plugin
import util
import osd
import skin
import string
import time
import thread
from event import *

mmap_file = '/tmp/mpav'
app       = config.CONF.mpav


osd = osd.get_singleton()
skin = skin.get_singleton()


class MPAV( childapp.ChildApp2 ):
    """
    class controlling the in and output from the mpav process
    """
    def __init__( self, app, mplayer, size=None, rplugin=None ):
        self.osd      = osd
        self.item     = mplayer.item
        self.mplayer  = mplayer
        self.lines    = []
        self.messages = []

        if rplugin:
            app += [ "-r", rplugin ]
        childapp.ChildApp2.__init__( self, app )
        
        self.change_resolution( size )
        self.toggle_fs()
    # __init__()
    

    def terminate( self ):
        """
        Stop MPAV
        """        
        self.stop( "quit\n" )
    # stop()


    def stdout_cb( self, line ):
        """
        Get stdout and store in "lines" buffer
        """
        self.lines += [ line ]
        k = "Message ID:"
        if line.find( k ) >= 0:
            self.messages[ -1 ][ -1 ] = line[ len( k ) : ]
    # stdout_cb()


    def add_msg( self, font, x, y, msg ):
        """
        Write message to MPAV screen
        """
        self.write( "cms '%s' %d %d %d 0xffffff 2 2 0x000000 '%s'\n" % ( font.name, font.size, x, y, msg ) )
        self.messages += [ [ font, x, y, msg, "????" ] ]
    # add_msg()


    def del_msg( self, msgid ):
        """
        Delete message from MPAV screen given its id
        msgid is a list: [ font, x, y, msg ]
        """
        for m in self.messages:
            if m[ : -1 ] == msgid:
                self.write( "dm %s\n" % m[ -1 ] )
    # del_msg()


    def toggle_fs( self ):
        """
        Toggle Fullscreen
        """
        self.write( "fs\n" )
    # toggle_fs()


    def change_resolution( self, size ):
        """
        Change resolution
        """
        self.size = size
        if isinstance( size, tuple ):
            self.write( "sr %d %d\n" % size )
    # change_resolution()
# MPAV        


class PluginInterface( plugin.Plugin ):
    """
    MPlayer Audio Visualization Plugin

    This plugin let you view some beautiful graphics while listen to music.

    While playing, you can hit '0' to toggle visualization mode between (in sequence):
       * just visualization (no text, default)
       * visualization + text (title, artist, album)
       * player window (deactivate mpav)

    To activate it, just add to your local_conf.py:

       plugin.activate( 'audio.mpav', args=( ( <width>, <height> ), <render_plugin>) )

    where:
       <width> and <height> are the MPAV window size (or resolution);
       <render_plugin> is the render plugin, it must be in your LD_LIBRARY_PATH or you need to give the full path. Usually it's libmpav_goom.so.

    Notice:
       * If you have a slow machine, don't use it!!!
       * If you experience performance problems, try using lower resolution (decrease width and height).

    You can get MPAV from: http://gsbarbieri.sytes.net/mpav/ while it's not shipped with Freevo.    
    """

    def __init__( self, size=None, rplugin=None ):
        """
        normal plugin init, but sets _type to 'mplayer_audio'
        """
        plugin.Plugin.__init__( self )
        self.start    = False
        self.mpav     = None
        self.player   = None
        self.size     = size
        self.rplugin  = rplugin
        self._type    = "mplayer_audio"
        self.osd_view = 0
        self.messages = []
        config.EVENTS['audio']['0'] = TOGGLE_OSD

        self.plugin_name = "audio.mpav"
        plugin.register( self, self.plugin_name )        
    # __init__()

        
    def play( self, command, player ):
        """
        called before playing is started to add some stuff to the command line
        """
        self.player = player
        return command + [ "-af", "export=" + mmap_file ]
    # play()


    def eventhandler( self, event ):
        """
        eventhandler to simulate hide/show of mpav
        """
        if event == TOGGLE_OSD:
            if   self.osd_view == 0 and self.mpav:
                self.show_info_mpav()
            elif self.osd_view == 1 and self.mpav:
                self.stop_mpav()
            elif self.osd_view == 2 and not self.mpav:
                self.start_mpav()

            self.osd_view = ( self.osd_view + 1 ) % 3
            return True
    # eventhandler()


    def stdout( self, line ):
        """
        get information from mplayer stdout
        """
        if self.mpav:
            return

        try:
            if line.find( "[export] Memory mapped to file: "+mmap_file ) == 0:
                self.start = True
                _debug_( "Detected MPlayer 'export' audio filter! Using MPAV." )
        except:
            pass

    # stdout()


    def elapsed( self, elapsed ):
        # Be sure mplayer started playing, it need to setup mmap first.
        if self.start and elapsed > 0:
            self.start_mpav()
            self.start = False
    # stdout()


    def start_mpav( self ):
        """
        start mpav
        """
        if not self.mpav:
            command = [ app, "-s", "-f", mmap_file ]
            self.mpav = MPAV( command, self.player, self.size, self.rplugin )
            
            if self.osd_view == 1:
                self.show_info_mpav()
            
    # start_mpav()


    def stop_mpav( self ):
        """
        stop mpav
        """
        if self.mpav:
            self.mpav.terminate()
            self.mpav = None
    # stop_mpav()    


    def show_info_mpav( self ):
        """
        show info on MPAV screen
        """
        font = skin.get_font( "default" )
        iattr = self.player.item.getattr
        x, y = 10, 10
        for a in ( "title", "artist", "album" ):
            m = String( _( string.capwords( a ) ) + ":", "latin-1" )
            m += " " + String( iattr( a ), "latin-1" ) 
            self.mpav.add_msg( font, x, y, m )
            y += font.height
    # show_info_mpav()


    def stop( self ):
        """
        stop plugin
        """
        self.stop_mpav()
    # stop()
# PluginInterface
