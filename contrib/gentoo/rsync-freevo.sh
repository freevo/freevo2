#!/usr/bin/env bash

# rsync-freevo
#
#   <dmeyer@tzi.de>
# $Id$

. /etc/make.conf

file=ebuild

if [ "$1" == "devel" ]; then
    echo downloading devel version
    file=ebuild-devel
fi

if [ "$PORTDIR_OVERLAY" = "" ]; then
    echo please define a PORTDIR_OVERLAY in /etc/make.conf
    echo and make sure you have the oermission to write in it
    exit 1
fi

cd /tmp
rm $file.tgz
wget http://freevo.sourceforge.net/gentoo/$file.tgz

if [ '!' -e $file.tgz ]; then
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
tar -zxvf /tmp/$file.tgz
rm /tmp/$file.tgz

# clear the dep cache because we have new informations
rm /var/cache/edb/dep/media-video/freevo-*

# end of rsync-freevo
