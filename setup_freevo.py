#if 0 /*
# -----------------------------------------------------------------------
# setup_freevo.py - Autoconfigure Freevo
#
# This is an application that is executed by the "./freevo" script
# after checking for python.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/06/20 01:50:14  rshortt
# Look for xmame.x11 as well, but override with xmame.SDL.  Changed xmame_SDL
# to just xmame.
#
# Revision 1.3  2003/04/24 19:58:20  dischi
# comment cleanup for 1.3.2-pre4
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

import sys
import os
import getopt
import string

CONFIG_VERSION = 1.0

# Help text
usage = '''\
Usage: ./freevo setup [OPTION]...
Set up Freevo for your specific environment.

   --geometry=WIDTHxHEIGHT      set the display size
                                  WIDTHxHEIGHT can be 800x600, 768x576 or 640x480

   --display=DISP               set the display
                                  DISP can be x11, fbdev, dxr3, mga, dfbmga or sdl
                                  
   --tv=NORM                    set the TV standard
                                  NORM can be ntsc, pal or secam

   --chanlist=LIST              set the channel list
                                  LIST can be us-bcast, us-cable, us-cable-hrc,
                                  japan-bcast, japan-cable, europe-west,
                                  europe-east, italy, newzealand, australia,
                                  ireland, france, china-bcast, southafrica,
                                  argentina, canada-cable

   --sysfirst                   look in the system path for applications before checking
                                ./runtime/apps.

   --help                       display this help and exit

The default is "--geometry=800x600 --display=x11 --tv=ntsc --chanlist=us-cable"
Please report bugs to <freevo-users@lists.sourceforge.net>.
'''

def print_usage():
    print usage
    
    
class Struct:
    pass



def match_files_recursively_helper(result, dirname, names):
    if dirname == '.' or dirname[:5].upper() == './WIP':
        return result
    for name in names:
        if os.path.splitext(name)[1].lower()[1:] == 'py':
            fullpath = os.path.join(dirname, name)
            result.append(fullpath)
    return result


def main():
    # Default opts

    # XXX Make this OO and also use the Optik lib
    conf = Struct()
    conf.geometry = '800x600'
    conf.display = 'x11'
    conf.tv = 'ntsc'
    conf.chanlist = 'us-cable'
    conf.version = CONFIG_VERSION
    sysfirst = 0 # Check the system path for apps first, then the runtime
    
    # Parse commandline options
    try:
        long_opts = 'help compile= geometry= display= tv= chanlist= sysfirst'.split()
        opts, args = getopt.getopt(sys.argv[1:], 'h', long_opts)
    except getopt.GetoptError:
        # print help information and exit:
        print_usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_usage()
            sys.exit()
            
        if o == '--geometry':
            conf.geometry = a

        if o == '--display':
            conf.display = a

        if o == '--tv':
            conf.tv = a

        if o == '--chanlist':
            conf.chanlist = a

        if o == '--sysfirst':
            sysfirst = 1

        # this is called by the Makefile, don't call it directly
        if o == '--compile':
            # Compile python files:
            import distutils.util
            try:
                optimize=min(int(a[0]),2)
                prefix=a[2:]
            except:
                sys.exit(1)

            files = []
            os.path.walk('.', match_files_recursively_helper, files)
            distutils.util.byte_compile(files, prefix='.', base_dir=prefix,
                                        optimize=optimize)
            sys.exit(0)


    print 'System path first=%s' % ( ['NO','YES'][sysfirst])
    
    check_program(conf, "mplayer", "mplayer", 1, sysfirst)
    check_program(conf, "jpegtran", "jpegtran", 0, sysfirst)
    check_program(conf, "xmame.x11", "xmame", 0, sysfirst)
    check_program(conf, "xmame.SDL", "xmame", 0, sysfirst)
    check_program(conf, "ssnes9x", "snes", 0, sysfirst)
    check_program(conf, "zsnes", "snes", 0, sysfirst)

    check_config(conf)

    # set geometry for display/tv combinations without a choice
    if conf.display == 'dfbmga':
        if conf.tv == 'ntsc':
            conf.geometry = '720x480'
        else:
            conf.geometry = '720x576'

    print
    print
    print 'Settings:'
    print '  %20s = %s' % ('geometry', conf.geometry)
    print '  %20s = %s' % ('display', conf.display)
    print '  %20s = %s' % ('tv', conf.tv)
    print '  %20s = %s' % ('chanlist', conf.chanlist)


    # Build everything
    create_config(conf)

    print
    print 'Now you can type "freevo" to run freevo if you have the full '
    print 'binary release.'
    print
    print 'Please read the manual on how to build the CVS/src Freevo version.'
    print
    print 'Do "make install" as root to install the binaries in /usr/local/freevo'
    print

    sys.exit()

vals_geometry = ['800x600', '768x576', '640x480']
vals_display = ['x11', 'fbdev', 'dfbmga', 'mga', 'dxr3', 'sdl']
vals_tv = ['ntsc', 'pal', 'secam']
vals_chanlist = ['us-bcast', 'us-cable', 'us-cable-hrc',
                 'japan-bcast', 'japan-cable', 'europe-west',
                 'europe-east', 'italy', 'newzealand', 'australia',
                 'ireland', 'france', 'china-bcast', 'southafrica',
                 'argentina', 'canada-cable']

def check_config(conf):
    if not conf.geometry in vals_geometry:
        print 'geometry must be one of: %s' % ' '.join(vals_geometry)
        sys.exit(1)
        
    if not conf.display in vals_display:
        print 'display must be one of: %s' % ' '.join(vals_display)
        sys.exit(1)
        
    if not conf.tv in vals_tv:
        print 'tv must be one of: %s' % ' '.join(vals_tv)
        sys.exit(1)
        
    if not conf.chanlist in vals_chanlist:
        print 'chanlist must be one of: %s' % ' '.join(vals_chanlist)
        sys.exit(1)
        

def create_config(conf):
    
    print 'Creating freevo.conf...',

    fd = open('freevo.conf', 'w')
    for val in dir(conf):
        if val[0:2] == '__': continue

        # Some Python magic to get all members of the struct
        fd.write('%s = %s\n' % (val, conf.__dict__[val]))
        
    print 'done'


def check_program(conf, name, variable, necessary, sysfirst):

    # Check for programs both in the path and the runtime apps dir
    search_dirs_runtime = ['./runtime/apps', './runtime/apps/mplayer']
    if sysfirst:
        search_dirs = os.environ['PATH'].split(':') + search_dirs_runtime
    else:
        search_dirs = search_dirs_runtime + os.environ['PATH'].split(':')
        
    print 'checking for %-13s' % (name+'...'),

    for dirname in search_dirs:
        filename = os.path.join(dirname, name)
        if os.path.exists(filename) and os.path.isfile(filename):
            print filename
            conf.__dict__[variable] = filename
            break
    else:
        if necessary:
            print "********************************************************************"
            print "ERROR: can't find %s" % name
            print "Please install the application respectively put it in your path."
            print "Freevo won't work without it."
            print "********************************************************************"
            print
            print
            sys.exit(1)
        else:
            print "not found (deactivated)"

if __name__ == '__main__':
    main()
