#!/bin/sh

#
# This script is a mix from the mplayer TVout scripts and some
# changes by me to support 768 width
#
# Note: fbset and matroxset are copied from mplayer! They're 
# included here for ease of use, but check out the mplayer
# source for updates if you have problems. There are more
# init scripts there, setup utilities, etc.
#
# /Dischi


# I don't want this is doing exacly, but it should enable the
# clone mode with IMHO looks better than the others

`dirname $0`/matroxset/matroxset -f /dev/fb1 -m 0
`dirname $0`/matroxset/matroxset -f /dev/fb0 -m 3

# switch to PAL
`dirname $0`/matroxset/matroxset 1

# set the 768x576 output
/usr/sbin/fbset -fb /dev/fb0 -depth 32 -left 23 -right -5 -upper 39 -lower 10 \
    -hslen 46 -vslen 4 -xres 768 -yres 576 -vxres 768 -vyres 576 -depth 32 \
    -laced false -bcast true


setterm -blank 0
