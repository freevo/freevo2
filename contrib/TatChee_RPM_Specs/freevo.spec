Summary:	Freevo
Name:		freevo
Version:	1.2.4
Release:	1
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}-%{version}.tar.gz
Patch0:		%{name}-%{version}-Makefile.patch
Patch1:		%{name}-%{version}-freevo_config.py.patch
Patch2:		%{name}-%{version}-boot_config.patch
Patch3:		%{name}-%{version}-scripts-python2.patch
URL:		http://freevo.sourceforge.net/
Requires:	python2
Requires:	mplayer, mpg321,xawtv, nvrec, libpng, zlib
Requires:	PyXML2 >= 0.7
Requires:	freetype >= 2.0.9
BuildRequires:	python2
BuildRequires:	freetype-devel >= 2.0.9
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/freevo

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer, mpg321 and nvrec to play and
record video and audio.

Note: This version does not have matroxfb support.

%prep
%setup 
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0

%build
python2 install.py sdl 
python2 install.py x11
#python2 install.py x11

%package boot
Summary: Files to enable a standalone Freevo system (started from initscript)
Group: Applications/Multimedia
Requires:	python2
Requires:	mplayer, mpg321,xawtv, nvrec, libpng, zlib
Requires:	PyXML2 >= 0.7
Requires:	freetype >= 2.0.9

%description boot
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer, mpg321 and nvrec to play and
record video and audio.

Note: This installs the initscripts necessary for a standalone Freevo system.

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}
#mkdir -p %{buildroot}%{_prefix}/matrox_g400
mkdir -p %{buildroot}%{_prefix}/{helpers,icons,osd_server,rc_client,skins}
#mkdir -p %{buildroot}%{_prefix}/matrox_g400/{fbset,matroxset}
mkdir -p %{buildroot}%{_prefix}/skins/{fonts,test1,test2}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}/etc/rc.d/init.d
install -m 755 freevo [a-e,g-z]*.py %{buildroot}%{_prefix}
install -m 755 helpers/* %{buildroot}%{_prefix}/helpers
install -m 644 icons/* %{buildroot}%{_prefix}/icons
#install -m 755 matrox_g400/*.sh matrox_g400/v4l1* %{buildroot}%{_prefix}/matrox_g400
#install -m 755 matrox_g400/fbset/fbset %{buildroot}%{_prefix}/matrox_g400/fbset
#install -m 755 matrox_g400/matroxset/matroxset %{buildroot}%{_prefix}/matrox_g400/matroxset
install -m 755 osd_server/osds_* osd_server/vtrelease %{buildroot}%{_prefix}/osd_server
install -m 755 rc_client/*py %{buildroot}%{_prefix}/rc_client
install -m 644 skins/fonts/* %{buildroot}%{_prefix}/skins/fonts
install -m 644 skins/test1/* %{buildroot}%{_prefix}/skins/test1
install -m 644 skins/test2/* %{buildroot}%{_prefix}/skins/test2
install -m 644 freevo_config.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m755 boot/freevo $RPM_BUILD_ROOT/etc/rc.d/init.d/freevo



%clean
rm -rf $RPM_BUILD_ROOT

%post
mkdir -p /var/cache/freevo
mkdir -p /var/cache/xmltv/logos
mkdir -p /var/log/freevo
chmod 777 /var/cache/{freevo,xmltv,xmltv/logos}

%preun 
rm -rf /var/log/freevo

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_prefix}/freevo
%attr(755,root,root) %{_prefix}/[a-e,g-z]*.py
%attr(755,root,root) %{_prefix}/helpers
%attr(644,root,root) %{_prefix}/icons/*
#%attr(755,root,root) %{_prefix}/matrox_g400
%attr(755,root,root) %{_prefix}/osd_server
%attr(755,root,root) %{_prefix}/rc_client
%attr(644,root,root) %{_prefix}/skins/fonts/*
%attr(644,root,root) %{_prefix}/skins/test1/*
%attr(644,root,root) %{_prefix}/skins/test2/*
%attr(644,root,root) %{_sysconfdir}/freevo/freevo_config.py
%doc BUGS Changelog FAQ INSTALL README TODO Docs/*

%files boot
%defattr(644,root,root,755)
%attr(755,root,root) /etc/rc.d/init.d/freevo
%attr(644,root,root) %{_sysconfdir}/freevo/boot_config

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

%changelog
* Tue Jul 16 2002 TC Wan <tcwan@cs.usm.my>
Initial SPEC file for RH 7.3
