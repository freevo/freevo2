#!/usr/bin/env bash

# ebuild-snapshot.sh 
#
#   <dmeyer@tzi.de>
# $Id$


fname=freevo_snapshot-`date +%Y%m%d`

sudo cp `dirname $0`/freevo.ebuild /usr/local/portage/app-misc/freevo_snapshot/$fname.ebuild

cd `dirname $0`/../../
echo cvs update
cvs update -dP

cd ..
echo copy directory to /tmp
cp -r freevo /tmp/$fname

echo remove some files and change owner
find /tmp/$fname -type d -name CVS | xargs rm -rf
sudo chown -R root.root /tmp/$fname

cd /tmp/
echo making tgz
sudo tar -zcvf /usr/portage/distfiles/$fname.tgz $fname

echo remove tmp dir
sudo rm -rf $fname

cd /usr/local/portage/app-misc/freevo_snapshot
sudo chown -R root.root .
sudo ebuild $fname.ebuild digest 

scp /usr/portage/distfiles/$fname.tgz riemen:www/freevo
sudo rm /usr/portage/distfiles/$fname.tgz

cd ..
tar -zcvf /tmp/ebuild.tgz freevo_snapshot freevo_runtime

scp /tmp/ebuild.tgz riemen:www/freevo
rm /tmp/ebuild.tgz


# end of ebuild-snapshot.sh 
