%define freevoname freevo-src
%define freevover 1.4
%define freevorel 1_freevo
##############################################################################
Summary: Meta-package for Freevo recording functionality
Name: freevo-recording-suite
Version: %{freevover}
Release: %{freevorel}
Copyright: GPL
Group: Applications/Multimedia
URL:   http://freevo.sourceforge.net/
Requires: freevo-core-suite
Requires: python-twisted >= 1.0.7 
Requires: vorbis-tools, libvorbis, lame, cdparanoia
Requires: mp1e >= 1.9.3
#Requires: ffmpeg >= 0.4.7
Requires: %{freevoname}


%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

This is a meta-package used by apt to setup all required recording packages
for using freevo to record TV programs.

%prep

%build

%install

%files 
%defattr(-,root,root)

%changelog
* Wed Sep 17 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for RH 9
