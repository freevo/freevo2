Summary: A cross-platform multimedia library.
Name: SDL
Version: 1.2.5
Release: 4_freevo
Source: http://www.libsdl.org/release/%{name}-%{version}.tar.gz
Patch0: SDL-1.1.7-byteorder.patch
Patch2: SDL-1.2.2-autoconf25.patch
Patch4: SDL-1.2.3-prefersounddaemons.patch
Patch5: SDL-1.2.3-c++.patch
Patch6: SDL-1.2.5-dgavideo-modes.patch
Patch7: SDL-1.2.5-nokeyboard.patch
Patch8: SDL-1.2.5-dxr3-ffmpeg.patch
URL: http://www.libsdl.org/
License: LGPL
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Prefix: %{_prefix}
BuildRequires: arts-devel audiofile-devel
BuildRequires: esound-devel

%description
Simple DirectMedia Layer (SDL) is a cross-platform multimedia library
designed to provide fast access to the graphics frame buffer and audio
device.

%package devel
Summary: Files needed to develop Simple DirectMedia Layer applications.
Group: Development/Libraries
Requires: SDL = %{version} XFree86-devel

%description devel
Simple DirectMedia Layer (SDL) is a cross-platform multimedia library
designed to provide fast access to the graphics frame buffer and audio
device. This package provides the libraries, include files, and other
resources needed for developing SDL applications.

%prep
rm -rf %{buildroot}

%setup -q 
%patch0 -p1 -b .byte
AUTOMAKE_VER=`automake --version |head -n1 |sed -e "s,.* ,," |cut -b1-3 | sed -e "s,\.,,g"`
if [ "$AUTOMAKE_VER" -gt 14 ]; then
%patch2 -p1 -b .ac25x
fi
%patch4 -p1 -b .prefer
%patch5 -p1 -b .c++
%patch6 -p1 -b .modes
%patch7 -p1 
%patch8 -p1 

