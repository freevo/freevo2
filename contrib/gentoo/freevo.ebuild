DESCRIPTION="Digital video jukebox (PVR, DVR)."
HOMEPAGE="http://www.freevo.org/"

PV2=`echo $PV | sed 's/_/-/'`
SRC_URI="mirror://sourceforge/${PN}/${PN}-src-${PV2}.tgz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86"
IUSE="matrox dvd encode lirc X"

DEPEND=">=dev-python/pygame-1.5.5
	>=media-libs/freetype-2.1.4
	>=dev-python/Imaging-1.1.3
	>=dev-python/pyxml-0.8.1
	>=dev-python/twisted-1.0.6
	>=media-libs/libsdl-1.2.5
	>=dev-python/pysqlite-0.4.1
	>=dev-python/mmpython-0.2
	matrox? ( >=media-video/matroxset-0.3 )
	>=media-video/mplayer-0.91
	>=media-tv/xmltv-0.5.16
	>=sys-apps/sed-4
	dvd? ( >=media-video/xine-ui-0.9.22 )
	encode? ( >=media-sound/cdparanoia-3.9.8 >=media-sound/lame-3.93.1 )
	lirc? ( app-misc/lirc >=dev-python/pylirc-0.0.3 )
	X? ( virtual/x11 )"


inherit distutils

src_unpack() {
	unpack freevo-src-${PV2}.tgz
	ln -s freevo-${PV2} freevo-${PV}
}

src_install() {
        distutils_src_install

 	install -d ${D}/etc/freevo
 	install -m 644 local_conf.py.example ${D}/etc/freevo

 	# install boot scripts
 	install -d ${D}/etc/init.d
 	install -m 755 boot/gentoo-freevo ${D}/etc/init.d/freevo
 	install -d ${D}/etc/conf.d
 	install -m 755 boot/gentoo-conf.d ${D}/etc/conf.d/freevo
}

pkg_postinst() {
	local myconf="--geometry=800x600 --display=sdl"
	use matrox && myconf="--geometry=768x576 --display=mga"

	/bin/ls -l /etc/localtime | grep Europe >/dev/null 2>/dev/null && \
	    myconf="$myconf --tv=pal"

	einfo "Running freevo setup"

	/usr/bin/freevo setup ${myconf} || die

	einfo
	einfo "Please check /etc/freevo/freevo.conf and /etc/freevo/local_conf.py and"
	einfo "before starting freevo. To rebuild freevo.conf with different parameters"
        einfo "run /opt/freevo/freevo setup"
	einfo

        if [ -e /opt/freevo/runtime/preloads ]; then
                ewarn "This version of freevo doesn't need the runtime anymore"
                ewarn "Please unmerge freevo_runtime"
                echo -ne "\a" ; sleep 0.1 &>/dev/null ; sleep 0,1 &>/dev/null
                echo -ne "\a" ; sleep 1
                echo -ne "\a" ; sleep 0.1 &>/dev/null ; sleep 0,1 &>/dev/null
                echo -ne "\a" ; sleep 1
                echo -ne "\a" ; sleep 0.1 &>/dev/null ; sleep 0,1 &>/dev/null
                echo -ne "\a" ; sleep 1
                echo -ne "\a" ; sleep 0.1 &>/dev/null ; sleep 0,1 &>/dev/null
                echo -ne "\a" ; sleep 1
                echo -ne "\a" ; sleep 0.1 &>/dev/null ; sleep 0,1 &>/dev/null
                echo -ne "\a" ; sleep 1
                sleep 5
        fi
        
        if [ -e /opt/freevo ]; then
                ewarn "There is something left in /opt/freevo, please delete it"
                ewarn "manually"
	fi

	if [ -e /etc/freevo/freevo_config.py ]; then
		ewarn "Please remove /etc/freevo/freevo_config.py"
		sleep 5
	fi

	if [ -e /etc/init.d/freevo-webserver ]; then
		ewarn "Please remove /etc/init.d/freevo-webserver and"
		ewarn "/etc/init.d/freevo-recordserver."
		sleep 5
	fi

	einfo
	einfo "You may also want to emerge tvtime or xmltv"
	einfo
}
