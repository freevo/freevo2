# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some special plugins known to Freevo.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2006 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

# kaa imports
import kaa.notifier

# get logging object
log = logging.getLogger('plugin')

#
# Some basic plugins known to Freevo.
#

class Plugin(object):
    """
    Basic plugin class.
    """

    def __init__(self, name=''):
        self._plugin_type = None
        self._plugin_level  = 10
        self._plugin_name = name
        self._plugin_special = False



class MainMenuPlugin(Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self._plugin_type = 'mainmenu'
        self._plugin_special = True


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
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self._plugin_type = 'item'
        self._plugin_special = True


    def actions(self, item):
        """
        return a list of actions to that item. Each action is type Action
        """
        return []


    def eventhandler(self, item, event):
        """
        Additional eventhandler for this item.
        """
        return False


class MimetypePlugin(Plugin):
    """
    Plugin class for mimetypes handled in a directory/playlist.
    self.display_type is a list of display types where this mimetype
    should be displayed, [] for always.
    """
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self.display_type = []
        self._plugin_type = 'mimetype'


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
        c = 0
        for t in self.suffix():
            c += len(listing.get(t))
        return c


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        pass


    def database(self):
        """
        returns a database object
        """
        return None


class PluginLoader(object):
    """
    Class for handling the different plugins.
    """
    def __init__(self):
        """
        Init the plugin loader.
        """
        # path where to search for plugins, will be set on init
        self.path = None
        # list of all plugins
        self.plugins = []
        self.loaded_plugins = []

        # next id for a plugin
        self.next_id = 0
        # plugins sorted by type
        self.types = {}
        # plugins based on name
        self.names = {}
        # status of the plugin module
        self.__initialized = False


    def activate(self, name, type=None, level=10, args=None):
        """
        Activate a plugin.
        """
        self.next_id += 1

        for p in self.plugins:
            if not isinstance(name, Plugin) and p[0] == name and \
                   p[1] == type and p[3] == args:
                log.warning('duplicate plugin activation, ignoring:\n' + \
                            '  <%s %s %s>' % (name, type, args))
                return
        if self.__initialized:
            self.__load_plugin(name, type, level, args)
            # sort plugins again
            cmp_func = lambda l, o: cmp(l._plugin_level, o._plugin_level)
            for key in self.types:
                self.types[key].sort(cmp_func)
        else:
            self.plugins.append((name, type, level, args, self.next_id))
        return self.next_id


    def deactivate(self, id):
        """
        Remove a plugin from the list.
        """
        if self.__initialized:
            return

        if isinstance(id, int):
            # remove by plugin id
            for p in self.plugins:
                if p[4] == id:
                    self.plugins.remove(p)
                    return
        else:
            # remove by name
            for p in copy.copy(self.plugins):
                if p[0] == id:
                    self.plugins.remove(p)


    def is_active(self, name, arg=None):
        """
        Search the list if the given plugin is active. If arg is set,
        check arg, too.
        """
        for p in self.plugins:
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


    def init(self, plugin_path, callback = None):
        """
        Load and init all the plugins. The function takes the path were the
        plugins are searched in. Optional is a callback, called after a
        plugin is loaded. If 'plugins' is given, only plugins with the given
        prefix are loaded.
        """
        self.__initialized = True
        self.path = plugin_path

        for name, type, level, args, number in self.plugins:
            kaa.notifier.step(False, True)
            if callback:
                callback()
            if isinstance(name, Plugin):
                # plugin already an object
                self.__load_plugin(name, type, level, args)
                continue
            self.__load_plugin(name, type, level, args)

        # sort plugins
        cmp_func = lambda l, o: cmp(l._plugin_level, o._plugin_level)
        for key in self.types:
            self.types[key].sort(cmp_func)


    def get(self, type=None):
        """
        Get the plugin list 'type' or all if type is None
        """
        if type == None:
            return self.plugins
        if not self.types.has_key(type):
            self.types[type] = []
        return self.types[type]


    def getbyname(self, name):
        """
        Get a plugin by it's name
        """
        return self.names.get(name, None)


    def register(self, plugin, name):
        """
        Register an object as a named plugin
        """
        self.names[name] = plugin


    def __find_plugin_file(self, filename):
        """
        Find the filename for the plugin and the python import statement.
        """
        full_filename = os.path.join(self.path, filename)

        if os.path.isfile(full_filename + '.py'):
            return filename.replace('/', '.'), None

        if os.path.isdir(full_filename):
            return filename.replace('/', '.'), None

        full_filename = os.path.join(self.path, 'plugins', filename)

        if os.path.isfile(full_filename + '.py'):
            return 'plugins.' + filename.replace('/', '.'), None

        if os.path.isdir(full_filename):
            return 'plugins.' + filename.replace('/', '.'), None

        if filename.find('/') > 0:
            special = filename[:filename.find('/')]
            filename = os.path.join(special, 'plugins',
                                    filename[filename.find('/')+1:])
            full_filename = os.path.join(self.path, filename)

            if os.path.isfile(full_filename + '.py'):
                return filename.replace('/', '.'), special

            if os.path.isdir(full_filename):
                return filename.replace('/', '.'), special

        return None, None


    def __load_plugin(self, name, type, level, args):
        """
        Load the plugin and add it to the lists
        """
        # fallback
        module  = name
        object  = '%s.PluginInterface' % module
        special = None

        # locate the plugin:
        files = []

        if not isinstance(name, Plugin):
            module, special = self.__find_plugin_file(name.replace('.', '/'))
            if module:
                object = module + '.PluginInterface'
            elif name.find('.') > 0:
                pname = name[:name.rfind('.')].replace('.', '/')
                module, special = self.__find_plugin_file(pname)
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

                if not hasattr(p, '_plugin_type'):
                    if hasattr(p, 'reason'):
                        reason = p.reason
                    else:
                        reason = '''unknown
                        The plugin neither called __init__ nor set a reason why
                        Please contact the plugin author'''
                    log.warning('plugin %s deactivated\n  reason: %s' % \
                                (name, reason))
                    return
            else:
                p = name

            p._plugin_level = level

            if type:
                special = type

            if p._plugin_type:
                if p._plugin_special and special:
                    key = p._plugin_type + '_' + special
                else:
                    key = p._plugin_type

                if not self.types.has_key(key):
                    self.types[key] = []
                self.types[key].append(p)

            if p._plugin_name:
                self.names[p._plugin_name] = p

            self.loaded_plugins.append(p)

        except:
            log.exception('failed to load plugin %s' % name)



_loader = PluginLoader()

# interface:
activate = _loader.activate
remove = _loader.deactivate
deactivate = _loader.deactivate
is_active = _loader.is_active
init = _loader.init
get = _loader.get
getbyname = _loader.getbyname
register = _loader.register

def mimetype(display_type=None):
    """
    return all MimetypePlugins for the given display_type. If display_type
    is None, return all MimetypePlugins.
    """
    if not display_type:
        return get('mimetype')
    ret = []
    for p in get('mimetype'):
        if not p.display_type or display_type in p.display_type:
            ret.append(p)
    return ret
