# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xmlconfig.py - Handling of cxml config files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
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

__all__ = [ 'xmlconfig' ]

# python imports
import os
import stat
import md5
from xml.dom import minidom

# kaa imports
import kaa.distribution.xmlconfig


def xmlconfig(configfile, sources, package):

    hashkey = [ f+str(os.stat(f)[stat.ST_MTIME]) for f in sources ]
    hashkey = md5.new(''.join(hashkey)).hexdigest()

    if os.path.isfile(configfile):
        fd = open(configfile)
        fd.readline()
        if fd.readline() == '# -*- hash: %s -*-\n' % hashkey:
            fd.close()
            return True
        fd.close()

    doc = None
    modules = []
    for cfg in sources:
        # load cxml file
        m = minidom.parse(cfg).firstChild
        if m.nodeName != 'config':
            raise RuntimeError('%s is no valid cxml file' % cfg)
        if not m.getAttribute('name'):
            doc = m.parentNode
            continue
        if not m.getAttribute('name').endswith('plugin'):
            modules.append(m)
            continue
        # list of plugins
        for plugin in m.childNodes:
            if plugin.nodeName == 'group':
                name = '%s.%s' % (m.getAttribute('name'), plugin.getAttribute('name'))
                plugin.setAttribute('name', name)
                modules.append(plugin)

    def valfunc(node):
        name = node.getAttribute('name')
        if name.startswith('plugin'):
            return '2%s' % name
        if node.hasAttribute('plugin') or '.plugin.' in name:
            return '1%s' % name
        if 'gui' in name:
            return '3%s' % name
        return '0%s' % name

    # sort modules somehow
    modules.sort(lambda x,y: cmp(valfunc(x), valfunc(y)))

    if doc is None:
        doc = '<?xml version="1.0"?><config name=""></config>'
        doc = minidom.parseString(doc)

    def get_parent(parent, name, position=''):
        for child in parent.childNodes:
            if child.nodeName == 'group':
                # print 'have', child.getattr('name')
                if position + child.nodeName == name:
                    raise RuntimeError('bad tree')
                if name.startswith(position + child.getAttribute('name')):
                    # print 'deeper'
                    position = position + child.getAttribute('name') + '.'
                    return get_parent(child, name, position)
        for name in name[len(position):].strip(' .').split('.'):
            node = doc.createElement('group')
            node.setAttribute('name', name)
            parent.appendChild(node)
            parent = node
        return parent

    for m in modules:
        parent = get_parent(doc.firstChild, m.getAttribute('name'))
        if m.hasAttribute('plugin'):
            node = doc.createElement('var')
            node.setAttribute('name', 'activate')
            node.setAttribute('default', m.getAttribute('plugin'))
            parent.appendChild(node)
            parent.setAttribute('is_plugin', 'yes')
        for child in m.childNodes[:]:
            parent.appendChild(child)

    if configfile.endswith('.cxml'):
        return open(configfile, 'w').write(doc.toxml())
    
    out = open(configfile, 'w')
    out.write('# -*- coding: iso-8859-1 -*-\n')
    out.write('# -*- hash: %s -*-\n' % hashkey)
    out.write('# auto generated file\n\n')
    out.write('from kaa.config import *\n\n')
    out.write('config = ')
    kaa.distribution.xmlconfig.Parser(package).parse(doc.firstChild, out)

    def find_plugins(node, position=''):
        for child in node.childNodes:
            if not child.nodeName == 'group':
                continue
            if child.hasAttribute('is_plugin'):
                name = "%s%s" % (position, child.getAttribute('name'))
                out.write('\'%s\', ' % name.strip('. ,'))
            find_plugins(child, position + child.getAttribute('name') + '.')
    out.write('\nplugins = [')
    find_plugins(doc.firstChild)
    out.write(']\n')

    def find_events(node):
        for child in node.childNodes:
            if child.nodeName == 'event':
                out.write('\'%s\', ' % child.getAttribute('name'))
            if child.nodeName == 'group':
                find_events(child)
    out.write('\nevents = [')
    find_events(doc.firstChild)
    out.write(']\n')
    
    def find_extern(node):
        for child in node.childNodes:
            if child.nodeName == 'extern':
                out.write('import %s\n' %  child.getAttribute('module'))
                out.write('config.add_variable(\'%s\', %s.config)\n\n' % \
                          (child.getAttribute('name'), child.getAttribute('module')))
            if child.nodeName == 'group':
                find_extern(child)
    find_extern(doc.firstChild)
    
    def find_code(node):
        for child in node.childNodes:
            if child.nodeName == 'code':
                out.write(kaa.distribution.xmlconfig.format_content(child) + '\n\n')
            if child.nodeName == 'group':
                find_code(child)
    find_code(doc.firstChild)
    out.close()
