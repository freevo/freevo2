DESCRIPTION="Freevo Runtime"
RUNTIME_DIR="${D}/opt/freevo/runtime"


SRC_URI="mirror://sourceforge/freetype/freetype-2.0.9.tar.bz2
	http://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-2.0.5.tar.gz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=media-libs/libsdl-1.2.4"


src_unpack() {
	unpack freetype-2.0.9.tar.bz2
	unpack SDL_ttf-2.0.5.tar.gz
}

src_compile() {
	# building a patched SDL-ttf
	cd work/SDL*
	patch -p1 < ${FILESDIR}/SDL_ttf2-patch2
	econf || die
	emake || die

	# building an old (working) freetype
	cd ../freetype*
	make || die
	emake || die
}

src_install() {
	pwd
	cd ../work
	install -d $RUNTIME_DIR
	install freetype-2.0.9/objs/.libs/libfreetype.so.6.3.0 $RUNTIME_DIR
	install SDL_ttf-2.0.5/.libs/libSDL_ttf-2.0.so.0.0.5 $RUNTIME_DIR
	install ${FILESDIR}/preloads $RUNTIME_DIR
}
