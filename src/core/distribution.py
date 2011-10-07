# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# distribution.py - Freevo distribution script for setup.py
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
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
import os
import sys

from distutils import core
from distutils.command import install_lib

Extension = core.Extension
VERSION   = '2.0'

DATA_MAPPING = [ ('./share', 'share/freevo2'),
                 ('./i18n', 'share/locale'),
                 ('./doc', 'share/doc/freevo-%s' % VERSION) ]

def package_finder((result, module), dirname, names):
    """
    os.path.walk helper for 'src'
    """
    for name in names:
        if os.path.splitext(name)[1] == '.py':
            import_name = dirname.replace('/','.')
            if not import_name:
                import_name = '.'
            import_name = 'freevo.%s%s' % (module, import_name[5:])
            result[import_name] = dirname
            return result
    return result


def data_finder(result, dirname, names):
    """
    os.path.walk helper for data directories
    """
    if dirname.endswith('.svn') or dirname.find('/.svn/') > 0:
        return result
    files = []
    for name in names:
        if os.path.isfile(os.path.join(dirname, name)):
            if dirname.find('i18n') == -1 or \
                   (name.find('pot') == -1 and name.find('update.py') == -1):
                files.append(os.path.join(dirname, name))
    if files:
        for mapping in DATA_MAPPING:
            dirname = dirname.replace(*mapping)
        result.append((dirname, files))
    return result


def i18n_mo(app):
    print 'updating mo files'
    for file in ([ os.path.join('i18n', fname) for \
                   fname in os.listdir('i18n') ]):
        if os.path.isdir(file) and not file.endswith('.svn'):
            file = os.path.join(file, 'LC_MESSAGES/%s.po' % app)
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

            # # for freevo main package: get the skin settings
            # fxd_strings = {}
            # if self.app == 'freevo':
            #     for file in ([ os.path.join('share/skins/main', fname)
            #                    for fname in os.listdir('share/skins/main') ]):
            #         if not file.endswith('.fxd'):
            #             continue
            #         f = open(file)
            #         data = f.readlines()
            #         f.close()
            #         for i in range(len(data)):
            #             # find main menu names
            #             if 0 < data[i].find('<item label') < \
            #                    data[i].find('name'):
            #                 text = data[i][data[i].find('name="')+6:]
            #                 text = text[:text.find('"')]
            #                 if fxd_strings.has_key(text):
            #                     fxd_strings[text].append('%s:%s' % (file, i))
            #                 else:
            #                     fxd_strings[text] = [ '%s:%s' % (file, i) ]
            #                 continue

            #             # find <text></text>
            #             if data[i][:-1].find('<text') == -1:
            #                 continue
            #             text = data[i][:-1]
            #             if data[i][:-1].find('>') == -1:
            #                 text += data[i+1][:-1]
            #             if text.find('/>') > 0 or text.find('</text>') == -1:
            #                 continue
            #             text = text[text.find('>')+1:text.find('</text>')]
            #             if not text.strip(' /():-_"\'') or text == 'x':
            #                 continue

            #             # strip ' ' at the beginnig and ' ', ': ', ':',
            #             # ',' or ', ' at the end
            #             text = text.strip(' ').rstrip(' :,')

            #             if fxd_strings.has_key(text):
            #                 fxd_strings[text].append('%s:%s' % (file, i))
            #             else:
            #                 fxd_strings[text] = [ '%s:%s' % (file, i) ]

            # # update
            # if os.path.isfile('freevo_config.py'):
            #     freevo_config = '../freevo_config.py'
            # else:
            #     freevo_config = ''
            # os.system('(cd src ; find . -name "*.*py" | xargs xgettext -L ' + \
            #           'Python -o ../i18n/%s.pot %s)' % \
            #           (self.app, freevo_config))

            # # for freevo main package: check skin
            # if self.app == 'freevo':
            #     # load pot file into mem
            #     f = open('i18n/freevo.pot')
            #     data = f.readlines()
            #     f.close()

            #     # search for duplicates from freevo.pot and skin
            #     f = open('i18n/freevo.pot', 'w')
            #     for line in data:
            #         if line.find('msgid "') == 0:
            #             text = line[line.find('"')+1:line.rfind('"')]
            #             if text in fxd_strings:
            #                 for found in fxd_strings[text]:
            #                     f.write('#: %s\n' % found)
            #                 del fxd_strings[text]
            #         f.write(line)

            #     # write skin strings
            #     for text in fxd_strings:
            #         f.write('\n')
            #         for line in fxd_strings[text]:
            #             f.write('#: %s\n' % line)
            #         f.write('msgid "%s"\nmsgstr ""\n' % text)
            #     f.close()

        if not self.no_merge and not self.compile_only:
            print 'updating po files'
            print '',
            # for file in ([ os.path.join('i18n', fname) \
            #                for fname in os.listdir('i18n') ]):
            #     if os.path.isdir(file) and not file.endswith('.svn'):
            #         txt = file
            #         for i in range(len(file), 10):
            #             txt += '.'
            #         print txt,
            #         sys.stdout.flush()
            #         file = os.path.join(file, 'LC_MESSAGES/%s.po' % self.app)
            #         os.system('msgmerge --update --backup=off %s i18n/%s.pot'\
            #                   % (file, self.app))
            print

        # po to mo conversion
        i18n_mo(self.app)


