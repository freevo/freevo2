#if 0 /*
# -----------------------------------------------------------------------
# setup_build.py - Autoconfigure Freevo
#
# This is an application that is executed by the "./configure" script
# after checking for python.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.29  2003/02/05 15:22:51  krister
# Updated build stuff, Changelog
#
# Revision 1.28  2003/02/05 06:05:21  krister
# Removed the backup of old config files, they just clutter the folder
#
# Revision 1.27  2003/02/04 13:07:16  dischi
# setip_build can now compile python files. This is used by the Makefile
# (make all). The Makefile now also has the directories as variables.
#
# Revision 1.26  2003/01/31 02:08:59  krister
# Changed the X11 display option to automatically select between xv,x11,etc.
#
# Revision 1.25  2003/01/28 03:46:02  krister
# Fixed a bug in application checking.
#
# Revision 1.24  2003/01/24 07:25:23  krister
# Added check for apps in the runtime/apps dir.
#
# Revision 1.23  2002/12/21 17:26:52  dischi
# Added dfbmga support. This includes configure option, some special
# settings for mplayer and extra overscan variables
#
# Revision 1.22  2002/12/09 14:23:53  dischi
# Added games patch from Rob Shortt to use the interface.py and snes support
#
# Revision 1.21  2002/10/24 03:16:18  krister
# Added DXR3 support.
#
# Revision 1.20  2002/10/17 04:16:16  krister
# Changed the 'nice' command so that it is built into runapp instead. Made default prio -20.
#
# Revision 1.19  2002/10/06 14:42:40  dischi
# log message cleanup
#
# Revision 1.18  2002/09/23 18:02:38  dischi
# Added check if the new configure was started
#
# Revision 1.17  2002/09/23 16:53:33  dischi
# check mplayer, nice, jpegtrans and xmame.SDL in configure
#
# Revision 1.16  2002/09/06 05:18:52  krister
# Added a 640x480 mode. Have not adapted the skin yet.
#
# Revision 1.2  2002/08/14 04:33:54  krister
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


# Help text
usage = '''\
Usage: ./configure [OPTION]...
Configure Freevo for your specific environment.

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
    
    # Parse commandline options
    try:
        long_opts = 'help compile= geometry= display= tv= chanlist='.split()
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


    check_program(conf, "mplayer", "mplayer", 1)
    check_program(conf, "jpegtran", "jpegtran", 0)
    check_program(conf, "xmame.SDL", "xmame_SDL", 0)
    check_program(conf, "ssnes9x", "snes", 0)
    check_program(conf, "zsnes", "snes", 0)

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
    print 'If you only downloaded the source package you need to compile it,'
    print 'type "make" to build freevo.'
    print
    print 'Do "make install" as root to put the binaries into /usr/local/freevo'
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


def check_program(conf, name, variable, necessary):

    # Check for programs both in the path and the runtime apps dir
    search_dirs = os.environ['PATH'].split(':')
    search_dirs.append('./runtime/apps')
    search_dirs.append('./runtime/apps/mplayer')

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
