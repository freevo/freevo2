DESCRIPTION="Freevo Runtime"
RUNTIME_DIR="${D}/opt/freevo/runtime"

IUSE="dxr3"

SRC_URI="mirror://sourceforge/freetype/freetype-2.0.9.tar.bz2
         http://www.libsdl.org/release/SDL-1.2.5.tar.gz
	 http://www.libsdl.org/projects/SDL_image/release/SDL_image-1.2.2.tar.gz
	 http://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-2.0.5.tar.gz
	 mirror://sourceforge/pylirc/pylirc-0.0.3.tar.gz
         http://cddb-py.sourceforge.net/CDDB.tar.gz"

LICENSE="GPL-2"

SLOT="0"

KEYWORDS="x86"

DEPEND=">=media-libs/libsdl-1.2.4
	   dxr3? ( >= media-libs/libfame-0.9.0 )"


src_unpack() {
	unpack SDL-1.2.5.tar.gz
	unpack freetype-2.0.9.tar.bz2
	unpack SDL_ttf-2.0.5.tar.gz
	unpack SDL_image-1.2.2.tar.gz
	unpack pylirc-0.0.3.tar.gz
	unpack CDDB.tar.gz
}

src_compile() {
        # compile pylirc if we use lirc
        if [ -f /usr/include/lirc/lirc_client.h ]
	then
  	    cd ${WORKDIR}/pylirc-0.0.3
	    ./setup.py build
	fi
	
	# compile CDDB.py
	cd ${WORKDIR}/CDDB-*
	python ./setup.py build
	
        # building a patched libsdl
	cd ${WORKDIR}/SDL-1.2.5
	patch -p1 < ${FILESDIR}/SDL-1.2.4-patch1

	use dxr3 && \
	  ( patch -p1 < ${FILESDIR}/SDL12_dxr3.patch
	    aclocal
	    automake
	    autoconf )
	  
	econf || die
	emake || die
	
	# building a patched SDL-ttf
	cd ${WORKDIR}/SDL_ttf*
	patch -p1 < ${FILESDIR}/SDL_ttf2-patch2
	econf || die
	emake || die

	# building an old (working) freetype
	cd ${WORKDIR}/freetype*
	econf || die
	emake || die

	# building a SDL_image with Exif support
	cd ${WORKDIR}/SDL_image*
	patch -p1 < ${FILESDIR}/IMG_jpg.c.diff
	econf || die
	emake || die
}

src_install() {
	cd ${WORKDIR}
	ls
	ls CDDB*
	install -d $RUNTIME_DIR/lib
	install -d $RUNTIME_DIR/python
	if [ -f /usr/include/lirc/lirc_client.h ]
	then
	    install pylirc-0.0.3/build/lib*/pylircmodule.so $RUNTIME_DIR/python
	fi
	install CDDB*/build/lib*/* $RUNTIME_DIR/python
	install freetype-2.0.9/objs/.libs/libfreetype.so.6.3.0 $RUNTIME_DIR/lib
	install SDL_ttf-2.0.5/.libs/libSDL_ttf-2.0.so.0.0.5 $RUNTIME_DIR/lib
	install SDL-1.2.5/src/.libs/libSDL-1.2.so.0.0.5 $RUNTIME_DIR/lib
	install SDL_image-1.2.2/.libs/libSDL_image-1.2.so.0.1.1 $RUNTIME_DIR/lib
	install -m 644 ${FILESDIR}/preloads-1.3.1 $RUNTIME_DIR/preloads
}
