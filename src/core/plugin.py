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
# Copyright (C) 2003-2009 Dirk Meyer, et al.
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

__all__ = [ 'Plugin', 'init_plugins', 'activate_plugin', 'register_plugin', 'get_plugin' ]

# python imports
import os
import logging

# kaa imports
import kaa

# get logging object
log = logging.getLogger('plugin')


class Plugin(object):
    """
    Basic plugin class.
    """

    plugin_media = None

    def __init__(self, name=''):
        self._plugin_level = 10

    def plugin_activate(self, level):
        """
        Activate the plugin with given level
        """
        pass

    def plugin_set_name(self, name):
        """
        Register plugin with the given name. In most cases this is not needed
        because the plugin will always be registered by its own name.
        """
        _loader.names[name] = self

    def plugin_level(self):
        """
        Return plugin level.
        """
        return self._plugin_level


class PluginLoader(object):
    """
    Class for handling the different plugins.
    """

    def __init__(self):
        self._plugin_list  = []
        self._baseclasses  = []
        self._plugin_names = {}
        self._initialized  = False

    def activate(self, name, type=None, level=10, args=None):
        """
        Activate a plugin.
        """
        if not self._initialized:
            return self._plugin_list.append((name, type, level, args))
        self.__load_plugin(name, type, level, args)
        # sort plugins again
        cmp_func = lambda l, o: cmp(l._plugin_level, o._plugin_level)
        for c in self._baseclasses:
            c.plugin_list.sort(cmp_func)

    def init(self, module, callback = None):
        """
        Load and init all the plugins. The function takes the path were the
        plugins are searched in. Optional is a callback, called after a
        plugin is loaded. If 'plugins' is given, only plugins with the given
        prefix are loaded.
        """
        self._initialized = True
        self.path = os.path.dirname(module.__file__)
        self.import_path = module.__name__
        for name, type, level, args in self._plugin_list:
            kaa.main.step(False, True)
            if callback:
                callback()
            self.__load_plugin(name, type, level, args)
        # sort plugins
        cmp_func = lambda l, o: cmp(l._plugin_level, o._plugin_level)
        for c in self._baseclasses:
            c.plugin_list.sort(cmp_func)

    def getbyname(self, name):
        """
        Get a plugin by it's name
        """
        return self._plugin_names.get(name, None)

    def register(self, plugin):
        """
        Register a plugin class
        """
        plugin.plugin_list = []
        return self._baseclasses.append(plugin)

    def _find_plugin_file(self, name):
        """
        Find the filename for the plugin and the python import statement.
        """
        filename = name.replace('.', '/')
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
        if filename.find('/') == -1:
            # unable to find plugin
            return None, None
        special, filename = filename.split('/', 1)
        filename = os.path.join(special, 'plugins', filename)
        full_filename = os.path.join(self.path, filename)
        if os.path.isfile(full_filename + '.py'):
            return filename.replace('/', '.'), special
        if os.path.isdir(full_filename):
            return filename.replace('/', '.'), special
        # unable to find plugin
        return None, None

    def __load_plugin(self, name, type, level, args):
        """
        Load the plugin and add it to the lists
        """
        if not isinstance(name, Plugin):
            # -----------------------------------------------------
            # locate plugin python file
            # -----------------------------------------------------
            module, special = self._find_plugin_file(name)
            if module:
                pclass = 'PluginInterface'
            elif name.find('.') > 0:
                pname = name[:name.rfind('.')]
                module, special = self._find_plugin_file(pname)
                if module:
                    pclass = name[name.rfind('.')+1:]
                else:
                    log.critical('unable to locate plugin %s' % name)
                    return
            else:
                log.critical('unable to locate plugin %s' % name)
                return
            # -----------------------------------------------------
            # load plugin python file
            # -----------------------------------------------------
            try:
                module = '%s.%s' % (self.import_path, module)
                log.debug('loading %s as plugin %s' % (module, pclass))
                exec('from %s import %s as plugin_class' % (module, pclass))
                # create object
                if not args:
                    plugin = plugin_class()
                elif isinstance(args, list) or isinstance(args, tuple):
                    plugin = plugin_class(*args)
                else:
                    plugin = plugin_class(args)
                # init failed
                if not hasattr(plugin, '_plugin_level'):
                    if hasattr(plugin, 'reason'):
                        reason = plugin.reason
                    else:
                        reason = '''unknown
                        The plugin neither called __init__ nor set a reason why
                        Please contact the plugin author'''
                    log.warning('plugin %s deactivated\n  reason: %s' % (name, reason))
                    return
            except:
                log.exception('failed to load plugin %s' % name)
                return
        else:
            # name is a plugin object
            plugin = name
            special = None
        # -----------------------------------------------------
        # configure and activate plugin object
        # -----------------------------------------------------
        if type:
            special = type
        try:
            plugin._plugin_level = level
            if special:
                plugin.plugin_media = special
            plugin.plugin_activate(level)
        except:
            log.exception('failed to activate plugin %s' % name)
            return
        # -----------------------------------------------------
        # register plugin object
        # -----------------------------------------------------
        self._plugin_names[name] = plugin
        for c in self._baseclasses:
            if isinstance(plugin, c):
                c.plugin_list.append(plugin)


_loader = PluginLoader()

# interface:
init_plugins = _loader.init
activate_plugin = _loader.activate
register_plugin = _loader.register
get_plugin = _loader.getbyname
