DESCRIPTION="Freevo"
FREEVO_INSTALL_DIR="${D}/opt/freevo"

IUSE="dxr3 matrox"

FPV=${PV}
PV=`echo ${PV} | sed 's/_\(pre[0-9]\)/-\1/'`
SRC_URI="mirror://sourceforge/freevo/freevo-src-${PV}.tgz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=dev-python/pygame-1.5.3
	>=dev-python/Imaging-1.1.3
	>=dev-python/PyXML-0.8.1
	>=media-libs/libsdl-1.2.4
	>=media-video/mplayer-0.90_rc2
	>=freevo_runtime-1.3.1
	ogg? (>=media-libs/pyvorbis-1.1)"


src_unpack() {
	unpack freevo-src-${PV}.tgz
	ln -s freevo-${PV} freevo-${FPV}
	cd freevo-${PV}
}

src_compile() {
	local myconf="--geometry=800x600 --display=sdl"
	use matrox && myconf="--geometry=768x576 --display=mga"
	use dxr3 && myconf="--geometry=768x576 --display=dxr3"

	/bin/ls -l /etc/localtime | grep Europe >/dev/null 2>/dev/null && \
	    myconf="$myconf --tv=pal"

	if [ "`use -X`" ]; then
	    mv Makefile Makefile.bak
	    sed 's/\(all.*\)freevo_xwin/\1/' Makefile.bak > Makefile
	    rm Makefile.bak
	fi
	emake || make || die
	./freevo setup ${myconf} || die
}

src_install() {
	# patch setup_freevo to use /etc/freevo
	patch -p1 < ${FILESDIR}/setup.patch

	install -d ${D}/etc/freevo
	install -m 644 freevo.conf local_conf.py ${D}/etc/freevo

	mydocs="BUGS COPYING ChangeLog FAQ INSTALL README TODO VERSION"
	mydocs="$mydocs Docs/CREDITS Docs/NOTES"
	dodoc $mydocs

	make PREFIX=$FREEVO_INSTALL_DIR \
	    LOGDIR=${D}/var/log/freevo \
	    CACHEDIR=${D}/var/cache/freevo install

	cd $FREEVO_INSTALL_DIR
	rm -rf $mydocs Docs runtime freevo.conf local_conf.py \
	    configure setup_build.py *.c *.h Makefile fbcon/Makefile fbcon/vtrelease.c \
	    contrib/TatChee_RPM_Specs contrib/gentoo skins/aubin1 skins/barbieri \
	    skins/dischi1 skins/krister1 skins/malt1

}

pkg_postinst() {
	einfo
	einfo "Please check /etc/freevo/freevo.conf and /etc/freevo/local_conf.py and"
	einfo "before starting freevo. To rebuild freevo.conf with different parameters"
        einfo "run /opt/freevo/freevo setup"
	einfo

	if [ -e /etc/freevo/freevo_config.py ]; then
		ewarn "Please remove /etc/freevo/freevo_config.py"
		sleep 5
	fi
}
