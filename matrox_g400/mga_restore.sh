#! /bin/sh

# This script should restore the settings for the MGA dualhead
# adapter so that the graphics accelerator is set for VGA connector 1,
# where a monitor is normally attached.
# It is used if your computer is hooked up to both a monitor and the TV.

# Note: This is copied from mplayer! Check out the mplayer
# source for updates if you have problems. There are more
# init scripts there, setup utilities, etc.
#
# XXX I have not tested this with a monitor on vga-connector 1,
# I'm only using a TV on vga-connector 2
# /Krister

if [ -c /dev/fb0 ]; then
  HEAD0=/dev/fb0
  HEAD1=/dev/fb1
else
  HEAD0=/dev/fb/0
  HEAD1=/dev/fb/1
fi

./matroxset/matroxset -f ${HEAD1} -m 0
./matroxset/matroxset -f ${HEAD0} -m 1
./matroxset/matroxset -f ${HEAD1} -m 2
