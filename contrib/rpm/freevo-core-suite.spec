%define freevoname freevo
%define freevover 1.5
%define freevorel 3_freevo
##############################################################################
Summary: Meta-package for Freevo core functionality
Name: freevo-core-suite
Version: %{freevover}
Release: %{freevorel}
Copyright: GPL
Group: Applications/Multimedia
URL:            http://freevo.sourceforge.net/
Requires: SDL >= 1.2.6, SDL_image >= 1.2.3, SDL_ttf >= 2.0.6, SDL_mixer >= 1.2.5
Requires: smpeg >= 0.4.4, freetype >= 2.1.4, util-linux
Requires: python >= 2.2, python-game >= 1.5.6, python-imaging >= 1.1.4, PyXML
Requires: mmpython >= 0.4.3, mx >= 2.0.5, python-numeric >= 23.1,
Requires: aumix >= 2.8, libjpeg >= 6b, libexif >= 0.5.10
Requires: python-Twisted >= 1.1.0
Requires: lsdvd
Requires: %{freevoname}
BuildArch: noarch


%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

This is a meta-package used by apt to setup all required core packages
for using freevo.

%prep

%build

%install

%files 
%defattr(-,root,root)

%changelog
* Tue Jun 29 2004 TC Wan <tcwan@cs.usm.my>
- Added python-numeric dependency
                                                                                
* Fri Jun 18 2004 TC Wan <tcwan@cs.usm.my>
- Updated for Freevo 1.5

* Mon Nov  3 2003 TC Wan <tcwan@cs.usm.my>
- Removed python-fchksum dependency

* Wed Oct 15 2003 TC Wan <tcwan@cs.usm.my>
- Moved twisted depedency to core

* Sat Sep 20 2003 TC Wan <tcwan@cs.usm.my>
- Removed CDDB dependency since it's part of mmpython

* Thu Sep 18 2003 TC Wan <tcwan@cs.usm.my>
- Added CDDB dependency

* Wed Sep 17 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for RH 9
