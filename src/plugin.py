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
# Revision 1.41  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.40  2003/09/10 19:29:29  dischi
# if plugins do not call __init__ they want to be disabled
#
# Revision 1.39  2003/09/10 18:13:48  dischi
# support for plugins to add defaults to config
#
# Revision 1.38  2003/09/09 18:36:11  dischi
# add a plugin helper to get more informations about the plugins
#
# Revision 1.37  2003/09/05 16:29:28  dischi
# make special function to init only one specific plugin
#
# Revision 1.36  2003/09/03 20:10:13  dischi
# Make sure a plugin is only loaded once with the same args and type
#
# Revision 1.35  2003/09/01 18:45:28  dischi
# update doc
#
# Revision 1.34  2003/08/31 17:15:00  dischi
# default level is 10 now to make it possible to set items before default ones
#
# Revision 1.33  2003/08/31 14:18:31  dischi
# added support for a progress callback (0-100)
#
# Revision 1.32  2003/08/30 17:03:02  dischi
# support for eventhandler in ItemPlugins
#
# Revision 1.31  2003/08/30 07:58:57  dischi
# Fix item plugin handling
#
# Revision 1.30  2003/08/27 15:25:47  mikeruelle
# Start of Radio Support
#
# Revision 1.29  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
# Revision 1.28  2003/08/22 17:51:29  dischi
# Some changes to make freevo work when installed into the system
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

DEBUG = 0


#
# Some basic plugins known to Freevo.
#

class Plugin:
    """
    Basic plugin class. All plugins should inherit from this
    class
    """
    def __init__(self):
        import config
        self._type   = None
        self._level  = 10
        self._number = 0
        self.plugin_name   = ''
        for var, val, desc in self.config():
            if not hasattr(config, var):
                setattr(config, var, val)
            
    def config(self):
        return []
        
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

    The plugin can also have an eventhandler. All events passed to the item
    will also be passed to this plugin. This works only for VideoItems right
    now (each item type must support it directly). If the function returns
    TRUE, the event won't be passed to other eventhandlers and also not to
    the item itself.
    
    def eventhandler(self, item, event, menuw=None):
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
    def draw(self(type, object), osd):
        this function will be called to update the screen
    def eventhandler(self, event, menuw=None):
        events no one else wants will be passed to this functions, when
        you also set the variable event_listener to TRUE, the object will
        get all events
    def shutdown(self):
        this function may be called to shutdown the plugin and will
        be called on freevo shutdown
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_counter   = 0         # poll counter, don't change this
        self.poll_interval  = 1         # poll every x*0.1 seconds
        self.poll_menu_only = TRUE      # poll only when menu is active
        self.event_listener = FALSE     # process all events

#
# Some plugin names to avoid typos
#

AUDIO_PLAYER = 'AUDIO_PLAYER'
VIDEO_PLAYER = 'VIDEO_PLAYER'
DVD_PLAYER   = 'DVD_PLAYER'
VCD_PLAYER   = 'VCD_PLAYER'
TV           = 'TV'
RADIO_PLAYER   = 'RADIO_PLAYER'



#
# Plugin functions
#


def activate(name, type=None, level=10, args=None):
    """
    activate a plugin
    """
    global __plugin_number__
    global __all_plugins__
    global __initialized__

    __plugin_number__ += 1

    for p in __all_plugins__:
        if p[0] == name and p[1] == type and p[3] == args:
            print 'WARNING: duplicate plugin activation, ignoring:'
            print '<%s %s %s>' % (name, type, args)
            print
            return
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



    
def init(callback = None):
    """
    load and init all the plugins
    """
    global __all_plugins__
    global __initialized__
    global __plugin_basedir__
    
    __initialized__ = TRUE
    __plugin_basedir__ = os.environ['FREEVO_PYTHON']

    current = 0
    for name, type, level, args, number in __all_plugins__:
        current += 1
        if callback:
            callback(int((float(current) / len(__all_plugins__)) * 100))
        __load_plugin__(name, type, level, args, number)

    # sort plugins in extra function (exec doesn't like to be
    # in the same function is 'lambda' 
    __sort_plugins__()



def init_special_plugin(id):
    """
    load only the plugin 'id'
    """
    global __all_plugins__
    global __initialized__
    global __plugin_basedir__
    
    __plugin_basedir__ = os.environ['FREEVO_PYTHON']

    for i in range(len(__all_plugins__)):
        name, type, level, args, number = __all_plugins__[i]
        if number == int(id):
            del __all_plugins__[i]
            __load_plugin__(name, type, level, args, number)
            break
        
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

__plugin_basedir__     = ''

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
    global __plugin_basedir__

    module = name[:name.rfind('.')]

    # locate the plugin
    if os.path.isfile(os.path.join(__plugin_basedir__, 'plugins/%s.py' % module)):
        module  = 'plugins.%s' % module
        object  = 'plugins.%s' % name
        special = None
    elif os.path.isfile(os.path.join(__plugin_basedir__, 'plugins/%s.py' % name)):
        module  = 'plugins.%s' % name
        object  = 'plugins.%s.PluginInterface' % name
        special = None
    elif os.path.isfile(os.path.join(__plugin_basedir__, '%s/plugins/%s.py' % \
                                     (module, name[name.rfind('.')+1:]))):
        special = module
        module  = '%s.plugins.%s' % (module, name[name.rfind('.')+1:])
        object  = '%s.PluginInterface' % module
    elif os.path.isdir(os.path.join(__plugin_basedir__, '%s' % name)):
        module  = name
        object  = '%s.PluginInterface' % module
        special = None
    else:
        module  = name
        object  = '%s.PluginInterface' % module
        special = None

    try:
        if DEBUG:
            print 'loading %s as plugin %s' % (module, name)
            
        exec('import %s' % module)
        if args:
            p = eval('%s%s' % (object, str(args)))
        else:
            p = eval('%s()' % object)

        if not hasattr(p, '_type'):
            if hasattr(p, 'reason'):
                reason = p.reason
            else:
                reason = 'unknown\nThe plugin neither called __init__ nor set a'\
                         'reason why\nPlease contact the plugin author or the freevo list'
            print 'plugin %s deactivated, reason: %s' % (name, reason)
            return
        
        p._number = number
        p._level = level

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

