%define geometry 800x600
%define display  x11
%define tv_norm  ntsc
%define chanlist us-cable
%define runtimever 4
Summary:	Freevo
Name:		freevo
Version:	1.3.1
Release:	1
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}-%{version}.tar.gz
Patch0:		%{name}-%{version}-runtime.patch
Patch1:		%{name}-%{version}-Makefile.patch
URL:		http://freevo.sourceforge.net/
Requires:	freevo-runtime >= %{runtimever}
Requires:	freevo-apps
Requires:	libjpeg
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log
%define _optimize 0

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer and nvrec to play and record video 
and audio.

%prep
#%setup  -n %{name}
%setup  -n %{name}-%{version}
%patch0 -p0
%patch1 -p0

./configure --geometry=%{geometry} --display=%{display} \
	--tv=%{tv_norm} --chanlist=%{chanlist}

%build
find . -name CVS | xargs rm -rf
make clean; make
pushd plugins/cddb
	make
popd
pushd src/games/rominfo
	make
popd

%package runtime
Summary: Libraries used by freevo executable. Must be installed for freevo to work.
Version:	%{runtimever}
Obsoletes: freevo_runtime
Group: Applications/Multimedia
AutoReqProv: no

%description runtime
This directory contains the Freevo runtime. It contains an executable,
freevo_python, dynamic link libraries for running Freevo as well as a copy
of the standard Python 2.2 libraries. It also contains the Freevo external 
applications. Right now that is MPlayer, cdparanoia and lame.

Please see the website at http://freevo.sourceforge.net for more information 
on how to use Freevo. The website also contains links to the source code
for all software included here.

%package apps
Summary: External applications used by freevo executable.
Obsoletes: freevo_apps
Group: Applications/Multimedia
Requires: freevo-runtime >= %{runtimever}
AutoReqProv: no

%description apps
This directory contains the Freevo external applications. 
Right now that is MPlayer, cdparanoia and lame.

Note: This package is not manadatory if standalone versions of the external
applications are installed, though configuration issues may be minimized if 
it is used.

%package boot
Summary: Files to enable a standalone Freevo system (started from initscript)
Group: Applications/Multimedia
Requires:	freevo

%description boot
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer, mpg321 and nvrec to play and
record video and audio.

Note: This installs the initscripts necessary for a standalone Freevo system.

%package testfiles
Summary: Sample multimedia files to test freevo
Group: Applications/Multimedia

%description testfiles
Test files that came with freevo. Placed in %{_cachedir}/freevo

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}
mkdir -p %{buildroot}%{_prefix}/fbcon/matroxset
mkdir -p %{buildroot}%{_prefix}/{boot,helpers,rc_client}
mkdir -p %{buildroot}%{_prefix}/{runtime/apps,runtime/dll,runtime/lib}
mkdir -p %{buildroot}%{_prefix}/src/{audio/eyed3,games/rominfo,gui,image,tv,video/plugins,www/bin,www/htdocs/images,www/htdocs/scripts,www/htdocs/styles}
mkdir -p %{buildroot}%{_prefix}/plugins/{cddb,weather/icons}
mkdir -p %{buildroot}%{_prefix}/skins/{fonts,icons,images,main1,xml/type1}
mkdir -p %{buildroot}%{_prefix}/skins/{aubin1,barbieri,dischi1,krister1,malt1}
mkdir -p %{buildroot}%{_prefix}/skins/icons/{AquaFusion,gnome,misc,old}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/{Images/Show,Images/Bins,Mame,Movies/skin.xml_Test,Music,tv-show-images}

