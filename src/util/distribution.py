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
#  |   from freevo.util.distribution import setup
#  |   
#  |   # now start the python magic
#  |   setup (name = "nice_plugin",
#  |          version = '0.1',
#  |          description = "My first plugin",
#  |          author = "me",
#  |          author_email = "my@mail.address",
#  |          url = "http://i-also-have-a-web.address",
#  |   
#  |          i18n = 'my_app', # optional
#  |          )
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
# Revision 1.10  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.9  2004/06/10 11:06:40  dischi
# make it possible to give a cmdclass to setup
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
import re

try:
    import version
except:
    import freevo.version as version

# Get the real distutils (not the Freevo stuff)
# This is a bad hack and will be removed when the distutils.py
# is deleted inthis tree
import imp

fp, pathname, description = imp.find_module('distutils' , sys.path[1:])
distutils = imp.load_module('distutils', fp, pathname, description)

fp, pathname, description = imp.find_module('core' , distutils.__path__)
core = imp.load_module('core', fp, pathname, description)

fp, pathname, description = imp.find_module('command' , distutils.__path__)
command = imp.load_module('command', fp, pathname, description)

fp, pathname, description = imp.find_module('install_lib' , command.__path__)
install_lib = imp.load_module('install_lib', fp, pathname, description)

Extension = core.Extension


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
    # ok, this can't be done by setup it seems, so we have to do it
    # manually
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
            

i18n_application = ''

def i18n_mo():
    print 'updating mo files'
    for file in ([ os.path.join('i18n', fname) for fname in os.listdir('i18n') ]):
        if os.path.isdir(file) and file.find('CVS') == -1:
            file = os.path.join(file, 'LC_MESSAGES/%s.po' % i18n_application)
            mo = os.path.splitext(file)[0] + '.mo'
            os.system('msgfmt -o %s %s' % (mo, file))

class i18n (core.Command):

    description = "update translation files"

    user_options = [
        ('no-merge', None,
         "don't merge po files"),
        ('compile-only', None,
         "only compile po files to mo files"),
        ]

    boolean_options = [ 'no-merge', 'compile-only' ]

    help_options = []

    negative_opt = {}

    def initialize_options (self):
        self.no_merge     = 0
        self.compile_only = 0
        
    def finalize_options (self):
        pass
        
    def run (self):
        if not self.compile_only:
            print 'updating pot file'

            # for freevo main package: get the skin settings
            fxd_strings = {}
            if i18n_application == 'freevo':
                for file in ([ os.path.join('share/skins/main', fname)
                               for fname in os.listdir('share/skins/main') ]):
                    if file.endswith('.fxd'):
                        f = open(file)
                        data = f.readlines()
                        f.close()
                        for i in range(len(data)):
                            # find main menu names
                            if 0 < data[i].find('<item label') < data[i].find('name'):
                                text = data[i][data[i].find('name="')+6:]
                                text = text[:text.find('"')]
                                if fxd_strings.has_key(text):
                                    fxd_strings[text].append('%s:%s' % (file, i))
                                else:
                                    fxd_strings[text] = [ '%s:%s' % (file, i) ]
                                continue

                            # find <text></text>
                            if data[i][:-1].find('<text') == -1:
                                continue
                            text = data[i][:-1]
                            if data[i][:-1].find('>') == -1:
                                text += data[i+1][:-1]
                            if text.find('/>') > 0 or text.find('</text>') == -1:
                                continue
                            text = text[text.find('>')+1:text.find('</text>')]
                            if not text.strip(' /():-_"\'') or text == 'x':
                                continue

                            # strip ' ' at the beginnig and ' ', ': ', ':',
                            # ',' or ', ' at the end
                            text = text.strip(' ').rstrip(' :,')
                            
                            if fxd_strings.has_key(text):
                                fxd_strings[text].append('%s:%s' % (file, i))
                            else:
                                fxd_strings[text] = [ '%s:%s' % (file, i) ]

            # update
            if os.path.isfile('freevo_config.py'):
                freevo_config = '../freevo_config.py'
            else:
                freevo_config = ''
            os.system('(cd src ; find . -name "*.*py" | xargs xgettext -L ' + \
                      'Python -o ../i18n/%s.pot %s)' % (i18n_application, freevo_config))

            # for freevo main package: check skin
            if i18n_application == 'freevo':
                # load pot file into mem
                f = open('i18n/freevo.pot')
                data = f.readlines()
                f.close()

                # search for duplicates from freevo.pot and skin
                f = open('i18n/freevo.pot', 'w')
                for line in data:
                    if line.find('msgid "') == 0:
                        text = line[line.find('"')+1:line.rfind('"')]
                        if text in fxd_strings:
                            for found in fxd_strings[text]:
                                f.write('#: %s\n' % found)
                            del fxd_strings[text]
                    f.write(line)

                # write skin strings
                for text in fxd_strings:
                    f.write('\n')
                    for line in fxd_strings[text]:
                        f.write('#: %s\n' % line)
                    f.write('msgid "%s"\nmsgstr ""\n' % text)
                f.close()
             
        if not self.no_merge and not self.compile_only:
            print 'updating po files'
            print '',
            for file in ([ os.path.join('i18n', fname) for fname in os.listdir('i18n') ]):
                if os.path.isdir(file) and file.find('CVS') == -1:
                    txt = file
                    for i in range(len(file), 10):
                        txt += '.'
                    print txt,
                    sys.stdout.flush()
                    file = os.path.join(file, 'LC_MESSAGES/%s.po' % i18n_application)
                    os.system('msgmerge --update --backup=off %s i18n/%s.pot' % \
                              (file, i18n_application))
            print

        # po to mo conversion
        i18n_mo()


class freevo_install_lib (install_lib.install_lib):
    def install (self):
        if os.path.isdir(self.build_dir):
            # remove __init__.py which will override the normal Freevo files
            for i in [ 'plugins', 'plugins/idlebar', 'video/plugins', 'audio/plugins',
                       'image/plugins', 'tv/plugins', 'skins/plugins', 'helpers']:
                init = os.path.join(self.build_dir, 'freevo', i, '__init__.py')
                if os.path.isfile(init):
                    os.remove(init)
        install_lib.install_lib.install(self)

        
def setup(**attrs):
    for i in ('name', 'version', 'description', 'author', 'author_email', 'url'):
        if not attrs.has_key(i):
            attrs[i] = ''

    for i in ('scripts', 'data_files'):
        if not attrs.has_key(i):
            attrs[i] = []

    if attrs.has_key('cmdclass'):
        cmdclass = attrs['cmdclass']
    else:
        cmdclass = {}

    if not attrs.has_key('i18n') or attrs['i18n'] != 'freevo':
        # this is a plugin, replace the cmdclass install_lib
        cmdclass['install_lib'] = freevo_install_lib
    
    if attrs.has_key('i18n'):
        global i18n_application
        i18n_application = attrs['i18n']
        cmdclass['i18n'] = i18n
        if len(sys.argv) > 1 and sys.argv[1].lower() in ('sdist', 'bdist_rpm'):
            for i in sys.argv:
                if i.find('--help') != -1:
                    break
            else:
                i18n_mo()


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

    core.setup(
        name         = attrs['name'],
        version      = attrs['version'],
        description  = attrs['description'],
        author       = attrs['author'],
        author_email = attrs['author_email'],
        url          = attrs['url'],
        
        scripts      = attrs['scripts'],
        package_dir  = package_dir,
        packages     = packages,
        data_files   = attrs['data_files'] + data_files,

        cmdclass     = cmdclass
        )
    

