# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This file handles the Freevo plugin interface
# Todo:  Maybe split plugin class definitions into an extra file
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.78  2004/11/21 11:12:06  dischi
# some logging updates
#
# Revision 1.77  2004/10/09 16:24:54  dischi
# add function to return number of plugins, activate callback change
#
# Revision 1.76  2004/10/08 20:18:17  dischi
# new eventhandler <-> plugin interface
#
# Revision 1.75  2004/10/06 19:16:29  dischi
# o rename __variable__ to _variable
# o notifier support
# o use 80 chars/line max
#
# Revision 1.74  2004/09/27 18:41:06  dischi
# add input plugin class
#
# Revision 1.73  2004/08/29 18:38:15  dischi
# make cache helper work again
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
import gettext
import copy

import cleanup
from event import Event

import config
import eventhandler
import notifier

import logging
log = logging.getLogger('config')


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
            self._ = gettext.translation(application,
                                         os.environ['FREEVO_LOCALE'],
                                         fallback=1).gettext
        except:
            self._ = lambda m: m


    def shutdown(self):
        """
        Execute on plugin shutdown (== system shutdown)
        """
        pass

    
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
        this function will be called every poll_interval milliseconds
    def eventhandler(self, event, menuw=None):
        events no one else wants will be passed to this functions, when
        you also set the variable event_listener to True, the object will
        get all events. Setting self.events to a list of event names will]
        register only that events to the eventhandler.
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_interval  = 100       # poll every x milliseconds
        self.poll_menu_only = True      # poll only when menu is active
        self.event_listener = False     # process all events
        self.events         = []        # events to register to ([] == all)

    def _poll(self):
        """
        wrapper for the poll function
        """
        if self.poll_menu_only and not eventhandler.is_menu():
            return True
        self.poll()
        return True

        
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


class InputPlugin(Plugin):
    """
    Plugin for input devices such as keyboard and lirc. A plugin of this
    type should be in input/plugins
    """
    def __init__(self):
        Plugin.__init__(self)
        self._eventhandler = eventhandler.get_singleton()
        self.config = config


    def post_key(self, key):
        """
        Send a keyboard event to the event queue
        """
        if not key:
            return None

        for c in (self._eventhandler.context, 'global'):
            try:
                e = self.config.EVENTS[c][key]
                e.context = self._eventhandler.context
                self._eventhandler.queue.append(e)
                break
            except KeyError:
                pass
        else:
            log.warning('no event mapping for key %s in context %s' % \
                        (key, self._eventhandler.context))

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
    global _plugin_number
    global _all_plugins
    global _initialized

    _plugin_number += 1

    for p in _all_plugins:
        if not isinstance(name, Plugin) and p[0] == name and \
               p[1] == type and p[3] == args:
            log.warning('duplicate plugin activation, ignoring:\n' + \
                        '  <%s %s %s>' % (name, type, args))
            return
    if _initialized:
        _load_plugin(name, type, level, args, _plugin_number)
        _sort_plugins()
    else:
        _all_plugins.append((name, type, level, args, _plugin_number))
    return _plugin_number


def remove(id):
    """
    remove a plugin from the list. This can only be done in local_config.py
    and not while Freevo is running
    """
    global _all_plugins
    global _initialized

    if _initialized:
        return

    # remove by plugin id
    if isinstance(id, int):
        for p in _all_plugins:
            if p[4] == id:
                _all_plugins.remove(p)
                return

    # remove by name
    r = [] 
    for p in copy.copy(_all_plugins):
        if p[0] == id:
            _all_plugins.remove(p)


def is_active(name, arg=None):
    """
    search the list if the given plugin is active. If arg is set,
    check arg, too.
    """
    global _all_plugins
    for p in _all_plugins:
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
                

def get_number():
    global _all_plugins
    return len(_all_plugins)


def init(callback = None, reject=['record', 'www'], exclusive=[]):
    """
    load and init all the plugins
    """
    global _all_plugins
    global _initialized
    global _plugin_basedir
    
    _initialized = True
    _plugin_basedir = os.environ['FREEVO_PYTHON']

    current = 0
    for name, type, level, args, number in _all_plugins:
        current += 1
        if callback:
            callback()
        if exclusive:
            # load only plugins from exclusive list
            for e in exclusive:
                if not isinstance(name, str):
                    _load_plugin(name, type, level, args, number)
                    break
                if name.startswith('%s.' % e):
                    _load_plugin(name, type, level, args, number)
                    break
        else:
            # load all plugin except rejected once
            for r in reject:
                if isinstance(name, str) and name.startswith('%s.' % r):
                    break
            else:
                _load_plugin(name, type, level, args, number)


    # sort plugins in extra function (exec doesn't like to be
    # in the same function is 'lambda' 
    _sort_plugins()



def init_special_plugin(id):
    """
    load only the plugin 'id'
    """
    global _all_plugins
    global _initialized
    global _plugin_basedir
    
    _plugin_basedir = os.environ['FREEVO_PYTHON']

    try:
        id = int(id)
    except ValueError:
        pass
    for i in range(len(_all_plugins)):
        name, type, level, args, number = _all_plugins[i]
        if number == id or name == id:
            _load_plugin(name, type, level, args, number)
            del _all_plugins[i]
            break
        
    # sort plugins in extra function (exec doesn't like to be
    # in the same function is 'lambda' 
    _sort_plugins()
    


def get(type):
    """
    get the plugin list 'type'
    """
    global _plugin_type_list

    if not _plugin_type_list.has_key(type):
        _plugin_type_list[type] = []

    return _plugin_type_list[type]


