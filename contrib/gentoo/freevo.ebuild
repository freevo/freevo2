DESCRIPTION="Freevo"
FREEVO_INSTALL_DIR="${D}/opt/freevo"

IUSE="matrox"

PV=`echo ${PV} | sed 's/_\(pre[0-9]\)/-\1/' | sed 's/_\(test[0-9]\)/-\1/'`
S="${WORKDIR}/freevo-${PV}"

SRC_URI="mirror://sourceforge/freevo/freevo-src-${PV}.tgz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=dev-python/pygame-1.5.5
	>=media-libs/freetype-2.1.4
	>=dev-python/Imaging-1.1.3
	>=dev-python/PyXML-0.8.1
	>=dev-python/twisted-1.0.6
	>=media-libs/libsdl-1.2.5
	>=dev-python/mmpython-0.1
	>=media-video/mplayer-0.90"

if [ -f /usr/include/lirc/lirc_client.h ]
then
    DEPEND="$DEPEND
            >=dev-python/pylirc-0.0.3"
fi


src_unpack() {
	unpack freevo-src-${PV}.tgz
}

src_compile() {
	local myconf="--geometry=800x600 --display=sdl"
	use matrox && myconf="--geometry=768x576 --display=mga"

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

	# install boot scripts
	install -d ${D}/etc/init.d
	install -m 755 boot/gentoo-recordserver ${D}/etc/init.d/freevo-recordserver
	install -m 755 boot/gentoo-webserver ${D}/etc/init.d/freevo-webserver
	use matrox && install -m 755 boot/gentoo-freevo-mga ${D}/etc/init.d/freevo

	mydocs="BUGS COPYING ChangeLog FAQ INSTALL README TODO VERSION"
	mydocs="$mydocs Docs/CREDITS Docs/NOTES Docs/html/"
	dodoc $mydocs

        dodir /usr/share/doc/${PF}/html
        mv Docs/html/* ${D}/usr/share/doc/${PF}/html/
	mv Docs/freevo_howto ${D}/usr/share/doc/${PF}/
	make PREFIX=$FREEVO_INSTALL_DIR \
	    LOGDIR=${D}/var/log/freevo \
	    CACHEDIR=${D}/var/cache/freevo install

	cd $FREEVO_INSTALL_DIR
	rm -rf $mydocs Docs runtime freevo.conf local_conf.py \
	    configure setup_build.py *.c *.h Makefile fbcon/Makefile fbcon/vtrelease.c \
	    contrib boot WIP freevo_setup~ freevo~

}

pkg_postinst() {
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
        
	if [ -e /etc/freevo/freevo_config.py ]; then
		ewarn "Please remove /etc/freevo/freevo_config.py"
		sleep 5
	fi

	einfo
	einfo "You may also want to emerge tvtime or xmltv"
	einfo
}
