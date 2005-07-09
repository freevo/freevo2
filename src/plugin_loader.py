# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin_loader.py - Plugin interface
# -----------------------------------------------------------------------------
# $Id$
#
# This file is the basic plugin interface for Freevo. It defines simple plugin
# base classes functions to add or remove a plugin.
#
# TODO: o make it possible to remove plugins later
#       o more cleanup
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

import kaa.notifier

# get logging object
log = logging.getLogger('plugin')


class Plugin(object):
    """
    Basic plugin class. All plugins should inherit from this class
    """
    def __init__(self):
        self.plugin_type = None
        self.plugin_level  = 10
        self.plugin_name = ''
        self.plugin_special = False


    def plugin_activate(self):
        """
        Execute on activation of the plugin.
        """
        pass


    def plugin_decativate(self):
        """
        Execute when the plugin is deactivated.
        """
        pass



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
            cmp_func = lambda l, o: cmp(l.plugin_level, o.plugin_level)
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


    def init(self, plugin_path, callback = None, plugins=[]):
        """
        Load and init all the plugins. The function takes the path were the
        plugins are searched in. Optional is a callback, called after a
        plugin is loaded. If 'plugins' is given, only plugins with the given
        prefix are loaded.
        """
        self.__initialized = True
        self.path = plugin_path
        
        for name, type, level, args, number in self.plugins:
            kaa.notifier.step(False, False)
            if callback:
                callback()
            if isinstance(name, Plugin):
                # plugin already an object
                self.__load_plugin(name, type, level, args)
                continue

            if plugins:
                # load only plugins from exclusive list
                for p in plugins:
                    if name.startswith('%s.' % p):
                        self.__load_plugin(name, type, level, args)
            else:
                parent = name[:name.rfind('.')]
                if name.find('.') > 0 and not self.is_active(parent):
                    # Parent plugin is not active. So this plugin is
                    # deactivated by default.
                    log.info('skip plugin %s' % name)
                    continue
                self.__load_plugin(name, type, level, args)

        # sort plugins
        cmp_func = lambda l, o: cmp(l.plugin_level, o.plugin_level)
        for key in self.types:
            self.types[key].sort(cmp_func)


    def get(self, type):
        """
        Get the plugin list 'type' or all if type is None
        """
        if not type:
            return self.plugins
        if not self.types.has_key(type):
            self.types[type] = []
        return self.types[type]


    def getbyname(self, name, multiple_choises=0):
        """
        Get a plugin by it's name
        """
        if self.names.has_key(name):
            return self.names[name]
        if multiple_choises:
            return []
        return None


    def register(self, plugin, name, multiple_choises=0):
        """
        Register an object as a named plugin
        """
        if multiple_choises:
            if not self.names.has_key(name):
                self.names[name] = []
            self.names[name].append(plugin)
        else:
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

                if not hasattr(p, 'plugin_type'):
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

            p.plugin_activate()
            p.plugin_level = level

            if type:
                special = type

            if p.plugin_type:
                if p.plugin_special and special:
                    key = p.plugin_type + '_' + special
                else:
                    key = p.plugin_type

                if not self.types.has_key(key):
                    self.types[key] = []
                self.types[key].append(p)

            if p.plugin_name:
                self.names[p.plugin_name] = p


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