install -m 755 freevo freevo_xwin runapp %{buildroot}%{_prefix}
install -m 644 freevo_config.py setup_build.py %{buildroot}%{_prefix}
install -m 644 fbcon/fbset.db %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/vtrelease fbcon/*.sh %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/matroxset/matroxset %{buildroot}%{_prefix}/fbcon/matroxset
install -m 755 helpers/blanking %{buildroot}%{_prefix}/helpers
install -m 755 helpers/*.pl %{buildroot}%{_prefix}/helpers
install -m 755 helpers/*.py %{buildroot}%{_prefix}/helpers
install -m 755 plugins/cddb/*.py plugins/cddb/cdrom.so %{buildroot}%{_prefix}/plugins/cddb
install -m 644 plugins/weather/*.py plugins/weather/librarydoc.txt %{buildroot}%{_prefix}/plugins/weather
install -m 644 plugins/weather/icons/*.png %{buildroot}%{_prefix}/plugins/weather/icons
install -m 644 rc_client/*.py %{buildroot}%{_prefix}/rc_client

install -m 644 runtime/*.py %{buildroot}%{_prefix}/runtime
install -m 644 runtime/preloads %{buildroot}%{_prefix}/runtime
install -m 644 runtime/README %{buildroot}%{_prefix}/runtime
install -m 644 runtime/VERSION %{buildroot}%{_prefix}/runtime
cp -av runtime/apps/* %{buildroot}%{_prefix}/runtime/apps
cp -av runtime/dll/* %{buildroot}%{_prefix}/runtime/dll
cp -av runtime/lib/* %{buildroot}%{_prefix}/runtime/lib

install -m 644 src/*.py %{buildroot}%{_prefix}/src
install -m 644 src/audio/*.py %{buildroot}%{_prefix}/src/audio
install -m 644 src/audio/eyed3/*.py %{buildroot}%{_prefix}/src/audio/eyed3
install -m 644 src/games/*.py %{buildroot}%{_prefix}/src/games
install -m 644 src/games/rominfo/rominfo* %{buildroot}%{_prefix}/src/games/rominfo
install -m 644 src/gui/*.py %{buildroot}%{_prefix}/src/gui
install -m 644 src/image/*.py %{buildroot}%{_prefix}/src/image
install -m 644 src/tv/*.py %{buildroot}%{_prefix}/src/tv
install -m 644 src/video/*.py %{buildroot}%{_prefix}/src/video
install -m 644 src/video/plugins/*.py %{buildroot}%{_prefix}/src/video/plugins

install -m 644 src/www/*.py %{buildroot}%{_prefix}/src/www
install -m 644 src/www/bin/* %{buildroot}%{_prefix}/src/www/bin
install -m 644 src/www/htdocs/images/* %{buildroot}%{_prefix}/src/www/htdocs/images
install -m 644 src/www/htdocs/scripts/* %{buildroot}%{_prefix}/src/www/htdocs/scripts
install -m 644 src/www/htdocs/styles/* %{buildroot}%{_prefix}/src/www/htdocs/styles

install -m 644 skins/fonts/* %{buildroot}%{_prefix}/skins/fonts
install -m 644 skins/icons/AquaFusion/* %{buildroot}%{_prefix}/skins/icons/AquaFusion
install -m 644 skins/icons/misc/* %{buildroot}%{_prefix}/skins/icons/misc
install -m 644 skins/icons/gnome/* %{buildroot}%{_prefix}/skins/icons/gnome
install -m 644 skins/icons/old/* %{buildroot}%{_prefix}/skins/icons/old
install -m 644 skins/images/* %{buildroot}%{_prefix}/skins/images
install -m 644 skins/main1/* %{buildroot}%{_prefix}/skins/main1
install -m 644 skins/xml/type1/* %{buildroot}%{_prefix}/skins/xml/type1
install -m 644 skins/aubin1/* %{buildroot}%{_prefix}/skins/aubin1
install -m 644 skins/barbieri/* %{buildroot}%{_prefix}/skins/barbieri
install -m 644 skins/malt1/* %{buildroot}%{_prefix}/skins/malt1

install -m 644 freevo.conf local_conf.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m 644 boot/URC-7201B00 %{buildroot}%{_prefix}/boot
install -m755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d


install -m 644 testfiles/Images/*.jpg %{buildroot}%{_cachedir}/freevo/testfiles/Images
install -m 644 testfiles/Images/*.ssr %{buildroot}%{_cachedir}/freevo/testfiles/Images
install -m 644 testfiles/Images/Show/* %{buildroot}%{_cachedir}/freevo/testfiles/Images/Show
install -m 644 testfiles/Images/Bins/* %{buildroot}%{_cachedir}/freevo/testfiles/Images/Bins
install -m 644 testfiles/Mame/* %{buildroot}%{_cachedir}/freevo/testfiles/Mame
install -m 644 testfiles/Movies/*.avi testfiles/Movies/*.jpg testfiles/Movies/*.xml %{buildroot}%{_cachedir}/freevo/testfiles/Movies
install -m 644 testfiles/Movies/skin.xml_Test/* %{buildroot}%{_cachedir}/freevo/testfiles/Movies/skin.xml_Test
install -m 644 testfiles/Music/*.mp3 %{buildroot}%{_cachedir}/freevo/testfiles/Music

%clean
rm -rf $RPM_BUILD_ROOT

%post
cd %{_prefix}; ./runapp python setup_build.py --compile=%{_optimize},%{_prefix}
mkdir -p %{_cachedir}/freevo
mkdir -p %{_cachedir}/xmltv/logos
mkdir -p %{_logdir}/freevo
chmod 777 %{_cachedir}/{freevo,xmltv,xmltv/logos}
chmod 777 %{_logdir}/freevo

%preun 
rm -rf %{_logdir}/freevo
find %{_prefix} -name "*.pyc" |xargs rm -f

%files
%defattr(-,root,root,755)
%{_prefix}/[c-q]*
%{_prefix}/rc_client
%{_prefix}/runapp
%{_prefix}/[s-z]*

%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(644,root,root) %config %{_sysconfdir}/freevo/freevo.conf
%attr(644,root,root) %config %{_sysconfdir}/freevo/local_conf.py
%attr(644,root,root) %doc BUGS ChangeLog COPYING FAQ INSTALL README TODO Docs/*

%files runtime
%defattr(644,root,root,755)
%{_prefix}/runtime/*.py
%{_prefix}/runtime/README
%{_prefix}/runtime/VERSION
%{_prefix}/runtime/preloads
%defattr(755,root,root,755)
%{_prefix}/runtime/apps/freevo_python
%{_prefix}/runtime/dll
%{_prefix}/runtime/lib

%preun runtime
find %{_prefix}/runtime -name "*.pyc" |xargs rm -f

%files apps
%defattr(755,root,root,755)
%{_prefix}/runtime/apps/cdparanoia
%{_prefix}/runtime/apps/lame
%{_prefix}/runtime/apps/mplayer

%files boot
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/freevo
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/freevo_dep
%attr(755,root,root) %{_prefix}/boot/URC-7201B00
%config %{_sysconfdir}/freevo/boot_config

%files testfiles
%defattr(644,root,root,755)
%{_cachedir}/freevo/testfiles

%post boot
if [ -x /sbin/chkconfig ]; then
  chkconfig --add freevo
fi
depmod -a

%preun boot
if [ "$1" = 0 ] ; then
  if [ -x /sbin/chkconfig ]; then
    chkconfig --del freevo
  fi
fi

%post testfiles
mkdir -p %{_cachedir}/freevo/testfiles/Movies/Recorded
ln -sf %{_cachedir}/freevo/testfiles %{_prefix}

%preun testfiles
rm -f %{_prefix}/testfiles

%changelog
* Thu Feb 13 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.3.1 release

* Fri Feb  7 2003 TC Wan <tcwan@cs.usm.my>
- Moved *.py bytecompilation to post-install to reduce RPM size
- Disabled automatic requires checking for runtime and apps
  (since we provide all the necessary libraries) to avoid
  rpm installation issues

* Tue Feb  4 2003 TC Wan <tcwan@cs.usm.my>
- Merged 1.3.1 runtime release

* Thu Jan 30 2003 TC Wan <tcwan@cs.usm.my>
- Added www subdir to specfile

* Wed Jan 29 2003 TC Wan <tcwan@cs.usm.my>
- Minor tweak to helpers subdirectory install

* Tue Dec 31 2002 TC Wan <tcwan@cs.usm.my>
- Automate CVS date generation

* Fri Dec 13 2002 TC Wan <tcwan@cs.usm.my>
- Update dir structure to Dec 13 CVS

* Fri Nov 29 2002 TC Wan <tcwan@cs.usm.my>
- Complete revamp for new directory structure

* Wed Nov 20 2002 TC Wan <tcwan@cs.usm.my>
- Cleaned up files directive

* Wed Nov 13 2002 TC Wan <tcwan@cs.usm.my>
- Disabled display=sdl as mplayer doesn't work reliably with this option

* Sat Oct 26 2002 TC Wan <tcwan@cs.usm.my>
- Fixed permissions problem for icons/64x64 directory

* Tue Oct 15 2002 TC Wan <tcwan@cs.usm.my>
- Moved freevo.conf to /etc/freevo where freevo_config.py resides
- Defaulted TV settings to ntsc, us-cable to match TV guide

* Mon Oct 14 2002 TC Wan <tcwan@cs.usm.my>
- Updated for 1.2.6 release.

* Fri Aug 23 2002 TC Wan <tcwan@cs.usm.my>
- Updated for 1.2.5 release.

* Fri Aug  7 2002 TC Wan <tcwan@cs.usm.my>
- Cleaned up Makefile.in, build both x11 and sdl versions

* Fri Aug  2 2002 TC Wan <tcwan@cs.usm.my>
- Updated for 1.2.5 prerelease version

* Thu Jul 18 2002 TC Wan <tcwan@cs.usm.my>
- Missing runapp in install list, added testfiles package.
- Cleanup *.pyc after an uninstall

* Tue Jul 16 2002 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for RH 7.3
