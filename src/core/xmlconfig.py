# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xmlconfig.py - Handling of cxml config files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2009 Dirk Meyer, et al.
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
import hashlib
from xml.dom import minidom

# kaa imports
import kaa.distribution.xmlconfig

def nodeattr(node, attr):
    for c in node.childNodes:
        if c.nodeName == attr:
            return ''.join(x.toxml() for x in c.childNodes)
    return ''

def xmlconfig(configfile, sources, package):
    """
    Write kaa.config XML file for Freevo. Reading it again is done in
    kaa.config without extra function here.
    """
    hashkey = [ f+str(os.stat(f)[stat.ST_MTIME]) for f in sources ]
    hashkey = hashlib.md5(''.join(hashkey)).hexdigest()

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
        if m.nodeName == 'plugin':
            m.setAttribute('plugin', m.getAttribute('activate'))
        elif m.nodeName == 'config':
            if not m.getAttribute('name'):
                doc = m.parentNode
                continue
        else:
            raise RuntimeError('%s is no valid cxml file' % cfg)
        modules.append(m)

    def valfunc(node):
        name = node.getAttribute('name')
        if name.startswith('plugin'):
            return '3%s' % name
        if 'plugin' in name:
            return '2%s' % name
        if node.hasAttribute('plugin'):
            return '1%s' % name
        if 'gui' in name:
            return '4%s' % name
        return '0%s' % name

    # sort modules somehow
    modules.sort(lambda x,y: cmp(valfunc(x), valfunc(y)))

    if doc is None:
        doc = '<?xml version="1.0"?><config name=""></config>'
        doc = minidom.parseString(doc)

    def get_parent(parent, name, position=''):
        for child in parent.childNodes:
            if child.nodeName == 'group':
                if position + child.nodeName == name:
                    raise RuntimeError('bad tree')
                if name.startswith(position + child.getAttribute('name')):
                    position = position + child.getAttribute('name') + '.'
                    return get_parent(child, name, position)
        for name in name[len(position):].strip(' .').split('.'):
            if name:
                node = doc.createElement('group')
                node.setAttribute('name', name)
                parent.appendChild(node)
                parent = node
        return parent

    for m in modules:
        parent = get_parent(doc.firstChild, m.getAttribute('name'))
        if m.getAttribute('plugin'):
            parent.setAttribute('plugin', m.getAttribute('plugin'))
        for child in m.childNodes[:]:
            parent.appendChild(child)

    if configfile.endswith('.cxml'):
        return open(configfile, 'w').write(doc.toxml())

    plugins = []
    def find_plugins(node, position=''):
        for child in node.childNodes:
            if not child.nodeName == 'group':
                continue
            if child.hasAttribute('plugin'):
                node = doc.createElement('var')
                node.setAttribute('name', 'activate')
                node.setAttribute('default', child.getAttribute('plugin'))
                child.insertBefore(node, child.firstChild)
                child.setAttribute('is_plugin', 'yes')
                plugins.append("%s%s" % (position, child.getAttribute('name')))
            find_plugins(child, position + child.getAttribute('name') + '.')
    find_plugins(doc.firstChild)

    out = open(configfile, 'w')
    out.write('# -*- coding: iso-8859-1 -*-\n')
    out.write('# -*- hash: %s -*-\n' % hashkey)
    out.write('# auto generated file\n\n')
    out.write('from kaa.config import *\n\n')
    out.write('config = ')
    kaa.distribution.xmlconfig.Parser(package).parse(doc.firstChild, out)

    out.write('\nplugins = [')
    for plugin in plugins:
        out.write('\'%s\', ' % plugin.strip('. ,'))
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
