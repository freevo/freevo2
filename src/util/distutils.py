# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/distutils.py - Freevo distutils for installing plugins
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#  If you want to create a package with a plugin, you have to rebuild
#  the freevo directory structure. E.g. if you have a video plugin and
#  an image for it, you should have the following structure:
#
#  root
#    |--> setup.py
#    |
#    |--> share
#    | |--> images
#    | | |--> file.jpg
#    |
#    |--> src
#    | |--> video
#    | | |--> plugins
#    | | | |--> __init__.py (empty)
#    | | | |--> plugin.py
#
#
#  The setup.py file should look like this:
#
#  |   #!/usr/bin/env python
#  |   
#  |   """Setup script for my freevo plugin."""
#  |   
#  |   
#  |   __revision__ = "$Id$"
#  |   
#  |   from distutils.core import setup, Extension
#  |   import distutils.command.install
#  |   from freevo.util.distutils import *
#  |   
#  |   # now start the python magic
#  |   setup (name = "nice_plugin",
#  |          version = '0.1',
#  |          description = "My first plugin",
#  |          author = "me",
#  |          author_email = "my@mail.address",
#  |          url = "http://i-also-have-a-web.address",
#  |   
#  |          package_dir = package_dir,
#  |          packages    = packages,
#  |          data_files  = data_files
#  |          )
#  |   finalize()
#
#
#  To auto-build distribution packages, a MANIFEST.in is helpfull. You should
#  create one, e.g.
#
#  |   recursive-include src *.py
#  |   recursive-include share *
#  |   include *
#
#
#  If you need help, please join the freevo developer mailing list
#
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.11  2003/11/10 18:46:09  dischi
# bugfix for freevo.pot
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


import os
import sys

try:
    import version
except:
    import freevo.version as version
    
def package_finder(result, dirname, names):
    """
    os.path.walk helper for 'src'
    """
    for name in names:
        if os.path.splitext(name)[1] == '.py':
            import_name = dirname.replace('/','.').replace('..src', 'freevo')
            result[import_name] = dirname
            return result
    return result


def data_finder(result, dirname, names):
    """
    os.path.walk helper for data directories
    """
    files = []
    for name in names:
        if os.path.isfile(os.path.join(dirname, name)):
            if dirname.find('i18n') == -1 or (name.find('pot') == -1 and \
                                              name.find('update.py') == -1):
                files.append(os.path.join(dirname, name))
            
    if files and dirname.find('/CVS') == -1:
        result.append((dirname.replace('./share', 'share/freevo').
                       replace('./src/www', 'share/freevo').\
                       replace('./i18n', 'share/locale').\
                       replace('./contrib', 'share/freevo/contrib').\
                       replace('./Docs', 'share/doc/freevo-%s' % version.__version__).\
                       replace('./helpers', 'share/freevo/helpers'), files))
    return result


def docbook_finder(result, dirname, names):
    """
    os.path.walk helper for docbook data files in Docs
    """
    files = []
    for name in names:
        if os.path.splitext(name)[1] == '.html':
            files.append(os.path.join(dirname, name))
            
    if files and dirname.find('/CVS') == -1:
        result.append((dirname.replace('/html', ''). \
                       replace('./Docs', 'share/doc/freevo-%s' % version.__version__), files))
    return result


def check_libs(libs):
    """
    check for python libs installed
    """
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'install':
        # check for needed libs
        for module, url in libs:
            print 'checking for %-13s' % (module+'...'),
            try:
                exec('import %s' % module)
                print 'found'
            except:
                print 'not found'
                print 'please download it from %s and install it' % url
                sys.exit(1)
            

def i18n(application):
    """
    i18n cmd support
    """
    global use_i18n
    use_i18n = 1

    # cmd == '18n'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'i18n':
        if len(sys.argv) > 2 and sys.argv[2].lower() == '--help':
            print 'Updates the i18n translation. This includes generating the pot'
            print 'file, merging the pot file into the po files and generate the'
            print 'mo files from them.'
            print
            print 'Options for \'i18n\' command:'
            print '  --no-merge     don\'t merge pot file into po files'
            print
            sys.exit(0)
            
        # arg i18n will update the pot file and maybe merge the po files
        print 'updating pot file'

        # for freevo main package: remember the skin settings
        if application == 'freevo':
            f = open('i18n/freevo.pot')
            fxd_strings = []
            add = 0
            for line in f.readlines():
                if line.find('Manualy added from fxd skin files') > 0:
                    add = 1
                if add:
                    fxd_strings.append(line)
            f.close()

        os.system('(cd src ; find . -name \*.py | xargs xgettext -o ../i18n/%s.pot)' % \
                  application)

        # for freevo main package: restore the skin settings
        if application == 'freevo':
            f = open('i18n/freevo.pot', 'a')
            for line in fxd_strings:
                f.write(line)
            f.close()

        # if arg 2 is not --no-merge to the merge
        if not (len(sys.argv) > 2 and sys.argv[2] == '--no-merge'):
            for file in ([ os.path.join('i18n', fname) for fname in os.listdir('i18n') ]):
                if os.path.isdir(file) and file.find('CVS') == -1:
                    print 'updating %s...' % file,
                    sys.stdout.flush()
                    file = os.path.join(file, 'LC_MESSAGES/%s.po' % application)
                    os.system('msgmerge --update --backup=off %s i18n/%s.pot' % \
                              (file, application))
            print

    # do not run this function if --help is given
    for a in sys.argv:
        if a.lower() == '--help':
            return

    # generate mo files for 'i18n', 'sdist' and 'bdist_rpm'
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('i18n', 'sdist', 'bdist_rpm'):
        # update the mo files
        print 'updating mo files'
        for file in ([ os.path.join('i18n', fname) for fname in os.listdir('i18n') ]):
            if os.path.isdir(file) and file.find('CVS') == -1:
                file = os.path.join(file, 'LC_MESSAGES/%s.po' % application)
                mo = os.path.splitext(file)[0] + '.mo'
                os.system('msgfmt -o %s %s' % (mo, file))

    # exit for cmd == 'i18n'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'i18n':
        sys.exit(0)



def finalize():
    """
    some stuff after setup is finished
    """
    global use_i18n
    if use_i18n and len(sys.argv) > 1 and sys.argv[1].lower() == '--help-commands':
        print 'Special Commands for Freevo:'
        print '  i18n             i18n help functions'
        print


        
# use i18n command option
use_i18n = 0

# create list of source files
package_dir = {}

os.path.walk('./src', package_finder, package_dir)
packages = []
for p in package_dir:
    packages.append(p)

# create list of data files (share)
data_files = []
os.path.walk('./share', data_finder, data_files)
os.path.walk('./contrib/fbcon', data_finder, data_files)
os.path.walk('./contrib/xmltv', data_finder, data_files)
os.path.walk('./src/www/htdocs', data_finder, data_files)
os.path.walk('./i18n', data_finder, data_files)

