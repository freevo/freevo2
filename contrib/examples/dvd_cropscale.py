#if 0 /*
# -----------------------------------------------------------------------
# dvd_cropscale.py - Calculate crop and scale params for DVD backups
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/08/23 09:50:59  dischi
# *** empty log message ***
#
# Revision 1.1  2003/01/22 01:50:46  krister
# This app runs mplayer on a DVD to calculate crop/scale params.
#
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
#endif


import os
import sys
import commands
import re


def main():

    # The DVD title is 1 by default, or can be given as the first argument
    title = 1
    if len(sys.argv) >= 2:
        title = int(sys.argv[1])

    # The test clip position is 0:15:0 by default, or can be given as the second argument
    pos = '0:15:00'
    if len(sys.argv) >= 3:
        pos = sys.argv[2]

    cmd = 'mplayer -quiet -dvd %s -vo null -ao null -vop cropdetect -frames 30 -ss %s 2> /dev/null' % (title, pos)
    status, output = commands.getstatusoutput(cmd)

    if status:
        print 'Error:', status
        sys.exit()

    # Parsed settings
    aspect = None
    crop = None
    
    lines = output.split('\n')
    for line in lines:

        # Check for base geometry
        m = re.match(r'VIDEO:\s+MPEG2\s+(\d+)x(\d+)\s+\(aspect (\d)\).*', line)
        if m and m.groups()[:2] != ('720', '480'):
            print 'Can only handle base geometry 720x480! Got %s)' % m.groups()[:2]
            sys.exit()
        elif m:
            # Aspect 0=1.33, 3=1.78
            if m.groups()[2] == '2':
                aspect = 1.33
            else:
                aspect = 1.78

        # Check for crop results
        m = re.match(r'[^(]+\(-vop crop=(\d+):(\d+):(\d+):(\d+)\).*', line)
        if m:
            # Is this the largest crop setting so far?
            w, h, x0, y0 = map(lambda s: int(s), m.groups())
            if not crop or (w, h, x0, y0) > crop:
                crop = w, h, x0, y0


    print 'Aspect: %s' % aspect
    print 'Cropvals: %s' % list(crop)
    print

    w, h, x0, y0 = crop

    # Calculate number of lines (=height=y) as the closest lower number
    # divisible by 16
    new_h = (h / 16) * 16

    # New start line
    new_y0 = y0 + (h - new_h) / 2

    # Ok, now we got the crop values. Calculate the scaling so that
    # the aspect ratio is correct, and the number of pixels on the line
    # is divisible by 16.
    
    # Scaling. The aspect on the disc is 1.5 (720/480), correct for that.
    scale_x = aspect / 1.5
    new_w = w * scale_x

    # Adjust to the closest modulo 16
    new_w = int(round(new_w / 16.0) * 16)

    args = (new_w, new_h, w, new_h, x0, new_y0)
    print 'Settings: -vop scale=%s:%s,crop=%s:%s:%s:%s' % args

    print 'Original aspect = %1.2f, new = %1.2f' % (aspect, (float(new_w) / new_h) )
    
            

if __name__ == '__main__':
    main()
