#!/bin/sh

# This is a modified version of the mga_pal_768x576 script fitted
# with the updated parameters for pal. Works better than the existing pal
# script for me - den_RDC

# I don't want this is doing exacly, but it should enable the
# clone mode with IMHO looks better than the others

`dirname $0`/matroxset/matroxset -f /dev/fb1 -m 0
`dirname $0`/matroxset/matroxset -f /dev/fb0 -m 3

# switch to PAL
`dirname $0`/matroxset/matroxset 1

#find fbset
fbset=/usr/sbin/fbset

if [ -x /usr/bin/fbset ]; then
    fbset=/usr/bin/fbset
fi

#
# This should do the right thing (it gives a perfect fit on my TV)
#

$fbset -fb /dev/fb0 -depth 32 -left 48 -right 24 -upper 70 -lower 32\
   -hslen 40 -vslen 2 -xres 800 -yres 600 -vxres 800 -vyres 600 -depth 32\
   -laced false -bcast true

