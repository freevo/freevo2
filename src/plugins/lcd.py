#if 0 /*
# -----------------------------------------------------------------------
# lcd.py - use PyLCD to display menus and music player
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#    To activate, put the following line in local_conf.py:
#       plugin.activate('lcd')
# Todo:        
#    1) Use Threads. PyLCD is too blocking!
#    2) Have Movie Player, TV Player and Image viewer to use LCD
#    3) Better (and more) LCD screens.
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/08/27 13:02:31  gsbarbieri
# 2x20 and 2x40 screens.
# Also, fixed some crashes
#
# Revision 1.6  2003/08/24 19:42:25  gsbarbieri
# Support 2x16 displays
#
# Revision 1.5  2003/08/20 22:48:25  gsbarbieri
# Try-Except to avoid crashes + MAME items handling
#
# Revision 1.4  2003/08/04 20:30:33  gsbarbieri
# Added some clauses to avoid exceptions.
#
# Revision 1.3  2003/08/04 04:08:10  gsbarbieri
# Now you can have screens for Lines x Columns, before we could just have screens for Lines.
#
# Revision 1.2  2003/08/04 03:02:03  gsbarbieri
# Changes from Magnus:
#    * Progress bar
#    * Animation
#    * UnicodeError handling
#
# Revision 1.1  2003/07/23 07:16:00  gsbarbieri
# New plugin: LCD
# This plugin show the selected menu item and some info about it and info
# about the item being played using a LCD display (using pyLCD: http://www.schwarzvogel.de/software-pylcd.shtml)
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

import copy
import pylcd
import time
import plugin
import config
DEBUG=1
# Configuration: (Should move to freevo_conf.py?)
sep_str = " | " # use as separator between two strings. Like: "Length: 123<sep_str>Plot: ..."

# Animaton-Sequence used in audio playback
# Some displays (like the CrytstalFontz) do display the \ as a /
animation_audioplayer_chars = ['-','\\','|','/']


# menu_info: information to be shown when in menu
# Structure:
#
# menu_info = {
#     <TYPE> : [ ( <ATTRIBUTE>, <FORMAT_STRING> ), ... ],
#    }
# <ATTRIBUTE> is some valid attribute to item.getattr()
menu_info = {
    "main" : [ ],
    "audio" : [ ( "length", "Length: %s" ),
                ( "artist", "Artist: %s" ),
                ( "album", "Album: %s" ),
                ( "year", "Year: %s" ) ],
    "audiocd" : [ ( "len(tracks)", "Tracks: %s" ),
                  ( "artist", "Artist: %s" ),
                  ( "album", "Album: %s" ),
                  ( "year", "Year: %s" ) ],
    "video" : [ ( "length", "Length: %s" ),
                ( "geometry", "Resolution: %s" ),
                ( "aspect", "Aspect: %s" ),
                ( "tagline", "Tagline: %s" ),
                ( "plot", "Plot: %s" ) ],
    "dir" : [ ( "plot", "Plot: %s" ),
              ( "tagline", "Tagline: %s" ) ],
    "image" : [ ( "geometry", "Geometry: %s" ),
                ( "date", "Date: %s" ),
                ( "description", "Description: %s" ) ],
    "playlist" : [ ( "len(playlist)", "%s items" ) ],
    "mame" : [ ( "description", "Description: %s" ) ],
    "unknow" : [ ]
    }
# menu_strinfo: will be passed to time.strinfo() and added to the end of info (after menu_info)
menu_strinfo = {
    "main" : "%H:%M - %a, %d-%b", # I like time in main menu
    "audio" : None,
    "audiocd" : None,
    "video" : None,
    "image" : None,
    "dir" : None,
    "playlist" : None,
    "mame" : None,
    "unknow" : None
    }


