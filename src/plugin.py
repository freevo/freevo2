#if 0 /*
# -----------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This file handles the Freevo plugin interface
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2003/07/09 19:12:57  dischi
# A plugin can now inherit from more than one basic plugin type. Basic
# types are the types known to this file: MainMenuPlugin, ItemPlugin and
# DaemonPlugin. This doesn't work for special plugins like IdleBarPlugins
#
# Second a plugin can be activated during runtime (e.g. by another plugin).
# It's not possible to remove a plugin during runtime, this only works on
# startup.
#
# Revision 1.21  2003/05/30 00:53:19  rshortt
# Various event bugfixes.
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
import traceback
from event import Event

TRUE  = 1
FALSE = 0

#
# Some basic plugins known to Freevo.
#

class Plugin:
    """
    Basic plugin class. All plugins should inherit from this
    class
    """
    def __init__(self):
        self._type   = None
        self._level  = 0
        self._number = 0
        self.plugin_name   = ''

        
class MainMenuPlugin(Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def __init__(self):
        Plugin.__init__(self)


    def items(self, parent):
        """
        return the list of items for the main menu
        """
        return []


class ItemPlugin(Plugin):
    """
    Plugin class to add something to the item action list
    """
    def __init__(self):
        Plugin.__init__(self)


    def actions(self, item):
        """
        return a list of actions to that item. Each actions is a tuple
        (function, 'name-in-the-menu')
        """
        return []

    
class DaemonPlugin(Plugin):
    """
    Plugin class for daemon objects who will be activae in the
    background while Freevo is running

    A DaemonPlugin can have the following functions:
    def poll(self):
        this function will be called every poll_intervall*0.1 seconds
    def draw(self):
        this function will be caleed to update the screen
    def eventhandler(self, event):
        events no one else wants will be passed to this functions
    def shutdown(self):
        this function may be called to shutdown the plugin and will
        be called on freevo shutdown
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_counter   = 0         # poll counter, don't change this
        self.poll_interval  = 1         # poll every x*0.1 seconds
        self.poll_menu_only = TRUE      # poll only when menu is active


#
# Some plugin names to avoid typos
#

AUDIO_PLAYER = 'AUDIO_PLAYER'
VIDEO_PLAYER = 'VIDEO_PLAYER'
DVD_PLAYER   = 'DVD_PLAYER'
TV           = 'TV'



#
# Plugin functions
#


def activate(name, type=None, level=0, args=None):
    """
    activate a plugin
    """
    global __plugin_number__
    global __all_plugins__
    global __initialized__

    __plugin_number__ += 1

    if __initialized__:
        __load_plugin__(name, type, level, args, __plugin_number__)
        __sort_plugins__()
    else:
        __all_plugins__.append((name, type, level, args, __plugin_number__))
    return __plugin_number__


def remove(id):
    """
    remove a plugin from the list. This can only be done in local_config.py
    and not while Freevo is running
    """
    global __all_plugins__
    global __initialized__

    if __initialized__:
        return

    # remove by plugin id
    if isinstance(id, int):
        for p in __all_plugins__:
            if p[4] == id:
                __all_plugins__.remove(p)
                return

    # remove by name
    r = [] 
    for p in __all_plugins__:
        if p[0] == id:
            r.append(p)

    for p in r:
        __all_plugins__.remove(p)



    
def init():
    """
    load and init all the plugins
    """
    global __all_plugins__
    global __initialized__
    
    __initialized__ = TRUE

    for name, type, level, args, number in __all_plugins__:
        __load_plugin__(name, type, level, args, number)

    # sort plugins in extra function (exec doesn't like to be
    # in the same function is 'lambda' 
    __sort_plugins__()


def shutdown(plugin_name=None):
    """
    called to shutdown one or all daemon plugins
    """
    shutdown_plugins = get('daemon_shutdown')
    for p in shutdown_plugins:
        if not plugin_name or p.plugin_name == plugin_name:
            p.shutdown()

            
def get(type):
    """
    get the plugin list 'type'
    """
    global __plugin_type_list__

    if not __plugin_type_list__.has_key(type):
        __plugin_type_list__[type] = []

    return __plugin_type_list__[type]


def getbyname(name):
    """
    get a plugin by it's name
    """
    global __named_plugins__
    if __named_plugins__.has_key(name):
        return __named_plugins__[name]
    return None


def register(plugin, name):
    """
    register an object as a named plugin
    """
    global __named_plugins__
    __named_plugins__[name] = plugin

    
def event(name):
    """
    create plugin event
    """
    return Event('PLUGIN_EVENT %s' % name)


def isevent(event):
    """
    plugin event parsing
    """
    event = str(event)
    if event[:12] == 'PLUGIN_EVENT':
        return event[13:]
    else:
        return None





#
# internal stuff
#

__initialized__        = FALSE
__all_plugins__        = []
__plugin_number__      = 0
__plugin_type_list__   = {}
__named_plugins__      = {}


def __add_to_ptl__(type, object):
    """
    small helper function to add a plugin to the PluginTypeList
    """
    global __plugin_type_list__
    if not __plugin_type_list__.has_key(type):
        __plugin_type_list__[type] = []
    __plugin_type_list__[type].append(object)
    


def __load_plugin__(name, type, level, args, number):
    """
    load the plugin and add it to the lists
    """
    global __plugin_type_list__
    global __named_plugins__

    module = name[:name.rfind('.')]

    # locate the plugin
    if os.path.isfile('src/plugins/%s.py' % module):
        module  = 'plugins.%s' % module
        object  = 'plugins.%s' % name
        special = None
    elif os.path.isfile('src/plugins/%s.py' % name):
        module  = 'plugins.%s' % name
        object  = 'plugins.%s.PluginInterface' % name
        special = None
    elif os.path.isfile('src/%s/plugins/%s.py' % (module, name[name.rfind('.')+1:])):
        special = module
        module  = '%s.plugins.%s' % (module, name[name.rfind('.')+1:])
        object  = '%s.PluginInterface' % module
    elif os.path.isdir('src/%s' % name):
        module  = name
        object  = '%s.PluginInterface' % module
        special = None
    else:
        module  = name
        object  = '%s.PluginInterface' % module
        special = None

    try:
        exec('import %s' % module)
        if args:
            p = eval('%s%s' % (object, str(args)))
        else:
            p = eval('%s()' % object)

        p._number = number

        if type:
            special = type

        if special:
            special = '_%s' % special
        else:
            special = ''

        # special plugin type (e.g. idlebar)
        if p._type:
            __add_to_ptl__(p._type, p)

        else: 
            if isinstance(p, DaemonPlugin):
                __add_to_ptl__('daemon', p)
                for type in ('poll', 'draw', 'eventhandler', 'shutdown' ):
                    if hasattr(p, type):
                        __add_to_ptl__('daemon_%s' % type, p)

            if isinstance(p, MainMenuPlugin):
                __add_to_ptl__('mainmenu%s' % special, p)
                if hasattr(p, 'eventhandler'):
                    __add_to_ptl__('daemon_eventhandler', p)

            if isinstance(p, ItemPlugin):
                __add_to_ptl__('item%s' % special, p)
                if not special:
                    for mtype in ( '_video', '_audio', '_image', '_games' ):
                        __add_to_ptl__('item%s' % mtype, p)

        if p.plugin_name:
            __named_plugins__[p.plugin_name] = p


    except:
        print 'failed to load plugin %s' % name
        traceback.print_exc()


def __sort_plugins__():
    """
    sort all plugin lists based on the level
    """
    global __plugin_type_list__
    for key in __plugin_type_list__:
        __plugin_type_list__[key].sort(lambda l, o: cmp(l._level, o._level))




#
# Main function
#
if __name__ == "__main__":
    import util
    import re
    import os
    
    start = re.compile('^class *(.*)\((.*Plugin).:')
    stop  = re.compile('^[\t ]*def.*:')
    comment = re.compile('^[\t ]*"""')

    print_line = 0
    ptypes = {}

    print '------------------------------------------'
    print 'LIST OF PLUGINS'
    print
    print
    
    for file in util.recursefolders('src',1, '*.py',1):
        if file == 'src/plugin.py':
            continue
        for line in util.readfile(file):
            if (comment.match(line) and print_line == 2) or \
               (stop.match(line) and print_line == 1):
                print_line = 0
                print
                
            if print_line == 2:
                print line[1:-1]

            if comment.match(line) and print_line == 1:
                print_line = 2
                
            if start.match(line):
                file = re.sub('/', '.', os.path.splitext(file)[0])
                file = re.sub('src.', '', file)
                file = re.sub('plugins.', '', file)
                file = re.sub('.__init__', '', file)

                type = start.match(line).group(2)
                if re.match('^plugin.(.*)', type):
                    type = re.match('^plugin.(.*)', type).group(1)
                if start.match(line).group(1) == 'PluginInterface':
                    name = file
                else:
                    name = '%s.%s' % ( file, start.match(line).group(1))
                
                print '%s (%s)' % (name, type)
                print_line = 1
        
