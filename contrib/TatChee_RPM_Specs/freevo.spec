%define geometry 800x600
%define display  x11
%define tv_norm  pal
%define chanlist europe-west
Summary:	Freevo
Name:		freevo
Version:	1.2.5
Release:	1
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}-%{version}.tar.gz
Patch0:		%{name}-%{version}-setup_build.py.patch
Patch1:		%{name}-%{version}-configure.patch
URL:		http://freevo.sourceforge.net/
Requires:	freevo_runtime
#Requires:	mplayer, mpg321, xawtv, nvrec
BuildRequires:	freevo_runtime
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer, mpg321 and nvrec to play and
record video and audio.

%prep
%setup  -n %{name}
%patch0 -p0
%patch1 -p0

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
mkdir -p %{buildroot}%{_prefix}/{boot,fbcon,gui,helpers,icons,plugins,rc_client,skins}
mkdir -p %{buildroot}%{_prefix}/plugins/{cddb,weather}
mkdir -p %{buildroot}%{_prefix}/plugins/weather/icons
mkdir -p %{buildroot}%{_prefix}/skins/{fonts,images,main1,xml}
mkdir -p %{buildroot}%{_prefix}/skins/xml/type1
mkdir -p %{buildroot}%{_prefix}/skins/{barbieri,dischi1,krister1,malt1}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/{Images,Movies,Music}

