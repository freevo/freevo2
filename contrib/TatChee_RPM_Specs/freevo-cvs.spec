%define geometry 800x600
%define display  x11
%define tv_norm  pal
%define chanlist europe-west
%define _cvsdate 20021120
Summary:	Freevo
Name:		freevo
Version:	1.3.0
Release:	CVS%{_cvsdate}
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}-%{version}-%{_cvsdate}.tar.gz
#Patch0:		%{name}-%{version}-configure.patch
#Patch1:		%{name}-%{version}-configure.patch
#Patch2:		%{name}-%{version}-freevo_config.py.patch
URL:		http://freevo.sourceforge.net/
Requires:	freevo_runtime >= 3
BuildRequires:	freevo_runtime
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer and nvrec to play and record video 
and audio.

%prep
%setup  -n %{name}
#%patch0 -p1
#%patch1 -p0
#%patch2 -p0

./configure --geometry=%{geometry} --display=%{display} \
	--tv=%{tv_norm} --chanlist=%{chanlist}

%build
make clean; make
cd plugins/cddb; make

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
mkdir -p %{buildroot}%{_prefix}/{boot,eyed3,fbcon,gui,helpers,icons,image,plugins,rc_client,skins,tv,video}
mkdir -p %{buildroot}%{_prefix}/icons/64x64
mkdir -p %{buildroot}%{_prefix}/plugins/{cddb,weather}
mkdir -p %{buildroot}%{_prefix}/plugins/weather/icons
mkdir -p %{buildroot}%{_prefix}/skins/{fonts,images,main1,xml}
mkdir -p %{buildroot}%{_prefix}/skins/xml/type1
mkdir -p %{buildroot}%{_prefix}/skins/{aubin1,barbieri,dischi1,krister1,malt1}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/{Images,Movies,Music,tv-show-images}
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/Images/Show
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/Movies/skin.xml_Test

install -m 755 freevo freevo_xwin runapp skin.py strptime.py [A-Z,a-e,g-r,t-z]*.py %{buildroot}%{_prefix}
install -m 644 fbcon/fbset.db %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/vtrelease %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/*.sh %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/matroxset/matroxset %{buildroot}%{_prefix}/fbcon/matroxset
install -m 644 gui/* %{buildroot}%{_prefix}/gui
install -m 644 eyed3/* %{buildroot}%{_prefix}/eyed3
install -m 644 helpers/* %{buildroot}%{_prefix}/helpers
install -m 644 image/* %{buildroot}%{_prefix}/image
install -m 644 tv/* %{buildroot}%{_prefix}/tv
install -m 644 video/* %{buildroot}%{_prefix}/video
install -m 644 icons/[a-z]* %{buildroot}%{_prefix}/icons
install -m 644 icons/64x64/* %{buildroot}%{_prefix}/icons/64x64
install -m 755 plugins/cddb/*.py plugins/cddb/cdrom.so %{buildroot}%{_prefix}/plugins/cddb
install -m 644 plugins/weather/*.py plugins/weather/librarydoc.txt %{buildroot}%{_prefix}/plugins/weather
install -m 644 plugins/weather/icons/* %{buildroot}%{_prefix}/plugins/weather/icons
install -m 644 rc_client/* %{buildroot}%{_prefix}/rc_client
install -m 644 skins/fonts/* %{buildroot}%{_prefix}/skins/fonts
install -m 644 skins/images/* %{buildroot}%{_prefix}/skins/images
install -m 644 skins/main1/* %{buildroot}%{_prefix}/skins/main1
install -m 644 skins/xml/type1/* %{buildroot}%{_prefix}/skins/xml/type1
install -m 644 skins/aubin1/* %{buildroot}%{_prefix}/skins/aubin1
install -m 644 skins/barbieri/* %{buildroot}%{_prefix}/skins/barbieri
#install -m 644 skins/dischi1/* %{buildroot}%{_prefix}/skins/dischi1
#install -m 644 skins/krister1/* %{buildroot}%{_prefix}/skins/krister1
install -m 644 skins/malt1/* %{buildroot}%{_prefix}/skins/malt1

install -m 644 freevo.conf freevo_config.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m 644 boot/URC-7201B00 %{buildroot}%{_prefix}/boot
install -m755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d


install -m 644 testfiles/Images/*.jpg %{buildroot}%{_cachedir}/freevo/testfiles/Images
install -m 644 testfiles/Images/*.ssr %{buildroot}%{_cachedir}/freevo/testfiles/Images
install -m 644 testfiles/Images/Show/*.* %{buildroot}%{_cachedir}/freevo/testfiles/Images/Show
install -m 644 testfiles/Movies/*.avi testfiles/Movies/*.jpg testfiles/Movies/*.xml %{buildroot}%{_cachedir}/freevo/testfiles/Movies
install -m 644 testfiles/Movies/skin.xml_Test/* %{buildroot}%{_cachedir}/freevo/testfiles/Movies/skin.xml_Test
install -m 644 testfiles/Music/*.* %{buildroot}%{_cachedir}/freevo/testfiles/Music

%clean
rm -rf $RPM_BUILD_ROOT

%post
mkdir -p %{_cachedir}/freevo
mkdir -p %{_cachedir}/xmltv/logos
mkdir -p %{_logdir}/freevo
chmod 777 %{_cachedir}/{freevo,xmltv,xmltv/logos}
chmod 777 %{_logdir}/freevo

%preun 
rm -rf %{_logdir}/freevo
find %{_prefix} -name "*.pyc" |xargs rm -f

%files
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_prefix}
%attr(755,root,root) %dir %{_prefix}/fbcon
%attr(755,root,root) %dir %{_prefix}/plugins
%attr(755,root,root) %dir %{_prefix}/plugins/cddb
%{_prefix}/eyed3
%{_prefix}/gui
%{_prefix}/helpers
%{_prefix}/icons
%{_prefix}/image
%{_prefix}/rc_client
%{_prefix}/skins
%{_prefix}/tv
%{_prefix}/video


%attr(755,root,root) %dir %{_sysconfdir}/freevo

%attr(755,root,root) %{_prefix}/freevo
%attr(755,root,root) %{_prefix}/freevo_xwin
%attr(755,root,root) %{_prefix}/runapp
%attr(644,root,root) %{_prefix}/*.py
%attr(644,root,root) %{_prefix}/fbcon/fbset.db
%attr(755,root,root) %{_prefix}/fbcon/vtrelease
%attr(755,root,root) %{_prefix}/fbcon/*.sh
%attr(755,root,root) %{_prefix}/fbcon/matroxset

%attr(755,root,root) %{_prefix}/plugins/cddb/cdrom.so
%attr(644,root,root) %{_prefix}/plugins/cddb/*.py
%{_prefix}/plugins/weather

%config %{_sysconfdir}/freevo/freevo_config.py
%config %{_sysconfdir}/freevo/freevo.conf
%doc BUGS ChangeLog COPYING FAQ INSTALL* README TODO Docs/*

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
