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


# disconnect both heads
`dirname $0`/matroxset/matroxset -f /dev/fb0 -m 0 > /dev/null 2> /dev/null
`dirname $0`/matroxset/matroxset -f /dev/fb1 -m 0 > /dev/null 2> /dev/null

# swap heads
`dirname $0`/matroxset/matroxset -f /dev/fb0 -m 2 > /dev/null 2> /dev/null
`dirname $0`/matroxset/matroxset -f /dev/fb1 -m 1 > /dev/null 2> /dev/null
`dirname $0`/matroxset/matroxset -f /dev/fb0 2 2 > /dev/null 2> /dev/null

#find fbset
fbset=/usr/sbin/fbset

if [ -x /usr/bin/fbset ]; then
    fbset=/usr/bin/fbset
fi

#
# The following is a modeline for setting up NTSC on the TV output (vga 2) on 
# a matrox dual-head card.

$fbset -db fbset.db -fb /dev/fb0 "ntsc-640x480_60" > /dev/null 2> /dev/null

# Set up a regular VGA monitor on vga connector 1. 
#
# Note: I don't think it is possible to use high resolutions since the 
# hardware graphics acceleration is used for connector 2 after running 
# this script. That means that it'll be hard to run a decent X11 
# session.
$fbset -db fbset.db -fb /dev/fb1 "mon-640x480-60" > /dev/null 2> /dev/null
