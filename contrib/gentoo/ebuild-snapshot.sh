#!/usr/bin/env bash

# ebuild-snapshot.sh 
#
#   <dmeyer@tzi.de>
# $Id$


version=`echo $1 | sed 's/-bla/_/g' | sed 's/-r[0-9]//'`
ebuild_version=`echo $1 | sed 's/-/_/g' | sed 's/_\(r[0-9]\)/-\1/'`
tag=REL-`echo $1 | sed 's/\./_/g' | sed 'y/prerc/PRERC/'` 
echo src name: freevo-$ebuild_version and freevo-src-$version
echo ebuild: freevo-$ebuild_version
echo cvs tag:  $tag

read

cd `dirname $0`/../../

function cvs_update {
    echo cvs update
    cvs update -dP
}

function cvs_tag {
    echo setting new cvs tag
    cvs tag -F $tag
}

function pack {
    cd /tmp
    sudo rm -rf freevo-$version
    mkdir freevo-$version
    cd freevo-$version
    cp -r /home/dmeyer/src/freevo/CVS .
    cvs update -r $tag -dP

    cd /tmp/freevo-$version

    ./autogen.sh

    find /tmp/freevo-$version -type d -name CVS | xargs rm -rf
    find /tmp/freevo-$version -name .cvsignore  | xargs rm -rf

    sudo chown -R root:root /tmp/freevo-$version

    sudo python setup.py sdist
    sudo mv dist/* /usr/portage/distfiles
    cd /tmp
    echo remove tmp dir
    sudo rm -rf freevo-$version
}

function ebuild {
    sudo cp /home/dmeyer/src/freevo/contrib/gentoo/freevo.ebuild \
	/usr/local/portage/media-tv/freevo/freevo-$ebuild_version.ebuild
    cd /usr/local/portage/media-tv/freevo
    sudo rm -f files/digest-freevo-$version
    sudo chown -R root:root .
    sudo ebuild freevo-$ebuild_version.ebuild digest 
}

function ebuild_upload {
    sudo rm -rf /tmp/ebuild*
    (
	cd /usr/local/portage

	tar --atime-preserve -zcvf /tmp/freevo-ebuild.tgz \
	    media-tv/freevo media-tv/freevo-snapshot dev-python/mmpython-snapshot \
	    media-video/xine-ui media-libs/libsdl >/dev/null
    )
    scp -r contrib/gentoo/ChangeLog contrib/gentoo/rsync-freevo /tmp/freevo-ebuild.tgz \
	dischi@freevo.sf.net:/home/groups/f/fr/freevo/htdocs/gentoo
    rm /tmp/freevo-ebuild.tgz
}

function sf_upload {
    # not working
    cd /usr/portage/distfiles/
    curl -T freevo-src-$version.tgz \
	ftp://anonymous:dmeyer_tzi.de@upload.sourceforge.net/incoming
}

function get_wiki {
    httrack -O wiki http://freevo.sourceforge.net/cgi-bin/moin.cgi/ \
	"-*action=*" "-*UserPref*" "-*FindPage*" "-*HelpContents*" \
	"-*FreevoWikiHelp*" "-*RecentChanges*" "-*TitleIndex*" \
	"-*WordIndex*" "-*SiteNavigation*" "-*Hilfe*" "-*HelpOn*" \
	"-*AbandonedPages.html*" "-*Aktuelle_c4nderungen.html*" \
	"-*AufgegebeneSeiten.html*" "-*BenutzerEinstellungen.html*"
}

eval $2


# end of ebuild-snapshot.sh 
