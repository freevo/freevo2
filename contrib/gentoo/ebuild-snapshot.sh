#!/usr/bin/env bash

# ebuild-snapshot.sh 
#
#   <dmeyer@tzi.de>
# $Id$


version=`echo $1 | sed 's/[-]/_/g'`
tag=REL-`echo $1 | sed 's/[\.-]/_/g' | sed 'y/prerc/PRERC/'` 
echo src name: freevo-$version and freevo-src-$version
echo cvs tag:  $tag

read

cd `dirname $0`/../../

function cvs_update {
    echo cvs update
    cvs update -dP
}

function cvs_tag {
    echo setting new cvs tag
    cvs tag $tag
}

function pack {
    cd ..
    sudo rm -rf /tmp/freevo-$version
    echo copy directory to /tmp
    cp -r freevo /tmp/freevo-$version

    echo cleaning up
    cd /tmp/freevo-$version
    make clean
    rm freevo.conf*
    find /tmp/freevo-$version -type d -name CVS | xargs rm -rf
    find /tmp/freevo-$version -name .cvsignore  | xargs rm -rf
    find /tmp/freevo-$version -name '.#*'       | xargs rm -rf
    sudo chown -R root.root /tmp/freevo-$version

    cd /tmp/
    echo making tgz
    sudo tar -zcvf /usr/portage/distfiles/freevo-src-$version.tgz freevo-$version

    echo remove tmp dir
    sudo rm -rf freevo-$version
}

function ebuild {
    sudo cp `dirname $0`/freevo.ebuild \
	/usr/local/portage/media-video/freevo/freevo-$version.ebuild

    cd /usr/local/portage/media-video/freevo
    sudo rm -f files/digest-freevo-$version
    sudo chown -R root.root .
    sudo ebuild freevo-$version.ebuild digest 

    cd ..
    tar -zcvf /tmp/ebuild.tgz freevo freevo_runtime
    scp -r /tmp/ebuild.tgz dischi@freevo.sf.net:/home/groups/f/fr/freevo/htdocs/gentoo
    rm /tmp/ebuild.tgz
}

function sf_upload {
    # not working
    cd /usr/portage/distfiles/
    curl -T freevo-src-$version.tgz \
	ftp://anonymous:dmeyer_tzi.de@upload.sourceforge.net/incoming
}

eval $2


# end of ebuild-snapshot.sh 
