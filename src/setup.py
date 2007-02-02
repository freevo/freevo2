# -*- coding: iso-8859-1 -*-
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
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file doc/CREDITS for a complete list of authors.
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
import getopt
import string

# For Internationalization purpose
import freevo.conf

CONFIG_VERSION = 2.1

# Help text
def print_usage():
    usage = _('''\
Usage: ./freevo setup [OPTION]...
Set up Freevo for your specific environment.

   --geometry=WIDTHxHEIGHT      set the display size
                                  WIDTHxHEIGHT can be 800x600, 768x576 or 640x480

   --display=DISP               set the display
                                  DISP can be x11, fbdev, mga, 
                                  directfb or dfbmga
                                  
   --tv=NORM                    set the TV standard
                                  NORM can be ntsc, pal or secam

   --help                       display this help and exit

The default is "--geometry=800x600 --display=x11 --tv=ntsc"
Please report bugs to <freevo-users@lists.sourceforge.net>.
''')

    print usage
    
    
class Struct(object):
    pass



def check_config(conf):
    vals_geometry = ['800x600', '768x576', '640x480']
    vals_display = ['x11', 'fbdev', 'directfb', 'dfbmga', 'mga']
    vals_tv = ['ntsc', 'pal', 'secam']

    if not conf.geometry in vals_geometry:
        print 'geometry must be one of: %s' % ' '.join(vals_geometry)
        sys.exit(1)
        
    if not conf.display in vals_display:
        print 'display must be one of: %s' % ' '.join(vals_display)
        sys.exit(1)
        
    if not conf.tv in vals_tv:
        print 'tv must be one of: %s' % ' '.join(vals_tv)
        sys.exit(1)
        

def create_config(conf):
    
    outfile='/etc/freevo/freevo.conf'
    try:
        fd = open(outfile, 'w')
    except:
        if not os.path.isdir(os.path.expanduser('~/.freevo')):
            os.mkdir(os.path.expanduser('~/.freevo'))
        outfile=os.path.expanduser('~/.freevo/freevo.conf')
        fd = open(outfile, 'w')
        
    for val in dir(conf):
        if val[0:2] == '__': continue

        # Some Python magic to get all members of the struct
        fd.write('%s = %s\n' % (val, conf.__dict__[val]))
        
    print
    print 'wrote %s' % outfile


def run_as_main():
    # Default opts

    # XXX Make this OO and also use the Optik lib
    conf = Struct()
    conf.geometry = '800x600'
    conf.display = 'x11'
    conf.tv = 'ntsc'
    conf.version = CONFIG_VERSION

    # Parse commandline options
    try:
        long_opts = 'help compile= geometry= display= tv= '.split()
        opts, args = getopt.getopt(sys.argv[2:], 'h', long_opts)
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


    check_config(conf)

    # set geometry for display/tv combinations without a choice
    if conf.display in ( 'directfb', 'dfbmga' ):
        if conf.tv == 'ntsc':
            conf.geometry = '720x480'
        else:
            conf.geometry = '720x576'

    print
    print
    print _('Settings:')
    print '  %20s = %s' % ('geometry', conf.geometry)
    print '  %20s = %s' % ('display', conf.display)
    print '  %20s = %s' % ('tv', conf.tv)


    # Build everything
    create_config(conf)
    print
    
    sys.exit()
