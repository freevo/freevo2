#!/bin/sh

#
# This script was posted on the mplayer-matrox mailing list by
# Brian Hall, http://www.bigfoot.com/~brihall
#
# Note: fbset and matroxset are copied from mplayer! They're 
# included here for ease of use, but check out the mplayer
# source for updates if you have problems. There are more
# init scripts there, setup utilities, etc.
#
# XXX I have not tested this with a monitor on vga-connector 1,
# I'm only using a TV on vga-connector 2
# /Krister

# goto the matrox_g400 dir
cd `dirname $0`

./fbset/fbset -fb /dev/fb0 > /dev/null 2> /dev/null
./fbset/fbset -fb /dev/fb1 > /dev/null 2> /dev/null

# disconnect both heads
./matroxset/matroxset -f /dev/fb0 -m 0 > /dev/null 2> /dev/null
./matroxset/matroxset -f /dev/fb1 -m 0 > /dev/null 2> /dev/null

# swap heads
./matroxset/matroxset -f /dev/fb0 -m 2 > /dev/null 2> /dev/null
./matroxset/matroxset -f /dev/fb1 -m 1 > /dev/null 2> /dev/null
./matroxset/matroxset -f /dev/fb0 2 2 > /dev/null 2> /dev/null

#
# The following is a modeline for setting up NTSC on the TV output (vga 2) on 
# a matrox dual-head card.
#

./fbset/fbset -db fbset.db -fb /dev/fb0 "ntsc-800x600" > /dev/null 2> /dev/null

#
# Set up a regular VGA monitor on vga connector 1. 
#
# Note: I don't think it is possible to use high resolutions since the 
# hardware graphics acceleration is used for connector 2 after running 
# this script. That means that it'll be hard to run a decent X11 
# session.
./fbset/fbset -db fbset.db -fb /dev/fb1 "640x480-60" > /dev/null 2> /dev/null