install -m 755 freevo freevo_xwin runapp freevo.conf skin.py strptime.py [a-e,g-r,t-z]*.py %{buildroot}%{_prefix}
install -m 644 fbcon/fbset.db %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/vtrelease %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/*.sh %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/matroxset/matroxset %{buildroot}%{_prefix}/fbcon/matroxset
install -m 644 gui/* %{buildroot}%{_prefix}/gui
install -m 644 helpers/* %{buildroot}%{_prefix}/helpers
install -m 644 icons/* %{buildroot}%{_prefix}/icons
install -m 755 plugins/cddb/*.py plugins/cddb/cdrom.so %{buildroot}%{_prefix}/plugins/cddb
install -m 644 plugins/weather/*.py plugins/weather/librarydoc.txt %{buildroot}%{_prefix}/plugins/weather
install -m 644 plugins/weather/icons/* %{buildroot}%{_prefix}/plugins/weather/icons
install -m 644 rc_client/*py %{buildroot}%{_prefix}/rc_client
install -m 644 skins/fonts/* %{buildroot}%{_prefix}/skins/fonts
install -m 644 skins/images/* %{buildroot}%{_prefix}/skins/images
install -m 644 skins/main1/* %{buildroot}%{_prefix}/skins/main1
install -m 644 skins/xml/type1/* %{buildroot}%{_prefix}/skins/xml/type1
install -m 644 skins/barbieri/* %{buildroot}%{_prefix}/skins/barbieri
install -m 644 skins/dischi1/* %{buildroot}%{_prefix}/skins/dischi1
install -m 644 skins/krister1/* %{buildroot}%{_prefix}/skins/krister1
install -m 644 skins/malt1/* %{buildroot}%{_prefix}/skins/malt1

install -m 644 freevo_config.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m 644 boot/URC-7201B00 %{buildroot}%{_prefix}/boot
install -m755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d


install -m 644 testfiles/Images/*.* %{buildroot}%{_cachedir}/freevo/testfiles/Images
install -m 644 testfiles/Movies/*.* %{buildroot}%{_cachedir}/freevo/testfiles/Movies
install -m 644 testfiles/Music/*.* %{buildroot}%{_cachedir}/freevo/testfiles/Music

%clean
rm -rf $RPM_BUILD_ROOT

%post
mkdir -p %{_cachedir}/freevo
mkdir -p %{_cachedir}/xmltv/logos
mkdir -p %{_logdir}/freevo
chmod 777 %{_cachedir}/{freevo,xmltv,xmltv/logos}

%preun 
rm -rf %{_logdir}/freevo
find %{_prefix} -name "*.pyc" |xargs rm -f

%files
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_prefix}
%attr(755,root,root) %dir %{_prefix}/fbcon
%attr(755,root,root) %dir %{_prefix}/gui
%attr(755,root,root) %dir %{_prefix}/helpers
%attr(755,root,root) %dir %{_prefix}/icons
%attr(755,root,root) %dir %{_prefix}/plugins
%attr(755,root,root) %dir %{_prefix}/plugins/cddb
%attr(755,root,root) %dir %{_prefix}/plugins/weather
%attr(755,root,root) %dir %{_prefix}/plugins/weather/icons
%attr(755,root,root) %dir %{_prefix}/rc_client
%attr(755,root,root) %dir %{_prefix}/skins
%attr(755,root,root) %dir %{_prefix}/skins/fonts
%attr(755,root,root) %dir %{_prefix}/skins/images
%attr(755,root,root) %dir %{_prefix}/skins/main1
%attr(755,root,root) %dir %{_prefix}/skins/xml
%attr(755,root,root) %dir %{_prefix}/skins/xml/type1
%attr(755,root,root) %dir %{_prefix}/skins/barbieri
%attr(755,root,root) %dir %{_prefix}/skins/dischi1
%attr(755,root,root) %dir %{_prefix}/skins/krister1
%attr(755,root,root) %dir %{_prefix}/skins/malt1
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(755,root,root) %{_prefix}/freevo
%attr(755,root,root) %{_prefix}/freevo_xwin
%attr(755,root,root) %{_prefix}/runapp
%attr(644,root,root) %{_prefix}/*.py
%attr(644,root,root) %{_prefix}/freevo.conf
%attr(644,root,root) %{_prefix}/fbcon/fbset.db
%attr(755,root,root) %{_prefix}/fbcon/vtrelease
%attr(755,root,root) %{_prefix}/fbcon/*.sh
%attr(755,root,root) %{_prefix}/fbcon/matroxset
%attr(644,root,root) %{_prefix}/helpers/*
%attr(644,root,root) %{_prefix}/icons/*
%attr(755,root,root) %{_prefix}/plugins/cddb/cdrom.so
%attr(644,root,root) %{_prefix}/plugins/cddb/*.py
%attr(644,root,root) %{_prefix}/plugins/weather/librarydoc.txt
%attr(644,root,root) %{_prefix}/plugins/weather/*.py
%attr(644,root,root) %{_prefix}/plugins/weather/icons/*
%attr(644,root,root) %{_prefix}/rc_client/*
%attr(644,root,root) %{_prefix}/skins/fonts/*
%attr(644,root,root) %{_prefix}/skins/images/*
%attr(644,root,root) %{_prefix}/skins/main1/*
%attr(644,root,root) %{_prefix}/skins/xml/type1/*
%attr(644,root,root) %{_prefix}/skins/barbieri/*
%attr(644,root,root) %{_prefix}/skins/dischi1/*
%attr(644,root,root) %{_prefix}/skins/krister1/*
%attr(644,root,root) %{_prefix}/skins/malt1/*
%config %{_sysconfdir}/freevo/freevo_config.py
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
%attr(644,root,root) %{_cachedir}/freevo/testfiles/Images/*
%attr(644,root,root) %{_cachedir}/freevo/testfiles/Movies/*
%attr(644,root,root) %{_cachedir}/freevo/testfiles/Music/*

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
ln -s %{_cachedir}/freevo/testfiles %{_prefix}

%preun testfiles
rm -f %{_prefix}/testfiles

%changelog
* Fri Aug 23 2002 TC Wan <tcwan@cs.usm.my>
Updated for 1.2.5 release.

* Fri Aug  7 2002 TC Wan <tcwan@cs.usm.my>
Cleaned up Makefile.in, build both x11 and sdl versions

* Fri Aug  2 2002 TC Wan <tcwan@cs.usm.my>
Updated for 1.2.5 prerelease version

* Thu Jul 18 2002 TC Wan <tcwan@cs.usm.my>
Missing runapp in install list, added testfiles package, cleanup *.pyc after an uninstall

* Tue Jul 16 2002 TC Wan <tcwan@cs.usm.my>
Initial SPEC file for RH 7.3