class freevo_install_lib (install_lib.install_lib):
    def install (self):
        if os.path.isdir(self.build_dir):
            # remove __init__.py which will override the normal Freevo files
            for i in [ 'plugins', 'plugins/idlebar', 'video/plugins',
                       'audio/plugins', 'image/plugins', 'tv/plugins',
                       'skins/plugins', 'helpers']:
                init = os.path.join(self.build_dir, 'freevo', i, '__init__.py')
                if os.path.isfile(init):
                    os.remove(init)
        install_lib.install_lib.install(self)


def setup(**attrs):
    for i in ('name', 'version'):
        if not attrs.has_key(i):
            raise AttributeError('%s is missing', i)

    for i in ('description', 'author', 'author_email', 'url'):
        if not attrs.has_key(i):
            attrs[i] = ''

    if not 'data_files' in attrs:
        attrs['data_files'] = []

    if not 'module' in attrs:
        attrs['module'] = 'ui'

    if not 'cmdclass' in attrs:
        attrs['cmdclass'] = {}

    # FIXME: handle plugins
    # if not attrs.has_key('i18n') or attrs['i18n'] != 'freevo':
    # # this is a plugin, replace the cmdclass install_lib
    # cmdclass['install_lib'] = freevo_install_lib

    if os.path.isdir('i18n'):
        i18n.app = attrs['name']
        attrs['cmdclass']['i18n'] = i18n
        if len(sys.argv) > 1 and sys.argv[1].lower() in ('sdist', 'bdist_rpm'):
            for i in sys.argv:
                if i.find('--help') != -1:
                    break
            else:
                i18n_mo(attrs['name'])

    # create list of source files
    if not 'package_dir' in attrs:
        package_dir = {}
        os.path.walk('./src', package_finder, (package_dir, attrs['module']))
        attrs['package_dir'] = package_dir

    # create list of data files (share)
    data_files = []
    os.path.walk('./share', data_finder, data_files)
    os.path.walk('./i18n', data_finder, data_files)
    os.path.walk('./doc', data_finder, data_files)

    scripts = []
    if os.path.isdir('bin'):
        for script in os.listdir('bin'):
            if not script.startswith('.'):
                scripts.append('bin/%s' % script)

    core.setup(
        name         = attrs['name'],
        version      = attrs['version'],
        description  = attrs['description'],
        author       = attrs['author'],
        author_email = attrs['author_email'],
        url          = attrs['url'],

        scripts      = scripts,
        package_dir  = attrs['package_dir'],
        packages     = attrs['package_dir'].keys()[:],
        data_files   = attrs['data_files'] + data_files,

        cmdclass     = attrs['cmdclass']
        )
