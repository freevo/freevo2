# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# setup.py - setup script for installing the freevo module
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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
import sys
import os
import stat

# We require python 2.5 or later, so complain if that isn't satisfied.
if sys.version.split()[0] < '2.5':
    print "Python 2.5 or later required."
    sys.exit(1)

# try to be clever and add the install prefix to the path
# to be sure kaa.base and freevo.core can be found
for pos, arg in enumerate(sys.argv[1:]):
    if arg.startswith('--prefix='):
        prefix=arg[9:]
    elif arg.startswith('--prefix') and pos + 2 < len(sys.argv):
        prefix=sys.argv[pos+2]
    else:
        continue
    libdir = 'lib/python%s.%s/site-packages' % sys.version_info[:2]
    sys.path.insert(0, os.path.join(prefix, libdir))

sys.path.insert(0, 'src/core')
# import freevo distribution utils
from distribution import setup, VERSION
from xmlconfig import xmlconfig

data_files = []
# add some files to Docs
for f in ('COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % VERSION, ['%s' % f ]))

if len(sys.argv) > 1 and not '--help' in sys.argv and \
       not '--help-commands' in sys.argv:
    def cxml_finder(result, dirname, names):
        for name in names:
            if name.endswith('.cxml'):
                result.append(os.path.join(dirname, name))
        return result
    cxml_files = []
    os.path.walk('./src', cxml_finder, cxml_files)
    if not os.path.isfile('build/config.cxml') or \
       os.stat('build/config.cxml')[stat.ST_MTIME] < \
       max(*[os.stat(x)[stat.ST_MTIME] for x in cxml_files ]):
        if not os.path.isdir('build'):
            os.mkdir('build')
        xmlconfig('build/config.cxml', cxml_files, 'freevo2')

    data_files.append(('share/freevo2/config', [ 'build/config.cxml' ]))

def package_finder(result, dirname, names):
    """
    os.path.walk helper for 'src'
    """
    for name in names:
        if os.path.splitext(name)[1] == '.py':
            import_name = dirname.replace('/','.').replace('..src', 'freevo2')
            result[import_name] = dirname
            return result
    return result

package_dir = {}
os.path.walk('./src', package_finder, package_dir)

# now start the python magic
setup (name         = 'freevo',
       version      = VERSION,
       description  = 'Freevo',
       author       = 'Krister Lagerstrom, et al.',
       author_email = 'freevo-devel@lists.sourceforge.net',
       url          = 'http://www.freevo.org',
       license      = 'GPL',
       package_dir  = package_dir,
       i18n         = 'freevo',
       data_files   = data_files,
       )
