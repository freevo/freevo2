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

mainmenu  = []
videomenu = []


class Plugin:
    def __init__(self):
        pass


class MainMenuPlugin(Plugin):
    def __init__(self):
        pass

    def items(self, parent):
        return []


#
# activate a plugin
#
def activate(name, type, level, args):
    for i in range(len(type)):
        if type[i][1] > level:
            type.insert(i, (name, level, args ))
            return
    type.append(( name, level, args))


#
# load and init all the plugins
#
def init():
    for l in (mainmenu, videomenu):
        remove = []
        for i in range(len(l)):
            module = l[i][0][:l[i][0].rfind('.')]
            
            if os.path.isfile('src/plugins/%s.py' % module):
                module = 'plugins.%s' % module
                object = 'plugins.%s' % l[i][0]
            else:
                module = l[i][0]
                object = '%s.PluginInterface' % module

            exec('import %s' % module)
            try:
                if l[i][2]:
                    l[i] = eval('%s%s' % (object, str(l[i][2])))
                else:
                    l[i] = eval('%s()' % object)

            except ImportError:
                print 'failed to load plugin %s' % l[i][0]
                remove.append(i-len(remove))

            except AttributeError:
                print 'failed to load plugin %s' % l[i][0]
                remove.append(i-len(remove))

            except TypeError:
                print 'wrong number of parameter for %s' % l[i][0]
                remove.append(i-len(remove))
                
        for i in remove:
            l.remove(l[i])

