#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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
# Revision 1.1  2005/06/19 12:06:46  dischi
# rename plugin.py to pluginlist.py to avoid naming conflict
#
# Revision 1.12  2004/10/28 19:39:09  dischi
# adhust to internal plugin.py changes
#
# Revision 1.11  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.10  2004/02/14 15:06:59  dischi
# make sure all regexps end
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


import config
import plugin
import util
import re
import os
import sys

def parse_plugins():
    start = re.compile('^class *(.*)\((.*Plugin\s*).:')
    stop  = re.compile('^[\t ]*def.*:')
    comment = re.compile('^[\t ]*"""')
    config_start = re.compile('^[ \t]+def +config *\( *self *\) *:')
    config_end   = re.compile(' *(class|def)')
    
    print_line = 0
    ptypes = {}
    
    all_plugins = []
    
    active = []
    for p in plugin._all_plugins:
        active.append(p[0])

    for file in util.recursefolders(os.environ['FREEVO_PYTHON'],1, '*.py',1):
        if file.find('plugin.py') > 0:
            continue
        parse_status = 0
        whitespaces  = 0
        scan_config  = 0
        for line in util.readfile(file) + [ 'class Foo' ]:
            if config_end.match(line) and scan_config:
                scan_config = 0
                all_plugins[-1][-1] = config
                
            if scan_config:
                config += line+'\n'

            if config_start.match(line):
                config      = 'def return_config():\n'
                scan_config = line.find('def')


            if (comment.match(line) and parse_status == 2) or \
                   (stop.match(line) and parse_status == 1):
                parse_status = 0
                all_plugins[-1][-2] = desc

            if parse_status == 2:
                if desc:
                    desc += '\n'
                if not whitespaces:
                    tmp = line.lstrip()
                    whitespaces = line.find(tmp)
                desc += line[whitespaces:].rstrip()

            if comment.match(line) and parse_status == 1:
                parse_status = 2
                whitespaces  = 0
                
            if start.match(line):
                fname = re.sub('^src.', '', file)
                fname = re.sub('^%s.' % os.environ['FREEVO_PYTHON'], '', fname)
                fname = re.sub('/', '.', os.path.splitext(fname)[0])
                fname = re.sub('plugins.', '', fname)
                fname = re.sub('.__init__', '', fname)

                type = start.match(line).group(2).strip()
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
                if not name in ('idlebar.IdleBarPlugin', ):
                    all_plugins.append([name, file, type, status, '', ''])
    return all_plugins


def print_info(plugin_name, all_plugins):
    for name, file, type, status, desc, config_string in all_plugins:
        if name == plugin_name:
            print 'Name: %s' % name
            print 'Type: %s' % type
            print 'File: %s' % file
            print
            print 'Description:'
            print '------------'
            print desc
            print
            if config_string.find('config') > 0:
                exec(config_string)
                config_list = return_config()

                if config_list:
                    print
                    print 'Plugin configuration variables:'
                    print '-------------------------------'
                    for v in config_list:
                        print '%s: %s' % (v[0], v[2])
                        print 'Default: %s' % v[1]
                        print
                    print
            if status == 'active':
                print 'The plugin is loaded with the following settings:'
                for p in plugin._all_plugins:
                    if p[0] == name:
                        type = p[1]
                        if not type:
                            type = 'default'
                        print 'type=%s, level=%s, args=%s' % (type, p[2], p[3])
            else:
                print 'The plugin is not activated in the current setting'

def iscode(line):
    return (len(line) > 2 and line[:2].upper() == line[:2] and \
            line.find('=') > 0) or \
            (line and line[0] in ('#',' ', '[', '(')) or (line.find('plugin.') == 0)


def info_html(plugin_name, all_plugins):
    ret = ''
    for name, file, type, status, desc, config_string in all_plugins:
        if name == plugin_name:
            ret += '<h2>%s</h2>' % name
            ret += '<b>Type: %s</b><br>' % type
            ret += '<b>File: %s</b><br>' % file
            ret += '\n'
            if not desc:
                ret += '<p>The plugin has no description. You can help by ' + \
                       'writing a small description and send it to the Freevo '\
                       'mailinglist.</p>\n'
            else:
                ret += '<br><b>Description</b>:'
                ret += '<p>'
                tmp  = desc
                desc = []
                for block in tmp.split('\n\n'):
                    for line in block.split('\n'):
                        desc.append(line)
                    desc.append('')

                code = 0
                for i in range(len(desc)):
                    line = desc[i]
                    if iscode(line):
                        if not code:
                            ret += '<br><pre class="code">\n'
                        ret += line+'\n'
                        code = 1

                        try:
                            if (desc[i+1] and not iscode(desc[i+1])) or \
                                   (desc[i+2] and not iscode(desc[i+2])):
                                ret += '</pre>'
                                code = 0
                        except IndexError:
                            ret += '</pre>'
                            code = 0
                    elif line:
                        ret += line + '\n'
                    elif code:
                        ret += '\n'
                    else:
                        ret += '<br>\n'

                if code:
                    ret += '</pre>'
                    code = 0
                ret += '</p>'
                ret += '\n'

            if status == 'active':
                ret += '<p>The plugin is loaded with the following settings:'
                for p in plugin._all_plugins:
                    if p[0] == name:
                        type = p[1]
                        if not type:
                            type = 'default'
                        ret += '<br>type=%s, level=%s, args=%s' % (type, p[2], p[3])
                ret += '</p>'
            else:
                ret += '<p>The plugin is not activated in the current setting</p>'
            return ret
    return ret
    


# show a list of all plugins
if len(sys.argv)>1 and sys.argv[1] == '-l':
    all_plugins = parse_plugins()

    types = []
    for p in all_plugins:
        if not p[2] in types:
            types.append(p[2])
    for t in types:
        print
        print '%ss:' % t
        underline = '--'
        for i in range(len(t)):
            underline += '-'
        print underline
        for name, file, type, status, desc, config in all_plugins:
            if type == t:
                if desc.find('\n') > 0 and desc.find('\n\n') == desc.find('\n'):
                    smalldesc = desc[:desc.find('\n')]
                else:
                    smalldesc = desc
                if len(smalldesc) > 43:
                    smalldesc = smalldesc[:40] + '...'
                if status == 'active':
                    name = '%s (%s)' % (name, status)
                print '%-35s %s' % (name, smalldesc)

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

# show infos about all plugins as html
elif len(sys.argv)>1 and sys.argv[1] == '-html':
    all_plugins = parse_plugins()

    print '<html><head>\
<meta HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=iso-8859-1">\
<title>Freevo Plugins</title>\
<link rel="stylesheet" type="text/css" href="freevowiki.css">\
</head>\
<body>\
<font class="headline" size="+3">Freevo Plugin List</font>\
<p><b>Index</b><ol>'

    for p in all_plugins:
        print '<li><a href="#%s">%s</a></li>' % (p[0], p[0])
    print '</ol> '

    for p in all_plugins:
        print '<a name="%s"></a>' % p[0]
        print info_html(p[0], [p])

    print '</body>'

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
    
