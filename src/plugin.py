#if 0 /*
# -----------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/04/18 10:22:07  dischi
# You can now remove plugins from the list and plugins know the list
# they belong to (can be overwritten). level and args are optional.
#
# Revision 1.3  2003/04/17 21:21:57  dischi
# Moved the idle bar to plugins and changed the plugin interface
#
# Revision 1.2  2003/04/16 08:47:00  dischi
# bugfix for bad plugins
#
# Revision 1.1  2003/04/15 20:01:34  dischi
# first version of a plugin interface
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

TRUE  = 1
FALSE = 0

class Plugin:
    """
    Basic plugin class. All plugins should inherit from this
    class
    """
    def __init__(self):
        self._type   = None
        self._level  = 0
        self._number = 0

class MainMenuPlugin(Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def __init__(self):
        Plugin.__init__(self)
        self._type = 'mainmenu'

    def items(self, parent):
        """
        return the list of items for the main menu
        """
        return []


class DaemonPlugin(Plugin):
    """
    Plugin class for daemon objects who will be activae in the
    background while Freevo is running
    """
    def __init__(self):
        Plugin.__init__(self)
        self._type   = 'daemon'

    def poll(self):
        """
        This function will be called every 0.1 seconds
        """
        pass

    def refresh(self):
        """
        This function will be called after a screen redraw from skin
        """
        pass
    




initialized = FALSE

#
# the plugin list
#
all_plugins = []
plugin_number = 0

#
# the plugin dictionary
#
ptl = {}
        
#
# activate a plugin
#
def activate(name, type=None, level=0, args=None):
    global plugin_number
    global all_plugins
    global initialized

    if initialized:
        return 0
    
    plugin_number += 1
    all_plugins.append((name, type, level, args, plugin_number))
    return plugin_number


#
# remove a plugin from the list
#
def remove(number):
    global all_plugins
    global initialized

    if initialized:
        return

    for p in all_plugins:
        if p[4] == number:
            all_plugins.remove(p)
            return
        
#
# load and init all the plugins
#
def init():
    global ptl
    global all_plugins
    global initialized

    initialized = TRUE

    for name, type, level, args, number in all_plugins:
        module = name[:name.rfind('.')]
            
        if os.path.isfile('src/plugins/%s.py' % module):
            module = 'plugins.%s' % module
            object = 'plugins.%s' % name
        else:
            module = name
            object = '%s.PluginInterface' % module

        try:
            exec('import %s' % module)
            if args:
                p = eval('%s%s' % (object, str(args)))
            else:
                p = eval('%s()' % object)

            p._number = number
            if type:
                p._type  = type
            if level:
                p._level = level

            if not ptl.has_key(p._type):
                ptl[p._type] = []
            type = ptl[p._type]
            
            for i in range(len(type)):
                if type[i]._level > p._level:
                    type.insert(i, p)
                    break
            else:
                type.append(p)

        except ImportError:
            print 'failed to import plugin %s' % name
            
        except AttributeError:
            print 'failed to load plugin %s' % name

        except TypeError:
            print 'wrong number of parameter for %s' % name


#                
# get the plugin list 'type'
#
def get(type):
    global ptl

    if not ptl.has_key(type):
        ptl[type] = []

    return ptl[type]
