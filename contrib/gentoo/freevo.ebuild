DESCRIPTION="Digital video jukebox (PVR, DVR)."
HOMEPAGE="http://www.freevo.org/"

SRC_URI="mirror://sourceforge/${PN}/${P}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86"
IUSE="matrox dvd encode lirc X"

inherit distutils

DEPEND=">=dev-python/pygame-1.5.6
	>=media-libs/freetype-2.1.5
	>=dev-python/Imaging-1.1.4
	>=dev-python/pyxml-0.8.3
	>=dev-python/twisted-1.2.0
	>=media-libs/libsdl-1.2.7
	>=dev-python/mmpython-0.4.3
	matrox? ( >=media-video/matroxset-0.3 )
	>=media-video/mplayer-1.0_pre4
	>=sys-apps/sed-4
	dvd? ( >=media-video/xine-ui-0.9.23 )
	encode? ( >=media-sound/cdparanoia-3.9.8 >=media-sound/lame-3.93.1 )
	lirc? ( app-misc/lirc >=dev-python/pylirc-0.0.3 )
	X? ( virtual/x11 )"


src_compile() {
        local myconf

        if [ "`use matrox`" ] ; then
                myconf="--geometry=768x576 --display=mga"
        elif [ "`use X`" ] ; then
                myconf="--geometry=800x600 --display=x11"
        else
                myconf="--geometry=800x600 --display=fbdev"
        fi

        if [ "`/bin/ls -l /etc/localtime | grep Europe`" ] ; then
                myconf="$myconf --tv=pal"
        fi

        sed -e "s:/etc/freevo/freevo.conf:${T}/freevo.conf:" \
                -i "${S}/src/setup_freevo.py" || die "sed failed"

        "${S}/freevo" setup ${myconf} || die "configure problem"

        sed -e "s:${T}/freevo.conf:/etc/freevo/freevo.conf:" \
                -i "${S}/src/setup_freevo.py" || die "sed failed"
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
        einfo "If you want to schedule programs, emerge xmltv now."
        echo

        einfo "Please check /etc/freevo/freevo.conf and"
        einfo "/etc/freevo/local_conf.py before starting Freevo."
        einfo "To rebuild freevo.conf with different parameters,"
        einfo "please run:"
        einfo "    freevo setup"
        echo

        if [ -e "/opt/freevo" ] ; then
                ewarn "Please remove /opt/freevo because it is no longer used."
        fi
        if [ -e "/etc/freevo/freevo_config.py" ] ; then
                ewarn "Please remove /etc/freevo/freevo_config.py."
        fi
        if [ -e "/etc/init.d/freevo-record" ] ; then
                ewarn "Please remove /etc/init.d/freevo-record"
        fi
        if [ -e "/etc/init.d/freevo-web" ] ; then
                ewarn "Please remove /etc/init.d/freevo-web"
        fi
}
