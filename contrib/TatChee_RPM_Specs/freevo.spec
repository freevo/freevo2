%define _target sdl
#%define _target x11
Summary:	Freevo
Name:		freevo
Version:	1.2.5
Release:	20020802
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}-%{version}-%{release}.tar.gz
Patch:		%{name}-%{version}-%{release}-rh73.patch
URL:		http://freevo.sourceforge.net/
Requires:	python2
Requires:	libpng, zlib
#Requires:	mplayer, mpg321, xawtv, nvrec
Requires:	PyXML2 >= 0.7
Requires:	freetype >= 2.0.9
BuildRequires:	python2
BuildRequires:	freetype-devel >= 2.0.9
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer, mpg321 and nvrec to play and
record video and audio.

Note: This version does not have matroxfb support.

%prep
%setup  -n %{name}-%{version}-%{release}
%patch -p1

./configure --osd=%{_target}

%build
make

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
#mkdir -p %{buildroot}%{_prefix}/matrox_g400
mkdir -p %{buildroot}%{_prefix}/{helpers,icons,osd_server,rc_client,skins}
#mkdir -p %{buildroot}%{_prefix}/matrox_g400/{fbset,matroxset}
mkdir -p %{buildroot}%{_prefix}/skins/{fonts,images,main1,test1,test2,dischi1,krister1}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}/etc/rc.d/init.d
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/{Images,Movies,Music}
install -m 755 freevo runapp skin.py startup.py strptime.py [a-e,g-r,t-z]*.py %{buildroot}%{_prefix}
install -m 755 helpers/* %{buildroot}%{_prefix}/helpers
install -m 644 icons/* %{buildroot}%{_prefix}/icons
#install -m 755 matrox_g400/*.sh matrox_g400/v4l1* %{buildroot}%{_prefix}/matrox_g400
#install -m 755 matrox_g400/fbset/fbset %{buildroot}%{_prefix}/matrox_g400/fbset
#install -m 755 matrox_g400/matroxset/matroxset %{buildroot}%{_prefix}/matrox_g400/matroxset
install -m 755 osd_server/osds_* osd_server/vtrelease %{buildroot}%{_prefix}/osd_server
install -m 755 rc_client/*py %{buildroot}%{_prefix}/rc_client
install -m 644 skins/fonts/* %{buildroot}%{_prefix}/skins/fonts
install -m 644 skins/images/* %{buildroot}%{_prefix}/skins/images
install -m 644 skins/main1/* %{buildroot}%{_prefix}/skins/main1
install -m 644 skins/test1/* %{buildroot}%{_prefix}/skins/test1
install -m 644 skins/test2/* %{buildroot}%{_prefix}/skins/test2
#install -m 644 skins/dischi1/* %{buildroot}%{_prefix}/skins/dischi1
install -m 644 skins/krister1/* %{buildroot}%{_prefix}/skins/krister1

install -m 644 freevo_config.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m755 boot/freevo %{buildroot}/etc/rc.d/init.d/freevo
install -m755 boot/freevo %{buildroot}/etc/rc.d/init.d/freevo


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
%attr(755,root,root) %dir %{_prefix}/icons
%attr(755,root,root) %dir %{_prefix}/skins
%attr(755,root,root) %dir %{_prefix}/skins/fonts
%attr(755,root,root) %dir %{_prefix}/skins/images
%attr(755,root,root) %dir %{_prefix}/skins/main1
%attr(755,root,root) %dir %{_prefix}/skins/test1
%attr(755,root,root) %dir %{_prefix}/skins/test2
#%attr(755,root,root) %dir %{_prefix}/skins/dischi1
%attr(755,root,root) %dir %{_prefix}/skins/krister1
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(755,root,root) %{_prefix}/freevo
%attr(755,root,root) %{_prefix}/runapp
%attr(755,root,root) %{_prefix}/*.py
%attr(755,root,root) %{_prefix}/helpers
%attr(644,root,root) %{_prefix}/icons/*
#%attr(755,root,root) %{_prefix}/matrox_g400
%attr(755,root,root) %{_prefix}/osd_server
%attr(755,root,root) %{_prefix}/rc_client
%attr(644,root,root) %{_prefix}/skins/fonts/*
%attr(644,root,root) %{_prefix}/skins/images/*
%attr(644,root,root) %{_prefix}/skins/main1/*
%attr(644,root,root) %{_prefix}/skins/test1/*
%attr(644,root,root) %{_prefix}/skins/test2/*
#%attr(644,root,root) %{_prefix}/skins/dischi1/*
%attr(644,root,root) %{_prefix}/skins/krister1/*
%attr(644,root,root) %{_sysconfdir}/freevo/freevo_config.py
%doc BUGS ChangeLog FAQ INSTALL README TODO Docs/*

%files boot
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(755,root,root) /etc/rc.d/init.d/freevo
%attr(644,root,root) %{_sysconfdir}/freevo/boot_config

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

%preun testfiles

%changelog
* Fri Aug  2 2002 TC Wan <tcwan@cs.usm.my>
Updated for 1.2.5 prerelease version

* Thu Jul 18 2002 TC Wan <tcwan@cs.usm.my>
Missing runapp in install list, added testfiles package, cleanup *.pyc after an uninstall

* Tue Jul 16 2002 TC Wan <tcwan@cs.usm.my>
Initial SPEC file for RH 7.3