# layouts: dict of layouts (screens and widgets)
# Structure:
#
# layouts = { <#_OF_LINES_IN_DISPLAY> :
#             { <#_OF_CHARS_IN_LINES> :
#                { <SCREEN_NAME> :
#                  <WIDGET_NAME> : ( <WIDGET_TYPE>,
#                                    <WIDGET_PARAMETERS>,
#                                    <PARAMETERS_VALUES> ),
#                  ...
#                  <MORE_WIDGETS>
#                  ...
#                },
#                ...
#                <MORE_SCREENS>
#                ...
#              }
#           }
# Note:
#    <PARAMETERS_VALUES>: will be used like this:
#       <WIDGET_PARAMETERS> % eval( <PARAMETERS_VALUES> )
#    There should be at least these screens:
#       welcome: will be the shown during the startup
#          menu: will be used in menu mode
#        player: will be used in player mode
#            tv: will be used in tv mode
# Values should match the ones supported by LCDd (man LCDd)
layouts = { 4 : # 4 lines display
            
            { 40 : # 40 chars per line
              
              # Welcome screen
              { "welcome" : 
                { "title"    : ( "title",
                                 "Freevo",
                                 None ),
                  "calendar" : ( "scroller",
                                 "1 2 %d 2 h 2 \"Today is %s.\"",
                                 "( self.width, time.strftime('%A, %d-%B') )" ),
                  "clock"    : ( "string",
                                 "%d 3 \"%s\"",
                                 "( ( self.width - len( time.strftime('%T') ) ) / 2 + 1 ," + \
                                 " time.strftime('%T') )" )
                  },
                
                "menu"    :
                { "title_l"  : ( "string",
                                 "1 1 'MENU: '",
                                 None ),
                  "item_l"   : ( "string",
                                 "1 2 'ITEM: '",
                                 None ),
                  "type_l"   : ( "string",
                                 "1 3 'TYPE: '",
                                 None ),
                  "info_l"   : ( "string",
                                 "1 4 'INFO: '",
                                 None ),                
                  "title_v"  : ( "scroller",
                                 "7 1 %d 1 h 2 \"%s\"",
                                 "( self.width, menu.heading )" ),
                  "item_v"   : ( "scroller",
                                 "7 2 %d 2 h 2 \"%s\"",
                                 "( self.width, title )" ),
                  "type_v"   : ( "scroller",
                                 "7 3 %d 3 h 2 \"%s\"",
                                 "( self.width, typeinfo )" ),
                  "info_v"   : ( "scroller",
                                 "7 4 %d 1 h 2 \"%s\"",
                                 "( self.width, info )" )
                  },
                
                "audio_player"  :
                { "music_l"   : ( "string",
                                  "2 1 'MUSIC: '",
                                  None ),
                  "album_l"   : ( "string",
                                  "2 2 'ALBUM: '",
                                  None ),
                  "artist_l"  : ( "string",
                                  "1 3 'ARTIST: '",
                                  None ),
                  "music_v"   : ( "scroller",
                                  "9 1 %d 1 h 2 \"%s\"",
                                "( self.width, title )" ),
                  "album_v"   : ( "scroller",
                                  "9 2 %d 2 h 2 \"%s\"",
                                  "( self.width, player.getattr('album') )" ),
                  "artist_v"  : ( "scroller",
                                  "9 3 %d 3 h 2 \"%s\"",
                                  "( self.width, player.getattr('artist') )" ),
                  "time_v"    : ( "string",
                                  "2 4 '% 2d:%02d/% 2d:%02d ( %2d%%)'",
                                  "( int(player.length / 60), int(player.length % 60)," +
                                  " int(player.elapsed / 60), int(player.elapsed % 60)," +
                                  " int(player.elapsed * 100 / player.length) )" ),
                  "timebar1_v": ( "string", "21 4 '['", None),
                  "timebar2_v": ( "string", "40 4 ']'", None),
                  "timebar3_v": ( "hbar",
                                  "22 4 '%d'","(int(player.elapsed *90 / player.length))"),
                  # animation at the begining of the time line
                  "animation_v": ( "string", "1 4 '%s'",
                                   "animation_audioplayer_chars[" +
                                   " player.elapsed % len(animation_audioplayer_chars)]")
                  },
                
                "tv"            :
                { "chan_l"   : ( "string",
                                 "1 1 'CHAN: '",
                                 None ),
                  "prog_l"   : ( "string",
                                 "1 2 'PROG: '",
                                 None ),
                  "time_l"  : ( "string",
                                "1 3 'TIME: '",
                                None ),
                  "desc_l"  : ( "string",
                                "1 4 'DESC: '",
                                None ),                
                  "chan_v"   : ( "scroller",
                                 "7 1 %d 1 h 2 \"%s\"",
                                 "( self.width, tv.channel_id )" ),
                  "prog_v"   : ( "scroller",
                                 "7 2 %d 2 h 2 \"%s\"",
                                 "( self.width, tv.title )" ),
                  "time_v"   : ( "scroller",
                                 "7 3 %d 3 h 2 \"%s-%s\"",
                                 "( self.width, tv.start, tv.stop )" ),
                  "desc_v"   : ( "scroller",
                                 "7 4 %d 4 h 2 \"%s\"",
                                 "( self.width, tv.desc )" )
                  }
                },              

              20 : # 20 chars per line
              
              # Welcome screen
              { "welcome" : 
                { "title"    : ( "title",
                                 "Freevo",
                                 None ),
                  "calendar" : ( "scroller",
                                 "1 2 %d 2 h 2 \"Today is %s.\"",
                                 "( self.width, time.strftime('%A, %d-%B') )" ),
                  "clock"    : ( "string",
                                 "%d 3 \"%s\"",
                                 "( ( self.width - len( time.strftime('%T') ) ) / 2 + 1 ," + \
                                 " time.strftime('%T') )" )
                  },
                
                "menu"    :
                { "title_v"  : ( "scroller",
                                 "1 1 %d 1 h 2 \"%s\"",
                                 "( self.width, menu.heading )" ),
                  "item_v"   : ( "scroller",
                                 "1 2 %d 2 h 2 \"%s\"",
                                 "( self.width, title )" ),
                  "type_v"   : ( "scroller",
                                 "1 3 %d 3 h 2 \"%s\"",
                                 "( self.width, typeinfo )" ),
                  "info_v"   : ( "scroller",
                                 "1 4 %d 1 h 2 \"%s\"",
                                 "( self.width, info )" )
                  },
                
                "audio_player"  :
                { "music_v"   : ( "scroller",
                                  "1 1 %d 1 h 2 \"%s\"",
                                  "( self.width, title )" ),
                  "album_v"   : ( "scroller",
                                  "1 2 %d 2 h 2 \"%s\"",
                                  "( self.width, player.getattr('album') )" ),
                  "artist_v"  : ( "scroller",
                                  "1 3 %d 3 h 2 \"%s\"",
                                  "( self.width, player.getattr('artist') )" ),
                  "time_v"    : ( "string",
                                  "2 4 '% 2d:%02d/% 2d:%02d ( %2d%%)'",
                                  "( int(player.length / 60), int(player.length % 60)," +
                                  " int(player.elapsed / 60), int(player.elapsed % 60)," +
                                  " int(player.elapsed * 100 / player.length) )" ),
                  # animation at the begining of the time line
                  "animation_v": ( "string", "1 4 '%s'",
                                   "animation_audioplayer_chars[player.elapsed % len(animation_audioplayer_chars)]")
                  },
                
                "tv"            :
                { "chan_v"   : ( "scroller",
                                 "1 1 %d 1 h 2 \"%s\"",
                                 "( self.width, tv.channel_id )" ),
                  "prog_v"   : ( "scroller",
                                 "1 2 %d 2 h 2 \"%s\"",
                                 "( self.width, tv.title )" ),
                  "time_v"   : ( "scroller",
                                 "1 3 %d 3 h 2 \"%s-%s\"",
                                 "( self.width, tv.start, tv.stop )" ),
                  "desc_v"   : ( "scroller",
                                 "1 4 %d 4 h 2 \"%s\"",
                                 "( self.width, tv.desc )" )
                  }              
                } # screens
              }, # chars per line


            2 : # 2 lines display            
            { 16 : # 16 chars per line
              # Welcome screen
              { "welcome" :
                { "title"    : ( "title",
                                 "1 1 Freevo",
                                 None )
                  },

                 "menu"    :
                 { "title_v"  : ( "scroller",
                                  "1 1 %d 1 h 2 \"%s\"",
                                  "( self.width, menu.heading )" ),
                   "item_v"   : ( "scroller",
                                  "1 2 %d 2 h 2 \"%s\"",
                                  "( self.width, title )" )
                   },

                 "audio_player"  :
                 { "music_v"   : ( "scroller",
                                   "1 1 %d 1 h 2 \"%s\"",
                                   "( self.width, title )" ),
                   "time_v"    : ( "string",
                                   "1 2 '  % 2d:%02d/% 2d:%02d'",
                                   "( int(player.length / 60), int(player.length % 60)," +
                                   " int(player.elapsed / 60), int(player.elapsed % 60))" )
                   },

                 "tv"            :
                 { "chan_v"   : ( "scroller",
                                  "1 1 %d 1 h 2 \"%s\"",
                                  "( self.width, tv.display_name) )" ),
                   "prog_v"   : ( "scroller",
                                  "1 2 %d 2 h 2 \"%s\"",
                                  "( self.width, tv.title )" )
                   }
                },
              
              20 : # 20 chars per line
              # Welcome screen
              { "welcome":
                { "title"    : ( "title",
                                 "1 1 Freevo",
                                 None )
                  },

                 "menu"    :
                 { "title_v"  : ( "scroller",
                                  "1 1 %d 1 h 2 \"%s\"",
                                  "( self.width, menu.heading )" ),
                   "item_v"   : ( "scroller",
                                  "1 2 %d 2 h 2 \"%s\"",
                                  "( self.width, title )" )
                   },

                 "audio_player":
                 { "music_v"   : ( "scroller",
                                   "1 1 %d 1 h 2 \"%s\"",
                                   "( self.width, title )" ),
                   "time_v"    : ( "string",
                                   "1 2 '  % 2d:%02d/% 2d:%02d'",
                                   "( int(player.length / 60), int(player.length % 60)," +
                                   " int(player.elapsed / 60), int(player.elapsed % 60))" )
                   },

                 "tv":
                 { "chan_v"   : ( "scroller",
                                  "1 1 %d 1 h 2 \"%s\"",
                                  "( self.width, tv.display_name) )" ),
                   "prog_v"   : ( "scroller",
                                  "1 2 %d 2 h 2 \"%s\"",
                                  "( self.width, tv.title )" )
                   }
                 },
              
              40 : # 40 chars per line
              # Welcome screen
              { "welcome":
                { "title"    : ( "title",
                                 "1 1 Freevo",
                                 None )
                  },

                 "menu":
                 { "title_l"  : ( "string",
                                 "1 1 'MENU: '",
                                 None ),
                  "item_l"   : ( "string",
                                 "1 2 'ITEM: '",
                                 None ),
                   "title_v"  : ( "scroller",
                                  "7 1 %d 1 h 2 \"%s\"",
                                  "( self.width, menu.heading )" ),
                   "item_v"   : ( "scroller",
                                  "7 2 %d 2 h 2 \"%s\"",
                                  "( self.width, title )" )
                   },

                 "audio_player":
                 { "music_l"   : ( "string",
                                  "1 1 'MUSIC: '",
                                  None ),
                  "music_v"   : ( "scroller",
                                  "8 1 %d 1 h 2 \"%s\"",
                                "( self.width, title )" ),
                  "time_v"    : ( "string",
                                  "2 2 '% 2d:%02d/% 2d:%02d ( %2d%%)'",
                                  "( int(player.length / 60), int(player.length % 60)," +
                                  " int(player.elapsed / 60), int(player.elapsed % 60)," +
                                  " int(player.elapsed * 100 / player.length) )" ),
                  "timebar1_v": ( "string", "21 2 '['", None),
                  "timebar2_v": ( "string", "40 2 ']'", None),
                  "timebar3_v": ( "hbar",
                                  "22 2 '%d'","(int(player.elapsed *90 / player.length))"),
                  # animation at the begining of the time line
                  "animation_v": ( "string", "1 2 '%s'",
                                   "animation_audioplayer_chars[" +
                                   " player.elapsed % len(animation_audioplayer_chars)]")
                  },

                "tv":
                { "chan_l"   : ( "string",
                                 "1 1 'CHAN: '",
                                 None ),
                  "prog_l"   : ( "string",
                                 "1 2 'PROG: '",
                                 None ),
                  "chan_v"   : ( "scroller",
                                 "7 1 %d 1 h 2 \"%s\"",
                                 "( self.width, tv.channel_id )" ),
                  "prog_v"   : ( "scroller",
                                 "7 2 %d 2 h 2 \"%s\"",
                                 "( self.width, tv.title )" ),
                  "time_v"   : ( "scroller",
                                 "%d 1 %d 3 h 2 \"[%s-%s]\"",
                                 "( self.width - 13, 13, tv.start, tv.stop )" ),
                  }
                } # screens
              } # chars per line
            } # lines per display
             
