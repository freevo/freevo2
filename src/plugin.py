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
# Revision 1.12  2003/04/21 18:19:54  dischi
# make it possible that whole directories can be a plugin
#
# Revision 1.11  2003/04/21 13:28:54  dischi
# Make it possible to inherit a plugin from Plugin(). This plugin will only
# be loaded, nothing else!
#
# Revision 1.10  2003/04/21 13:00:06  dischi
# mainmenu plugins can also have global eventhandlers
#
# Revision 1.9  2003/04/20 20:58:49  dischi
# scan for plugins and print them
#
# Revision 1.8  2003/04/20 11:44:45  dischi
# add item plugins
#
# Revision 1.7  2003/04/20 10:54:04  dischi
# add getbyname and add some more load paths
#
# Revision 1.6  2003/04/19 21:24:59  dischi
# small changes at the plugin interface
#
# Revision 1.5  2003/04/18 15:01:37  dischi
# support more types of plugins and removed the old item plugin support
#
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
import traceback

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
        self.plugin_name   = ''

        
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


class ItemPlugin(Plugin):
    """
    Plugin class to add something to the item action list
    """
    def __init__(self):
        Plugin.__init__(self)
        self._type = 'item'

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
        this function will be called every 0.1 seconds
    def draw(self):
        this function will be caleed to update the screen
    def eventhandler(self, event):
        events no one else wants will be passed to this functions
    """
    def __init__(self):
        Plugin.__init__(self)
        self._type   = 'daemon'



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
named_plugins = {}

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
    global named_plugins
    
    initialized = TRUE

    for name, type, level, args, number in all_plugins:
        module = name[:name.rfind('.')]

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
                p._type  = type
            elif special:
                p._type  = '%s_%s' % (p._type, special)
            if level:
                p._level = level

            if p._type:
                if not ptl.has_key(p._type):
                    ptl[p._type] = []
                type = ptl[p._type]

                for i in range(len(type)):
                    if type[i]._level > p._level:
                        type.insert(i, p)
                        break
                else:
                    type.append(p)

            if p.plugin_name:
                named_plugins[p.plugin_name] = p
                
                
        except:
            print 'failed to load plugin %s' % name
            traceback.print_exc()

    if ptl.has_key('daemon'):
        for type in ('poll', 'draw', 'eventhandler' ):
            ptl['daemon_%s' % type] = []
            for p in ptl['daemon']:
                if hasattr(p, type):
                    ptl['daemon_%s' % type].append(p)

    for mtype in ( '', '_video', '_audio', '_image', '_games' ):
        if ptl.has_key('mainmenu%s' % mtype):
            for p in ptl['mainmenu%s' % mtype]:
                if hasattr(p, 'eventhandler'):
                    ptl['daemon_eventhandler'].append(p)
                
            
#                
# get the plugin list 'type'
#
def get(type):
    global ptl

    if not ptl.has_key(type):
        ptl[type] = []

    return ptl[type]


def getbyname(name):
    global named_plugins
    if named_plugins.has_key(name):
        return named_plugins[name]
    return None

#
# create plugin event
#
def event(name):
    return 'PLUGIN_EVENT %s' % name

#
# plugin event parsing
#
def isevent(event):
    if event[:12] == 'PLUGIN_EVENT':
        return event[13:]
    else:
        return None

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
        for line in open(str(file),'r').readlines():
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
        
