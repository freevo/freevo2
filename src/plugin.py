# -*- coding: iso-8859-1 -*-
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
# Revision 1.71  2004/08/01 10:55:27  dischi
# cosmetic change for debug
#
# Revision 1.70  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.69  2004/07/25 19:47:38  dischi
# use application and not rc.app
#
# Revision 1.68  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.67  2004/06/24 14:56:19  dischi
# make it possible to put a subplugin into main
#
# Revision 1.66  2004/06/07 16:10:45  rshortt
# Change 'RECORD' to plugin.RECORD.
#
# Revision 1.65  2004/05/31 10:40:57  dischi
# update to new callback handling in rc
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


import os, sys
import traceback
import gettext
import copy

from event import Event

import eventhandler
import rc

DEBUG = 0

if float(sys.version[0:3]) < 2.3:
    True  = 1
    False = 0

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
        """
        return a list of config variables this plugin needs to be set in
        in freevo_config.py. Each variable in again a list and contains
        (varname, default value, description)
        """
        return []

    def translation(self, application):
        """
        Loads the gettext translation for this plugin (only this class).
        This can be used in plugins who are not inside the Freevo distribution.
        After loading the translation, gettext can be used by self._() instead
        of the global _().
        """
        try:
            self._ = gettext.translation(application, os.environ['FREEVO_LOCALE'],
                                         fallback=1).gettext
        except:
            self._ = lambda m: m

        
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
    True, the event won't be passed to other eventhandlers and also not to
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
    Plugin class for daemon objects who will be activate in the
    background while Freevo is running

    A DaemonPlugin can have the following functions:
    def poll(self):
        this function will be called every poll_intervall*0.1 seconds
    def draw(self(type, object), osd):
        this function will be called to update the screen
    def eventhandler(self, event, menuw=None):
        events no one else wants will be passed to this functions, when
        you also set the variable event_listener to True, the object will
        get all events
    def shutdown(self):
        this function may be called to shutdown the plugin and will
        be called on freevo shutdown
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_counter   = 0         # poll counter, don't change this
        self.poll_interval  = 1         # poll every x*0.1 seconds
        self.poll_menu_only = True      # poll only when menu is active
        self.event_listener = False     # process all events


    def poll_wrapper(self):
        if self.poll_menu_only and not eventhandler.is_menu():
            return
        self.real_poll()

        
class MimetypePlugin(Plugin):
    """
    Plugin class for mimetypes handled in a directory/playlist.
    self.display_type is a list of display types where this mimetype
    should be displayed, [] for always.
    """
    def __init__(self):
        import util
        Plugin.__init__(self)
        self.display_type = []
        self.find_matches = util.find_matches

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return []

    
    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        return []


    def count(self, parent, files):
        """
        return how many items will be build on files
        """
        return len(self.find_matches(files, self.suffix()))
            

    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        pass


    def dirconfig(self, diritem):
        """
        adds configure variables to the directory
        """
        return []

    
#
# Some plugin names to avoid typos
#

AUDIO_PLAYER   = 'AUDIO_PLAYER'
RADIO_PLAYER   = 'RADIO_PLAYER'
VIDEO_PLAYER   = 'VIDEO_PLAYER'
TV             = 'TV'
RECORD         = 'RECORD'


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
        if not isinstance(name, Plugin) and p[0] == name and p[1] == type and p[3] == args:
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
    for p in copy.copy(__all_plugins__):
        if p[0] == id:
            __all_plugins__.remove(p)


def is_active(name, arg=None):
    """
    search the list if the given plugin is active. If arg is set,
    check arg, too.
    """
    global __all_plugins__
    for p in __all_plugins__:
        if p[0] == name:
            if not arg:
                return p
            if isinstance(arg, list) or isinstance(arg, tuple):
                try:
                    for i in range(len(arg)):
                        if arg[i] != p[3][i]:
                            break
                    else:
                        return p
                except:
                    pass
            if arg == p[3]:
                return p
    return False
                
    
def init(callback = None):
    """
    load and init all the plugins
    """
    global __all_plugins__
    global __initialized__
    global __plugin_basedir__
    
    __initialized__ = True
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

    try:
        id = int(id)
    except ValueError:
        pass
    for i in range(len(__all_plugins__)):
        name, type, level, args, number = __all_plugins__[i]
        if number == id or name == id:
            __load_plugin__(name, type, level, args, number)
            del __all_plugins__[i]
            break
        
    # sort plugins in extra function (exec doesn't like to be
    # in the same function is 'lambda' 
    __sort_plugins__()
    

def shutdown(plugin_name=None):
    """
    called to shutdown one or all daemon plugins
    """
    for key in __plugin_type_list__:
        for p in __plugin_type_list__[key]:
            if (not plugin_name or p.plugin_name == plugin_name) and hasattr(p, 'shutdown'):
                _debug_('shutdown plugin %s' % p.plugin_name, 2)
                p.shutdown()

 
def get(type):
    """
    get the plugin list 'type'
    """
    global __plugin_type_list__

    if not __plugin_type_list__.has_key(type):
        __plugin_type_list__[type] = []

    return __plugin_type_list__[type]


def mimetype(display_type):
    """
    return all MimetypePlugins for the given display_type. If display_type is
    None, return all MimetypePlugins.
    """
    if not display_type:
        return __plugin_type_list__['mimetype']
    ret = []
    for p in __plugin_type_list__['mimetype']:
        if not p.display_type or display_type in p.display_type:
            ret.append(p)
    return ret

        
def getall():
    """
    return a list of all plugins
    """
    global __all_plugins__
    ret = []
    for t in __all_plugins__:
        ret.append(t[0])
    return ret


