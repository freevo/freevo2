#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# plugins.py - list all plugins and prints help about them
# -----------------------------------------------------------------------
# $Id$
#
# Notes:       This script prints out informations aboyt plugins in
#              Freevo. As descriptions the Python class description
#              between two """ after the class name is used.
#
# Todo:        All plugins need to get a nice description
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/09/09 18:36:11  dischi
# add a plugin helper to get more informations about the plugins
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

import config
import plugin
import util
import re
import os
import sys


def parse_plugins():
    start = re.compile('^class *(.*)\((.*Plugin).:')
    stop  = re.compile('^[\t ]*def.*:')
    comment = re.compile('^[\t ]*"""')

    print_line = 0
    ptypes = {}
    
    all_plugins = []
    
    active = []
    for p in plugin.__all_plugins__:
        active.append(p[0])

    for file in util.recursefolders(os.environ['FREEVO_PYTHON'],1, '*.py',1):
        if file.find('plugin.py') > 0:
            continue
        parse_status = 0
        for line in util.readfile(file):
            if (comment.match(line) and parse_status == 2) or \
                   (stop.match(line) and parse_status == 1):
                parse_status = 0
                all_plugins[-1][-1] = desc

            if parse_status == 2:
                if desc:
                    desc += '\n'
                desc += line.lstrip().rstrip()

            if comment.match(line) and parse_status == 1:
                parse_status = 2

            if start.match(line):
                fname = re.sub('^src.', '', file)
                fname = re.sub('^%s.' % os.environ['FREEVO_PYTHON'], '', fname)
                fname = re.sub('/', '.', os.path.splitext(fname)[0])
                fname = re.sub('plugins.', '', fname)
                fname = re.sub('.__init__', '', fname)

                type = start.match(line).group(2)
                if re.match('^plugin.(.*)', type):
                    type = re.match('^plugin.(.*)', type).group(1)
                if start.match(line).group(1) == 'PluginInterface':
                    name = fname
                else:
                    name = '%s.%s' % ( fname, start.match(line).group(1))

                if name in active:
                    status = 'active'
                else:
                    status = 'not loaded'

                parse_status = 1
                desc = ''
                all_plugins.append([name, file, type, status, ''])
    return all_plugins


def print_info(plugin_name, all_plugins):
    for name, file, type, status, desc in all_plugins:
        if name == plugin_name:
            print 'Name: %s' % name
            print 'Type: %s' % type
            print 'File: %s' % file
            print
            print 'Description:'
            print desc
            print
            if status == 'active':
                print 'The plugin is loaded with the following settings:'
                for p in plugin.__all_plugins__:
                    if p[0] == name:
                        type = p[1]
                        if not type:
                            type = 'default'
                        print 'type=%s, level=%s, args=%s' % (type, p[2], p[3])
            else:
                print 'The plugin is not activated in the current setting'




# show a list of all plugins
if len(sys.argv)>1 and sys.argv[1] == '-l':
    for name, file, type, status, desc in parse_plugins():
        print '%s (%s, %s)' % (name, type, status)

# show info about a plugin
elif len(sys.argv)>2 and sys.argv[1] == '-i':
    print_info(sys.argv[2], parse_plugins())

# show infos about all plugins (long list)
elif len(sys.argv)>1 and sys.argv[1] == '-a':
    all_plugins = parse_plugins()
    for p in all_plugins:
        if p != all_plugins[0] and p != all_plugins[-1]:
            print '\n********************************\n'
        print_info(p[0], [p])

else:
    print 'This helper shows the list of all plugins included in Freevo and'
    print 'can print informations about them.'
    print
    print 'A plugin can be activated by adding "plugin.activate(name)" into the'
    print 'local_conf.py. Optional arguments are type, level and args'
    print 'type:  specifies the type of this plugin. The default it is all for plugins'
    print '       not located in a specific media dir (e.g. rom_drives), some plugins'
    print '       are supposed to be insert into the specific dir (e.g. video.imdb) and'
    print '       have this as default type. You can override it by setting the type, e.g.'
    print '       the type \'video\' for rom_drives.rom_items will only show the rom drives'
    print '       in the video main menu.'
    print 'level: specifies the position of the plugin in the plugin list. This sets the'
    print '       position of the items in the menu from this plugin to arrange them'
    print 'args:  some plugins require some additional arguments'
    print
    print 'To remove a plugin activated in freevo_config, it\'s possible to add '
    print '"plugin.remove(name)" into the local_conf.py. The activate function also'
    print 'returns a plugin number, for the plugins loaded by freevo_config, it\'s also'
    print 'possible to use this number: plugin.remove(number).'
    print
    print 'There are five types of plugins:'
    print 'MainMenuPlugin: show items in the main menu or in the media main menu like video'
    print 'ItemPlugin    : add actions to items, shown after pressing ENTER on the item'
    print 'DaemonPlugin  : a plugin that runs in the background'
    print 'IdlebarPlugin : subplugin for the idlebar plugin'
    print 'Plugin        : plugin to add some functions to Freevo, see plugin description.'
    print
    print
    print 'This helper script has the following options to get information about possible'
    print 'plugins in Freevo:'
    print
    print 'usage: freevo plugins [-l | -i name | -a ]'
    print ' -l           list all plugins'
    print ' -i name      print detailed informations about plugin "name"'
    print ' -a           print detailed informations about all plugins (long)'
    print
    print 'Please note that this helper is new and not all plugins have a good description.'
    print 'Feel free to send patches to the Freevo mailing list'
    print
    