# poll_widgets: widgets that should be refreshed during the pool
# Structure:
#
# poll_widgets = { <#_OF_LINES_IN_DISPLAY> :
#                  { <SCREEN_NAME> : ( <WIDGET_NAME>, ... ) },
#                  ...
#                }
poll_widgets = { 4 : {
    40 : { "welcome" : [ "clock" ] },
    20 : { "welcome" : [ "clock" ] },    
    },
                 }

DEBUG = config.DEBUG

def get_info( item, list ):
    info = ""

    for l in list:

        v = item.getattr( l[ 0 ] )
        if v:
            if info:
                info += sep_str
            info += l[ 1 ] % v

    return info



class PluginInterface( plugin.DaemonPlugin ):
    def __init__( self ):
        """
        init the lcd
        """
        plugin.DaemonPlugin.__init__( self )
        try:
            self.lcd = pylcd.client()
            cm = self.lcd.connect()
        except:
            print "ERROR: LCD plugin will not load! " + \
                  "Maybe you don't have LCDd (lcdproc daemon) running?"
            self.disable = 1
            return
        
        if DEBUG > 0:
            print "Connecting to LCD: %s" % cm
            print "Info as know by the module:"
            self.lcd.getinfo()
            print ""
            
        plugin.register( self, "lcd" )

        self.poll_interval = 10
        self.disable = 0
        self.height = self.lcd.d_height
        self.width  = self.lcd.d_width
        self.generate_screens()
        if self.disable:
            return
        
        # Show welcome screen:
        for w in self.screens[ "welcome" ]:
            type, param, val = self.screens[ "welcome" ][ w ]            
            if val: param = param % eval( val )

            try:
                self.lcd.widget_set( "welcome", w, param.encode( 'latin1' ) )
            except UnicodeError:
                self.lcd.widget_set( "welcome", w, param )
                
        self.lcd.screen_set( "welcome", "-priority 192 -duration 2 -heartbeat off" )
        self.last_screen = "welcome"

        self.lsv = { } # will hold last screen value (lsv)

    def close( self ):
        """
        to be called before the plugin exists.
        It terminates the connection with the server
        """
        #self.lcd.send( "bye" )
        
    def draw( self, ( type, object ), osd ):
        """
        'Draw' the information on the LCD display.
        """
        if self.disable: return

        sname = type
        if type == 'menu':   
            menu  = object.menustack[ -1 ]
            title = menu.selected.name
            typeinfo = menu.selected.type
            info = ""

            if menu.selected.getattr( 'type' ):
                typeinfo = menu.selected.getattr( 'type' )

            # get info:
            if menu.selected.type and menu_info.has_key( menu.selected.type ):
                info = get_info( menu.selected, menu_info[ menu.selected.type ] )
                if menu_strinfo.has_key( menu.selected.type ) and menu_strinfo[ menu.selected.type ]:
                    if info:
                        info += sep_str
                    info += time.strftime( menu_strinfo[ menu.selected.type ] )

            # specific things related with item type
            if menu.selected.type == 'audio':
                title = menu.selected.getattr( 'title' )
                if menu.selected.getattr( 'trackno' ):
                    title = "%s - %s" % ( menu.selected.getattr( 'trackno' ), title )
                    
        elif type == 'player':
            player = object
            title  = player.getattr( 'title' )
            if player.getattr( 'trackno' ):
                title = "%s - %s" % ( player.getattr( 'trackno' ), title )                
            sname  = "%s_%s" % ( player.type, type )

            
        elif type == 'tv':
            tv = copy.copy( object.selected )

            if tv.start == 0:
                tv.start = " 0:00"
                tv.stop  = "23:59" # could also be: '????'
            else:
                tv.start = time.localtime( tv.start )
                tv.stop  = time.localtime( tv.stop )
                
                tv.start = "% 2d:%02d" % ( tv.start[ 3 ], tv.start[ 4 ] )
                tv.stop  = "% 2d:%02d" % ( tv.stop[ 3 ], tv.stop[ 4 ] )

            
        s = self.screens[ sname ]
        for w in s:
            t, param, val = s[ w ]
            try:
                if val: param = param % eval( val )
            except:
                pass
            k = '%s %s' % ( sname, w )
            try:
                if self.lsv[ k ] == param:
                    continue # nothing changed in this widget
            except KeyError:
                pass

            self.lsv[ k ] = param
            try:
                self.lcd.widget_set( sname, w, param.encode( 'latin1' ) )
            except UnicodeError:
                self.lcd.widget_set( sname, w, param )

        if self.last_screen != sname:
            self.lcd.screen_set( self.last_screen, "-priority 128" )
            self.lcd.screen_set( sname, "-priority 64" )
            self.last_screen = sname

        
    def poll( self ):
        if self.disable: return

        try:
            screens = poll_widgets[ self.lines ][ self.columns ]
        except:
            return

        for s in screens:
            widgets = screens[ s ]
            
            for w in widgets:
                type, param, val = self.screens[ s ][ w ]
                
                if val: param = param % eval( val )
                try:
                    self.lcd.widget_set( s, w, param.encode( 'latin1' ) )
                except UnicodeError:
                    self.lcd.widget_set( s, w, param )
        

    def generate_screens( self ):
        screens = None
        l = self.height
        c = self.width
        # Find a screen
        # find a display with 'l' lines
        while not screens:
            try:                
                screens = layouts[ l ]
            except KeyError:
                if DEBUG > 0:
                    print "WARNING: Could not find screens for %d lines LCD!" % l
                l -= 1
                if l < 1:
                    print "ERROR: No screens found!"
                    self.disable = 1
                    return
        # find a display with 'l' line and 'c' columns
        while not screens:
            try:
                screens = layouts[ l ][ c ]
            except KeyError:
                if DEBUG > 0:
                    print "WARNING: Could not find screens for %d lines and %d columns LCD!" % ( l, c )
                c -= 1
                if c < 1:
                    print "ERROR: No screens found!"
                    self.disable = 1
                    return

        
        self.lines = l
        self.columns = c
        try:
            self.screens = screens = layouts[ l ][ c ]
        except KeyError:
            if DEBUG > 0:
                print "WARNING: Could not find screens for %d lines and %d columns LCD!" % ( self.height, self.width )                
            print "ERROR: No screens found!"
            self.disable = 1
            return
        
        for s in screens:
            self.lcd.screen_add( s )
            widgets = screens[ s ]
            self.lcd.screen_set( s, "-heartbeat off" )

            for w in widgets:
                type, param, val = screens[ s ][ w ]
                self.lcd.widget_add( s, w, type )
        
