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
# Revision 1.12  2002/08/21 05:07:59  krister
# Moved Makefile.in to Makefile.
#
# Revision 1.11  2002/08/21 04:58:26  krister
# Massive changes! Obsoleted all osd_server stuff. Moved vtrelease and matrox stuff to a new dir fbcon. Updated source to use only the SDL OSD which was moved to osd.py. Changed the default TV viewing app to mplayer_tv.py. Changed configure/setup_build.py/config.py/freevo_config.py to generate and use a plain-text config file called freevo.conf. Updated docs. Changed mplayer to use -vo null when playing music. Fixed a bug in music playing when the top dir was empty.
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



# Help text
usage = """\
Usage: ./configure [OPTION]...
Configure Freevo for your specific environment.

   --geometry=WIDTHxHEIGHT      set the display size
                                  WIDTHxHEIGHT can be 800x600 or 768x576

   --display=DISP               set the display
                                  DISP can be xv, x11, fbdev, mga
                                  
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
"""

def print_usage():
    print usage
    
    
class Struct:
    pass


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
        long_opts = 'help geometry= display= tv= chanlist='.split()
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
            conf.norm = a

        if o == '--chanlist':
            conf.chanlist = a


    print 'Settings:'
    print '  %20s = %s' % ('geometry', conf.geometry)
    print '  %20s = %s' % ('display', conf.display)
    print '  %20s = %s' % ('tv', conf.tv)
    print '  %20s = %s' % ('chanlist', conf.chanlist)

    check_config(conf)

    # Build everything
    create_config(conf)
    
    print
    print 'Now you can type "make" to build freevo. It can be run from here,'
    print 'just type "freevo" to start it.'
    print
    print 'Do "make install" as root to put the binaries into /usr/local/freevo'
    print

    sys.exit()

vals_geometry = ['800x600', '768x576']
vals_display = ['xv', 'x11', 'fbdev', 'mga']
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
    # Backup all old config files
    for i in range(9, 0, -1):
        os.system('mv freevo.conf.%s freevo.conf.%s &> /dev/null' % (i, i+1))
        
    os.system('mv freevo.conf freevo.conf.1 &> /dev/null')
    
    print 'Creating freevo.conf...',

    fd = open('freevo.conf', 'w')
    for val in dir(conf):
        if val[0:2] == '__': continue

        # Some Python magic to get all members of the struct
        fd.write('%s = %s\n' % (val, conf.__dict__[val]))
        
    print 'done'
    

if __name__ == '__main__':
    main()
