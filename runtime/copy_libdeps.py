#if 0 /*
# -----------------------------------------------------------------------
# check_libdeps.py - Check dynamic lib dependencies
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/02/21 04:36:43  krister
# Bugfix for missing network libs.
#
# Revision 1.1  2003/01/24 07:19:48  krister
# New runtime
#
# Revision 1.2  2002/08/14 04:33:54  krister
# Made more C-compatible.
#
# Revision 1.1  2002/08/03 07:59:15  krister
# Proposal for new standard fileheader.
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
import sys
import glob
import commands


def main():
    '''Build a list of all dll dependencies, copy stripped versions to dll/

    Dependencies are found in the directory lib (Python with installed
    modules), and apps (Freevo applications).

    The "preloads" file is also generated.
    '''

    libdeps = {}
    check_dir('lib', libdeps)
    check_dir('apps', libdeps)

    extra_libs = ['/lib/libnss_files.so.2',
                  '/lib/libnss_dns.so.2'] # These are not autodetected
    for extra_lib in extra_libs:
        libdeps[extra_lib] = 1
        check_lib(extra_lib, libdeps)

    print
    print 'Found library dependencies:'
    preloads = []
    deplist = libdeps.keys()
    for dep in deplist:
        print dep
        os.system('cp -i %s dll/' % dep)
        os.system('chmod +w dll/%s' % os.path.basename(dep))
        os.system('chmod ugo+rx dll/%s' % os.path.basename(dep))
        os.system('strip dll/%s' % os.path.basename(dep))
        pre_str = './runtime/dll/%s' % os.path.basename(dep)
        if pre_str.find('ld-linux') == -1:
            preloads.append(pre_str)

    # Generate the preloads file
    preloads_str = ' '.join(preloads)
    fd = open('preloads', 'w')
    fd.write(preloads_str + '\n')
    fd.close()
    
    return


def check_dir(dirname, libdeps, level=0):
    '''Recursively build a list of all dll deps starting in a given folder'''

    # Get all files in this directory
    filenames = os.listdir(dirname)

    print ' ' * level*2, 'Checking dir %s' % dirname
    
    subdirs = []
    for filename in filenames:
        full_name = os.path.join(dirname, filename)
        if os.path.isdir(full_name):
            subdirs.append(full_name)
        elif not os.path.islink(full_name) and os.path.isfile(full_name):
            if full_name.endswith('.so'):
                print ' ' * (level*2+1), 'Found lib %s' % full_name
                check_lib(full_name, libdeps, level=level*2+2)
            elif os.stat(full_name).st_mode & 0111:
                if not full_name.endswith('.py'):
                    # This is an executable
                    print ' ' * (level*2+1), 'Found app %s' % full_name
                    check_lib(full_name, libdeps, level=level*2+2)

    for subdir in subdirs:
        check_dir(subdir, libdeps, level=level+1)


def check_lib(filename, libdeps, level=0):
    '''Recursively check the dependencies for a dyn. lib/app

    The filename is the relative or absolute path to the lib/app file
    '''

    deps = get_deps(filename)

    for dep in deps:
        print ' ' * (level*2+1), dep,
        if dep not in libdeps:
            print 'NEW'
            libdeps[dep] = 1
            check_lib(dep, libdeps, level=level+1)
        else:
            print 'seen'
    
    return


def get_deps(filename):
    '''Run ldd on a dynamic link lib/app and return a list of the dependencies.'''

    deps = []
    (exitstatus, outtext) = commands.getstatusoutput('ldd %s' % filename)
    if not exitstatus:
        lines = outtext.split('\n')
        for line in lines:
            # Must have a '=>' string to be a dependency
            if line.find('=>') == -1:
                continue
            dep = line.strip().split()[2]
            deps.append(dep)

    return deps

    
if __name__ == '__main__':
    main()
    