%build
cp /usr/share/libtool/config.{sub,guess} .
./autogen.sh
CFLAGS="$RPM_OPT_FLAGS -fPIC" CXXFLAGS="$RPM_OPT_FLAGS -fPIC" LDFLAGS="-fPIC" ./configure --disable-debug --prefix=%{prefix} --sysconfdir=/etc --enable-dlopen --enable-arts --enable-arts-shared --libdir=%{_libdir} \
--enable-esd --enable-esd-shared
# Workaround for broken automake mess
AUTOMAKE_VER=`automake --version |head -n1 |sed -e "s,.* ,," |cut -b1-3 | sed -e "s,\.,,g"`
if [ "$AUTOMAKE_VER" -gt 14 ]; then
cat >automake <<EOF
exit 0
EOF
chmod +x automake
export PATH=`pwd`:$PATH
fi
# End workaround
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
# Continued workaround for automake mess
export PATH=`pwd`:$PATH
%makeinstall

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc README-SDL.txt COPYING CREDITS BUGS
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root)
%doc README README-SDL.txt COPYING CREDITS BUGS WhatsNew docs.html docs/html
%doc docs/index.html
%{_bindir}/*-config
%{_libdir}/lib*.so
%{_libdir}/*a
%{_includedir}/SDL
%{_datadir}/aclocal/*
%{_mandir}/man3/SDL*.3*

%changelog
* Tue Sep 16 2003 TC Wan <tcwan@cs.usm.my> 1.2.5-4_freevo
- Patched for no keyboard, dxr3 ffmpeg support

* Mon Feb 10 2003 Thomas Woerner  <twoerner@redhat.com> 1.2.5-3
- added -fPIC to LDFLAGS

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Dec 10 2002 Thomas Woerner <twoerner@redhat.com> 1.2.5-1
- new version 1.2.5
- disabled conflicting automake16 patch
- dgavideo modes fix (#78861)

* Sun Dec 01 2002 Elliot Lee <sopwith@redhat.com> 1.2.4-7
- Fix unpackaged files by including them.
- _smp_mflags

* Fri Nov 29 2002 Tim Powers <timp@redhat.com> 1.2.4-6
- remove unpackaged files from the buildroot
- lib64'ize

* Sat Jul 20 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- do not require nasm for mainframe

* Tue Jul  2 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.4-4
- Fix bug #67255

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.4-1
- 1.2.4
- Fix build with automake 1.6

* Mon Mar 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-7
- Fix AM_PATH_SDL automake macro with AC_LANG(c++) (#60533)

* Thu Feb 28 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-6
- Rebuild in current environment

* Thu Jan 24 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-5
- dlopen() aRts and esd rather than linking directly to them.
- make sure aRts and esd are actually used if they're running.

* Mon Jan 21 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-4
- Don't crash without xv optimization: BuildRequire a version of nasm that
  works.

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Dec 17 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-2
- Rebuild with new aRts, require arts-devel rather than kdelibs-sound-devel
- Temporarily exclude alpha (compiler bugs)

* Thu Nov 22 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.3-1
- 1.2.3

* Sat Nov 17 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-5
- Add workaround for automake 1.5 asm bugs

* Tue Oct 30 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-4
- Make sure -fPIC is used on all architectures (#55039)
- Fix build with autoconf 2.5x

* Fri Aug 31 2001 Bill Nottingham <notting@redhat.com> 1.2.2-3
- rebuild (fixes #50750??)

* Thu Aug  2 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-2
- SDL-devel should require esound-devel and kdelibs-sound-devel (#44884)

* Tue Jul 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.2-1
- Update to 1.2.2; this should fix #47941
- Add build dependencies

* Tue Jul 10 2001 Elliot Lee <sopwith@redhat.com> 1.2.1-3
- Rebuild to eliminate libXv/libXxf86dga deps.

* Fri Jun 29 2001 Preston Brown <pbrown@redhat.com>
- output same libraries for sdl-config whether --libs or --static-libs 
  selected.  Fixes compilation of most SDL programs.
- properly packaged new HTML documentation

* Sun Jun 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.1-1
- 1.2.1

* Mon May  7 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.2.0-2
- Add Bill's byteorder patch

* Sun Apr 15 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.2.0

* Tue Feb 27 2001 Karsten Hopp <karsten@redhat.de>
- SDL-devel requires SDL

* Tue Jan 16 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Require arts rather than kdelibs-sound

* Sun Jan  7 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.7

* Tue Oct 24 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.1.6

* Mon Aug  7 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- build against new DGA
- update to 1.1.4, remove patches (they're now in the base release)

* Tue Aug  1 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- %%post -p /sbin/ldconfig (Bug #14928)
- add URL

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sun Jun 18 2000 Bill Nottingham <notting@redhat.com>
- replace patch that fell out of SRPM

* Tue Jun 13 2000 Preston Brown <pbrown@redhat.com>
- FHS paths
- use 1.1 (development) version; everything even from Loki links to it!

* Thu May  4 2000 Bill Nottingham <notting@redhat.com>
- autoconf fixes for ia64

* Mon Apr 24 2000 Tim Powers <timp@redhat.com>
- updated to 1.0.8

* Tue Feb 15 2000 Tim Powers <timp@redhat.com>
- updated to 1.0.4, fixes problems when run in 8bpp

* Tue Feb 01 2000 Tim  Powers <timp@redhat.com>
- applied patch from Hans de Goede <hans@highrise.nl> for fullscreen toggling.
- using  --enable-video-x11-dgamouse since it smoothes the mouse some.

* Sun Jan 30 2000 Tim Powers <timp@redhat.com>
- updated to 1.0.3, bugfix update

* Fri Jan 28 2000 Tim Powers <timp@redhat.com>
- fixed group etc

* Fri Jan 21 2000 Tim Powers <timp@redhat.com>
- build for 6.2 Powertools

* Wed Jan 19 2000 Sam Lantinga <slouken@devolution.com>
- Re-integrated spec file into SDL distribution
- 'name' and 'version' come from configure 
- Some of the documentation is devel specific
- Removed SMP support from %build - it doesn't work with libtool anyway

* Tue Jan 18 2000 Hakan Tandogan <hakan@iconsult.com>
- Hacked Mandrake sdl spec to build 1.1

* Sun Dec 19 1999 John Buswell <johnb@mandrakesoft.com>
- Build Release

* Sat Dec 18 1999 John Buswell <johnb@mandrakesoft.com>
- Add symlink for libSDL-1.0.so.0 required by sdlbomber
- Added docs

* Thu Dec 09 1999 Lenny Cartier <lenny@mandrakesoft.com>
- v 1.0.0

* Mon Nov  1 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- First spec file for Mandrake distribution.

# end of file
