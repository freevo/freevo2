#!/usr/bin/env bash

# rsync-freevo.sh 
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
wget http://www.tzi.de/~dmeyer/freevo/ebuild.tgz

if [ '!' -e ebuild.tgz ]; then
    echo download failed
    exit 1
fi

cd $PORTDIR_OVERLAY

if [ '!' -e app-misc ]; then
    mkdir app-misc
fi

cd app-misc
rm -rf freevo_runtime freevo_snapshot freevo

tar -zxvf /tmp/ebuild.tgz
rm /tmp/ebuild.tgz

# end of rsync-freevo.sh 