def getbyname(name, multiple_choises=0):
    """
    get a plugin by it's name
    """
    global __named_plugins__
    if __named_plugins__.has_key(name):
        return __named_plugins__[name]
    if multiple_choises:
        return []
    return None


def register(plugin, name, multiple_choises=0):
    """
    register an object as a named plugin
    """
    global __named_plugins__
    if multiple_choises:
        if not __named_plugins__.has_key(name):
            __named_plugins__[name] = []
        __named_plugins__[name].append(plugin)
    else:
        __named_plugins__[name] = plugin


def register_callback(name, *args):
    """
    register a callback to the callback handler 'name'. The format of
    *args depends on the callback
    """
    global __callbacks__
    if not __callbacks__.has_key(name):
        __callbacks__[name] = []
    __callbacks__[name].append(args)


def get_callbacks(name):
    """
    return all callbacks registered with 'name'
    """
    global __callbacks__
    if not __callbacks__.has_key(name):
        __callbacks__[name] = []
    return __callbacks__[name]

    
def event(name, arg=None):
    """
    create plugin event
    """
    return Event('PLUGIN_EVENT %s' % name, arg=arg)


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

__initialized__        = False
__all_plugins__        = []
__plugin_number__      = 0
__plugin_type_list__   = {}
__named_plugins__      = {}
__callbacks__          = {}
__plugin_basedir__     = ''


def __add_to_ptl__(type, object):
    """
    small helper function to add a plugin to the PluginTypeList
    """
    global __plugin_type_list__
    if not __plugin_type_list__.has_key(type):
        __plugin_type_list__[type] = []
    __plugin_type_list__[type].append(object)
    


def __find_plugin_file__(filename):
    global __plugin_basedir__
    full_filename = os.path.join(__plugin_basedir__, filename)

    if os.path.isfile(full_filename + '.py'):
        return filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return filename.replace('/', '.'), None

    full_filename = os.path.join(__plugin_basedir__, 'plugins', filename)

    if os.path.isfile(full_filename + '.py'):
        return 'plugins.' + filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return 'plugins.' + filename.replace('/', '.'), None

    if filename.find('/') > 0:
        special = filename[:filename.find('/')]
        filename = os.path.join(special, 'plugins', filename[filename.find('/')+1:])
        full_filename = os.path.join(__plugin_basedir__, filename)

        if os.path.isfile(full_filename + '.py'):
            return filename.replace('/', '.'), special

        if os.path.isdir(full_filename):
            return filename.replace('/', '.'), special

    return None, None

        

def __load_plugin__(name, type, level, args, number):
    """
    load the plugin and add it to the lists
    """
    
    
    global __plugin_type_list__
    global __named_plugins__
    global __plugin_basedir__

    # fallback
    module  = name
    object  = '%s.PluginInterface' % module
    special = None

    # locate the plugin:
    files = []

    if not isinstance(name, Plugin):
        module, special = __find_plugin_file__(name.replace('.', '/'))
        if module:
            object = module + '.PluginInterface'
        elif name.find('.') > 0:
            module, special = __find_plugin_file__(name[:name.rfind('.')].replace('.', '/'))
            if module:
                object = module + '.%s' % name[name.rfind('.')+1:]
            else:
                print 'can\'t locate plugin %s' % name
                print 'start \'freevo plugins -l\' to get a list of plugins'
                return
        else:
            print 'can\'t locate plugin %s' % name
            print 'start \'freevo plugins -l\' to get a list of plugins'
            return
        
    try:
        if not isinstance(name, Plugin):
            if DEBUG:
                print 'loading %s as plugin %s' % (module, object)

            exec('import %s' % module)
            if not args:
                p = eval(object)()
            elif isinstance(args, list) or isinstance(args, tuple):
                paramlist = 'args[0]'
                for i in range(1, len(args)):
                    paramlist += ',args[%s]' % i
                p = eval('%s(%s)' % (object, paramlist))
            else:
                p = eval(object)(args)

            if not hasattr(p, '_type'):
                if hasattr(p, 'reason'):
                    reason = p.reason
                else:
                    reason = 'unknown\nThe plugin neither called __init__ nor set a '\
                             'reason why\nPlease contact the plugin author or the freevo list'
                print 'plugin %s deactivated\nreason: %s' % (name, reason)
                return
        else:
            p = name
            
        p._number = number
        p._level = level

        if type:
            special = type

        if special == 'main':
            special = ''
        elif special:
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
                if hasattr(p, 'poll'):
                    if p.poll_menu_only:
                        # replace poll with the poll wrapper to handle
                        # poll_menu_only
                        p.real_poll = p.poll
                        p.poll      = p.poll_wrapper
                    rc.register(p.poll, True, p.poll_interval)

            if isinstance(p, MainMenuPlugin):
                __add_to_ptl__('mainmenu%s' % special, p)
                if hasattr(p, 'eventhandler'):
                    __add_to_ptl__('daemon_eventhandler', p)

            if isinstance(p, ItemPlugin):
                __add_to_ptl__('item%s' % special, p)

            if isinstance(p, MimetypePlugin):
                __add_to_ptl__('mimetype', p)

            if hasattr(p, 'shutdown'):
                # register shutdown handler
                rc.register(p.shutdown, True, rc.SHUTDOWN)
                
        if p.plugin_name:
            __named_plugins__[p.plugin_name] = p


    except:
        print 'failed to load plugin %s' % name
        print 'start \'freevo plugins -l\' to get a list of plugins'
        traceback.print_exc()


def __sort_plugins__():
    """
    sort all plugin lists based on the level
    """
    global __plugin_type_list__
    for key in __plugin_type_list__:
        __plugin_type_list__[key].sort(lambda l, o: cmp(l._level, o._level))

