DESCRIPTION="Freevo Runtime"
RUNTIME_DIR="${D}/opt/freevo/runtime"

IUSE="dxr3"

SRC_URI="http://www.libsdl.org/release/SDL-1.2.5.tar.gz
	 http://www.libsdl.org/projects/SDL_image/release/SDL_image-1.2.2.tar.gz
	 http://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-2.0.6.tar.gz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=media-libs/libsdl-1.2.5
	>=dev-python/pygame-1.5.5"

src_unpack() {
	unpack SDL-1.2.5.tar.gz
	unpack SDL_ttf-2.0.6.tar.gz
	unpack SDL_image-1.2.2.tar.gz
}

src_compile() {
        # building a patched libsdl
	cd ${WORKDIR}/SDL-1.2.5
	patch -p1 < ${FILESDIR}/SDL-1.2.4-patch1
	
	econf || die
	emake || die
	
	# building a patched SDL-ttf
	cd ${WORKDIR}/SDL_ttf*
	patch -p0 < ${FILESDIR}/SDL_ttf2-2.0.6-patch2
	econf || die
	emake || die

	building a SDL_image with Exif support
	cd ${WORKDIR}/SDL_image*
	patch -p1 < ${FILESDIR}/IMG_jpg.c.diff
	econf || die
	emake || die
}

src_install() {
	cd ${WORKDIR}
	install -d $RUNTIME_DIR/lib
	install SDL_ttf-2.0.6/.libs/libSDL_ttf-2.0* $RUNTIME_DIR/lib
	install SDL-1.2.5/src/.libs/libSDL-1.2.so.0.0.5 $RUNTIME_DIR/lib
	install SDL_image-1.2.2/.libs/libSDL_image-1.2.so.0.1.1 $RUNTIME_DIR/lib
	install -m 644 ${FILESDIR}/preloads-1.3.2 $RUNTIME_DIR/preloads
}
