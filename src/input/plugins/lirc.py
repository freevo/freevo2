# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# lirc.py - A lirc input plugin for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/09/25 04:39:07  rshortt
# An input plugin for lirc: plugin.activate('input.lirc') - untested.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import config
import eventhandler
import rc
rc = rc.get_singleton()

try:
    import pylirc
except ImportError:
    print 'WARNING: PyLirc not found, lirc remote control disabled!'
    raise Exception



class PluginInterface(plugin.Plugin):

    def __init__(self):
        plugin.Plugin.__init__(self)
        self.plugin_name = 'LIRC'

        try:
            if os.path.isfile(config.LIRCRC):
                pylirc.init('freevo', config.LIRCRC)
                pylirc.blocking(0)
            else:
                raise IOError
        except RuntimeError:
            print 'WARNING: Could not initialize PyLirc!'
            raise Exception
        except IOError:
            print 'WARNING: %s not found!' % config.LIRCRC
            raise Exception

        self.nextcode = pylirc.nextcode
        self.previous_returned_code   = None
        self.previous_code            = None;
        self.repeat_count             = 0
        self.firstkeystroke           = 0.0
        self.lastkeystroke            = 0.0
        self.lastkeycode              = ''
        self.default_keystroke_delay1 = config.LIRC_DELAY1
        self.default_keystroke_delay2 = config.LIRC_DELAY2

        rc.inputs.append(self)


    def config(self):
        return [('LIRCRC', '/etc/freevo/lircrc', 
                           'Location of Freevo lircrc file.'),
                ('LIRC_DELAY1', 0.25, 'Repeat delay 1.'),
                ('LIRC_DELAY2', 0.25, 'Repeat delay 2.'),
               ]


    def get_last_code(self):
        """
        read the lirc interface
        """
        result = None

        if self.previous_code != None:
            # Let's empty the buffer and return the most recent code
            while 1:
                list = self.nextcode();
                if list != []:
                    break
        else:
            list = self.nextcode()

        if list == []:
            # It's a repeat, the flag is 0
            list   = self.previous_returned_code
            result = list

        elif list != None:
            # It's a new code (i.e. IR key was released), the flag is 1
            self.previous_returned_code = list
            result = list

        self.previous_code = result
        return result
        

    def poll(self):
        """
        return next event
        """
        list = self.get_last_code()
        
        if list == None:
            nowtime = 0.0
            nowtime = time.time()
            if (self.lastkeystroke + self.default_keystroke_delay2 < nowtime) and \
                   (self.firstkeystroke != 0.0):
                self.firstkeystroke = 0.0
                self.lastkeystroke = 0.0
                self.repeat_count = 0
            
        if list != None:
            nowtime = time.time()
            
            if list: 
                for code in list:
                    if ( self.lastkeycode != code ):
                        self.lastkeycode = code
                        self.lastkeystroke = nowtime
                        self.firstkeystroke = nowtime

            if self.firstkeystroke == 0.0 :
                self.firstkeystroke = time.time()
            else:
                if (self.firstkeystroke + self.default_keystroke_delay1 > nowtime):
                    list = []
                else:
                    if (self.lastkeystroke + self.default_keystroke_delay2 < nowtime):
                        self.firstkeystroke = nowtime

            self.lastkeystroke = nowtime
            self.repeat_count += 1

            for code in list:
                eventhandler.post_key(code)


