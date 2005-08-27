#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# install.py - install external plugins or themes into Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2005/08/27 15:36:20  dischi
# remove some util functions
#
# Revision 1.11  2004/10/28 19:37:40  dischi
# remove LD_PRELOAD handling
#
# Revision 1.10  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.9  2004/06/10 11:03:23  dischi
# remove runtime installing support
#
# Revision 1.8  2004/06/06 10:32:02  dischi
# protect freevo files
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


import sys
import os

# We can't import config to get the True/False builtins for older python
# versions if we don't have a runtime so we do this here.
if float(sys.version[0:3]) < 2.3:
    True  = 1
    False = 0

def mkalldir(d):
    cd = ''
    for p in d.split('/'):
        cd = os.path.join(cd, p)
        if not os.path.isdir(cd):
            os.mkdir(cd)
            
def getdirnames(dirname, softlinks=True, sort=True):
    """
    Get all subdirectories in the given directory.
    Returns a list that is case insensitive sorted.
    """
    if not dirname.endswith('/'):
        dirname += '/'

    try:
        dirnames = [ dirname + dname for dname in os.listdir(dirname) if \
                     os.path.isdir(dirname + dname) and \
                     (softlinks or not os.path.islink(dirname + dname))]
    except OSError:
        return []

    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return dirnames

    
if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
    is_local = False
    tgz = os.path.abspath(sys.argv[1])

    # check if we use an installed version of python or not
    src = os.environ['FREEVO_PYTHON'].rfind('src')
    if src >= 0 and os.environ['FREEVO_PYTHON'][src:] == 'src':
        # local version, chdir to freevo working directory
        is_local = True
        os.chdir(os.path.join(os.environ['FREEVO_PYTHON'], '..'))

    if os.path.basename(tgz).startswith('freevo-runtime-'):
        print 'please use \'python setup.py runtime\' to install a runtime'
        sys.exit(0)


    # when we have a runtime, we can include the vfs
    from util import vfs
    import __builtin__
    import util.fileops

    __builtin__.__dict__['vfs'] = vfs

    # create tmp directory
    if os.path.isdir('tmp'):
        print 'directory tmp exists, please remove it'
        sys.exit(1)
    os.mkdir('tmp')

    # unpack
    os.system('tar -zxf %s -C tmp' % tgz)

    if is_local:
        # move all files from src, share and i18n into the Freevo tree
        all_files = []
        os.path.walk('tmp', util.fileops.match_files_recursively_helper, all_files)
        for file in all_files:
            new_file = file[file[4:].find('/')+5:]
            if os.path.isfile(file) and (new_file.find('share') == 0 or
                                         new_file.find('src') == 0 or
                                         new_file.find('i18n') == 0):
                for protected in ('tv', 'audio', 'video', 'plugins',
                                  'plugins/idlebar', 'skins'):
                    if new_file == 'src/%s/__init__.py' % protected:
                        print 'skipping %s' % new_file
                        break
                    if new_file == 'src/%s/plugins/__init__.py' % protected:
                        print 'skipping %s' % new_file
                        break
                else:
                    if os.path.isfile(new_file):
                        print 'updating %s' % new_file
                    else:
                        print 'installing %s' % new_file
                    mkalldir(os.path.dirname(new_file))
                    os.rename(file, new_file)
    else:
        # check package
        d = getdirnames('tmp')
        if len(d) != 1:
            print 'package is not a freevo theme or plugin, please contact the author'
        else:
            # chdir into plugin main directory and run setup.py
            cur = os.getcwd()
            os.chdir(d[0])

            sys.argv = ['setup.py', 'install']
            execfile('setup.py')

            os.chdir(cur)

    # remove tmp directory
    util.fileops.rmrf('tmp')
    
else:
    print 'freevo install helper to install external plugins or themes into Freevo'
    print
    print 'usage freevo install file'
    print 'File needs to be a tgz containing a setup.py and the Freevo file structure'
    print
