#!/usr/bin/env bash

# rsync-freevo
#
#   <dmeyer@tzi.de>
# $Id$

. /etc/make.conf

if [ "$PORTDIR_OVERLAY" = "" ]; then
    echo please define a PORTDIR_OVERLAY in /etc/make.conf
    echo and make sure you have the oermission to write in it
    exit 1
fi

cd /tmp
wget http://freevo.sourceforge.net/gentoo/ebuild.tgz

if [ '!' -e ebuild.tgz ]; then
    echo download failed
    exit 1
fi

cd $PORTDIR_OVERLAY

if [ '!' -e media-video ]; then
    mkdir media-video
fi

rm -rf app-misc/freevo_runtime app-misc/freevo_snapshot \
    media-video/freevo_runtime media-video/freevo_snapshot media-video/freevo

cd media-video
tar -zxvf /tmp/ebuild.tgz
rm /tmp/ebuild.tgz

# end of rsync-freevo
