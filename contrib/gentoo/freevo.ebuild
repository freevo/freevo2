DESCRIPTION="Freevo"
FREEVO_INSTALL_DIR="${D}/opt/freevo"


SRC_URI="http://www.tzi.de/~dmeyer/freevo/${P}.tgz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=dev-python/pygame-1.5.3
	>=dev-python/Imaging-1.1.3
	>=dev-python/PyXML-0.7.1
	>=media-libs/libsdl-1.2.4
	>=media-video/mplayer-0.90_rc2
	=freevo_runtime-1.1
	ogg? (>=media-libs/pyvorbis-1.1)"


src_unpack() {
	unpack ${P}.tgz
}

src_compile() {
	local myconf="--geometry=800x600 --display=sdl"
	use matrox && myconf="--geometry=768x576 --display=mga"
	./configure ${myconf} || die
	emake || make || die
}

src_install() {
	install -d ${D}/etc/freevo
	install freevo_config.py freevo.conf ${D}/etc/freevo
	rm freevo_config.py freevo.conf

	install -d $FREEVO_INSTALL_DIR
	cp -r * $FREEVO_INSTALL_DIR

	# install -d ${D}/usr/bin
	# install ${FILESDIR}/freevo ${D}/usr/bin
	# install ${FILESDIR}/freevo $FREEVO_INSTALL_DIR

	install -m 0777 -d ${D}/var/log/freevo
	install -m 0777 -d ${D}/var/cache/freevo
	install -m 0777 -d ${D}/var/cache/xmltv
}

pkg_postinst() {
	einfo
	einfo "If you have Python 2.2.2 installed, support for bins files"
	einfo "is not working. You need to install a newer (masked) version"
	einfo "of PyXML (version 0.8.1)"
	einfo
	einfo "Please check /etc/freevo/freevo.conf and"
	einfo "/etc/freevo/freevo_config.py before starting freevo"
	einfo
}