def getall():
    """
    return a list of all plugins
    """
    global _all_plugins
    ret = []
    for t in _all_plugins:
        ret.append(t[0])
    return ret


def mimetype(display_type):
    """
    return all MimetypePlugins for the given display_type. If display_type is
    None, return all MimetypePlugins.
    """
    if not display_type:
        return _plugin_type_list['mimetype']
    ret = []
    for p in _plugin_type_list['mimetype']:
        if not p.display_type or display_type in p.display_type:
            ret.append(p)
    return ret

        
def getbyname(name, multiple_choises=0):
    """
    get a plugin by it's name
    """
    global _named_plugins
    if _named_plugins.has_key(name):
        return _named_plugins[name]
    if multiple_choises:
        return []
    return None


def register(plugin, name, multiple_choises=0):
    """
    register an object as a named plugin
    """
    global _named_plugins
    if multiple_choises:
        if not _named_plugins.has_key(name):
            _named_plugins[name] = []
        _named_plugins[name].append(plugin)
    else:
        _named_plugins[name] = plugin


def register_callback(name, *args):
    """
    register a callback to the callback handler 'name'. The format of
    *args depends on the callback
    """
    global _callbacks
    if not _callbacks.has_key(name):
        _callbacks[name] = []
    _callbacks[name].append(args)


def get_callbacks(name):
    """
    return all callbacks registered with 'name'
    """
    global _callbacks
    if not _callbacks.has_key(name):
        _callbacks[name] = []
    return _callbacks[name]

    
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

_initialized        = False
_all_plugins        = []
_plugin_number      = 0
_plugin_type_list   = {}
_named_plugins      = {}
_callbacks          = {}
_plugin_basedir     = ''


def _add_to_ptl(type, object):
    """
    small helper function to add a plugin to the PluginTypeList
    """
    global _plugin_type_list
    if not _plugin_type_list.has_key(type):
        _plugin_type_list[type] = []
    _plugin_type_list[type].append(object)
    


def _find_plugin_file(filename):
    global _plugin_basedir
    full_filename = os.path.join(_plugin_basedir, filename)

    if os.path.isfile(full_filename + '.py'):
        return filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return filename.replace('/', '.'), None

    full_filename = os.path.join(_plugin_basedir, 'plugins', filename)

    if os.path.isfile(full_filename + '.py'):
        return 'plugins.' + filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return 'plugins.' + filename.replace('/', '.'), None

    if filename.find('/') > 0:
        special = filename[:filename.find('/')]
        filename = os.path.join(special, 'plugins',
                                filename[filename.find('/')+1:])
        full_filename = os.path.join(_plugin_basedir, filename)

        if os.path.isfile(full_filename + '.py'):
            return filename.replace('/', '.'), special

        if os.path.isdir(full_filename):
            return filename.replace('/', '.'), special

    return None, None

        

def _load_plugin(name, type, level, args, number):
    """
    load the plugin and add it to the lists
    """
    
    
    global _plugin_type_list
    global _named_plugins
    global _plugin_basedir

    # fallback
    module  = name
    object  = '%s.PluginInterface' % module
    special = None

    # locate the plugin:
    files = []

    if not isinstance(name, Plugin):
        module, special = _find_plugin_file(name.replace('.', '/'))
        if module:
            object = module + '.PluginInterface'
        elif name.find('.') > 0:
            pname = name[:name.rfind('.')].replace('.', '/')
            module, special = _find_plugin_file(pname)
            if module:
                object = module + '.%s' % name[name.rfind('.')+1:]
            else:
                log.critical('can\'t locate plugin %s' % name)
                return
        else:
            log.critical('can\'t locate plugin %s' % name)
            return
        
    try:
        if not isinstance(name, Plugin):
            log.debug('loading %s as plugin %s' % (module, object))

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
                    reason = 'unknown\nThe plugin neither called __init__ '\
                             'nor set a reason why\nPlease contact the plugin'\
                             'author or the freevo list'
                log.warning('plugin %s deactivated\n  reason: %s' % (name, reason))
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
            _add_to_ptl(p._type, p)

        else: 
            if isinstance(p, DaemonPlugin):
                if hasattr(p, 'poll'):
                    notifier.addTimer( p.poll_interval,
                                       notifier.Callback( p._poll ) )
                if hasattr(p, 'eventhandler'):
                    if p.events:
                        for e in p.events:
                            eventhandler.register(p, e)
                    else:
                        if p.event_listener:
                            eventhandler.register(p, eventhandler.GENERIC_HANDLER)
                        else:
                            eventhandler.register(p, eventhandler.EVENT_LISTENER)

            if isinstance(p, MainMenuPlugin):
                _add_to_ptl('mainmenu%s' % special, p)
                if hasattr(p, 'eventhandler'):
                    eventhandler.register(p, eventhandler.GENERIC_HANDLER)

            if isinstance(p, ItemPlugin):
                _add_to_ptl('item%s' % special, p)

            if isinstance(p, MimetypePlugin):
                _add_to_ptl('mimetype', p)

        # register shutdown handler
        cleanup.register( p.shutdown )
                
        if p.plugin_name:
            _named_plugins[p.plugin_name] = p


    except:
        log.exception('failed to load plugin %s' % name)


def _sort_plugins():
    """
    sort all plugin lists based on the level
    """
    global _plugin_type_list
    for key in _plugin_type_list:
        _plugin_type_list[key].sort(lambda l, o: cmp(l._level, o._level))

