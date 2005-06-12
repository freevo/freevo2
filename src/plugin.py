# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------------
# $Id$
#
# This file is the basic plugin interface for Freevo. It defines simple plugin
# base classes functions to add or remove a plugin. On init it will load all
# plugins for the given application.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import os
import copy
import logging

import notifier

# freevo imports
import cleanup
from event import Event
import eventhandler

# get logging object
log = logging.getLogger('config')

# status of the plugin module
initialized = False

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

        # FIXME: bad coding style
        import config
        
        for var, val, desc in self.config():
            log.debug('FIXME: %s' % var)
            if not hasattr(config, var):
                setattr(config, var, val)


    def config(self):
        """
        return a list of config variables this plugin needs to be set in
        in freevo_config.py. Each variable in again a list and contains
        (varname, default value, description)
        """
        return []


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
    """
    def __init__(self):
        Plugin.__init__(self)
        # FIXME: remove this
        self.defined_actions = self.actions
        self.actions = self.actions_wrapper


    def actions(self, item):
        """
        return a list of actions to that item. Each actions is a tuple
        (function, 'name-in-the-menu')
        """
        return []


    def actions_wrapper(self, item):
        """
        Bad warpper for actions used while actions is restructured.
        FIXME: remove this function.
        """
        from menu.action import ActionWrapper
        items = []
        for a in self.defined_actions(item):
            if isinstance(a, (list, tuple)):
                if len(a) > 3:
                    items.append(ActionWrapper(a[1], a[0], a[2], a[3]))
                elif len(a) > 2:
                    items.append(ActionWrapper(a[1], a[0], a[2]))
                elif hasattr(a, 'action'):
                    items.append(a.action)
                else:
                    items.append(ActionWrapper(a[1], a[0]))
            else:
                items.append(a)
        return items


    def eventhandler(self, item, event, menuw=None):
        """
        Additional eventhandler for this item.
        """
        return False

    
class DaemonPlugin(Plugin):
    """
    Plugin class for daemon objects who will be activate in the
    background while Freevo is running
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_interval  = 100       # poll every x milliseconds
        self.poll_menu_only = True      # poll only when menu is active
        self.event_listener = False     # process all events
        self.events         = []        # events to register to ([] == all)


    def poll(self):
        """
        This function will be called every poll_interval milliseconds.
        """
        pass


    def _poll(self):
        """
        wrapper for the poll function
        """
        if self.poll_menu_only and not eventhandler.is_menu():
            return True
        self.poll()
        return True


    def eventhandler(self, event):
        """
        Events no one else wants will be passed to this functions, when
        you also set the variable event_listener to True, the object will
        get all events. Setting self.events to a list of event names will]
        register only that events to the eventhandler.
        """
        return False

    
class MimetypePlugin(Plugin):
    """
    Plugin class for mimetypes handled in a directory/playlist.
    self.display_type is a list of display types where this mimetype
    should be displayed, [] for always.
    """
    def __init__(self):
        Plugin.__init__(self)
        self.display_type = []


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


    def count(self, parent, listing):
        """
        return how many items will be build on files
        """
        return len(listing.match_suffix(self.suffix()))


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


    def database(self):
        """
        returns a database object
        """
        return None


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
    _plugin_number += 1

    for p in _all_plugins:
        if not isinstance(name, Plugin) and p[0] == name and \
               p[1] == type and p[3] == args:
            log.warning('duplicate plugin activation, ignoring:\n' + \
                        '  <%s %s %s>' % (name, type, args))
            return
    if initialized:
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
    if initialized:
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
    return len(_all_plugins)


def init(callback = None, reject=['record', 'www'], exclusive=[]):
    """
    load and init all the plugins
    """
    global initialized
    initialized = True

    current = 0
    for name, type, level, args, number in _all_plugins:
        if notifier.step:
            notifier.step(False, False)
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



def get(type):
    """
    get the plugin list 'type'
    """
    if not _plugin_type_list.has_key(type):
        _plugin_type_list[type] = []
    return _plugin_type_list[type]


def getall():
    """
    return a list of all plugins
    """
    ret = []
    for t in _all_plugins:
        ret.append(t[0])
    return ret


def mimetype(display_type=None):
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
    if _named_plugins.has_key(name):
        return _named_plugins[name]
    if multiple_choises:
        return []
    return None


def register(plugin, name, multiple_choises=0):
    """
    register an object as a named plugin
    """
    if multiple_choises:
        if not _named_plugins.has_key(name):
            _named_plugins[name] = []
        _named_plugins[name].append(plugin)
    else:
        _named_plugins[name] = plugin


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

_all_plugins        = []
_plugin_number      = 0
_plugin_type_list   = {}
_named_plugins      = {}


def _add_to_ptl(type, object):
    """
    small helper function to add a plugin to the PluginTypeList
    """
    if not _plugin_type_list.has_key(type):
        _plugin_type_list[type] = []
    _plugin_type_list[type].append(object)



def _find_plugin_file(filename):
    full_filename = os.path.join(os.environ['FREEVO_PYTHON'], filename)

    if os.path.isfile(full_filename + '.py'):
        return filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return filename.replace('/', '.'), None

    full_filename = os.path.join(os.environ['FREEVO_PYTHON'],
                                 'plugins', filename)

    if os.path.isfile(full_filename + '.py'):
        return 'plugins.' + filename.replace('/', '.'), None

    if os.path.isdir(full_filename):
        return 'plugins.' + filename.replace('/', '.'), None

    if filename.find('/') > 0:
        special = filename[:filename.find('/')]
        filename = os.path.join(special, 'plugins',
                                filename[filename.find('/')+1:])
        full_filename = os.path.join(os.environ['FREEVO_PYTHON'], filename)

        if os.path.isfile(full_filename + '.py'):
            return filename.replace('/', '.'), special

        if os.path.isdir(full_filename):
            return filename.replace('/', '.'), special

    return None, None



def _load_plugin(name, type, level, args, number):
    """
    load the plugin and add it to the lists
    """
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
                log.warning('plugin %s deactivated\n  reason: %s' % \
                            (name, reason))
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

        if p._type:
            # special plugin type (e.g. idlebar)
            _add_to_ptl(p._type, p)

        else:
            if isinstance(p, DaemonPlugin):
                # plugin is a DaemonPlugin
                if p.__class__.poll != DaemonPlugin.poll:
                    # plugin has a self defined poll function, register it
                    notifier.addTimer( p.poll_interval, p._poll )

                if p.__class__.eventhandler != DaemonPlugin.eventhandler:
                    # plugin has a self defined eventhandler
                    if p.events:
                        for e in p.events:
                            eventhandler.register(p, e)
                    else:
                        if p.event_listener:
                            handler = eventhandler.EVENT_LISTENER
                        else:
                            handler = eventhandler.GENERIC_HANDLER
                        eventhandler.register(p, handler)

            if isinstance(p, MainMenuPlugin):
                # plugin is a MainMenuPlugin
                _add_to_ptl('mainmenu%s' % special, p)

            if isinstance(p, ItemPlugin):
                # plugin is an ItemPlugin
                _add_to_ptl('item%s' % special, p)

            if isinstance(p, MimetypePlugin):
                # plugin is a MimetypePlugin
                _add_to_ptl('mimetype', p)

        # register shutdown handler
        if p.__class__.shutdown != Plugin.shutdown:
            # plugin has a self defined shutdown function
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

