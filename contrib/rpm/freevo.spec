##########################################################################
# Set default freevo parameters
%define geometry 800x600
%define display  x11

##########################################################################


%if %{?_without_us_defaults:0}%{!?_without_us_defaults:1}
%define tv_norm  ntsc
%define chanlist us-cable
%else
%define tv_norm  pal
%define chanlist europe-west
%endif

##########################################################################
%define name freevo
%define version 1.5.2
%define release 1_fc2
%define _cachedir /var/cache
%define _logdir /var/log
%define _contribdir /usr/share/freevo/contrib
%define _docdir /usr/share/doc/%{name}-%{version}


Summary:        Freevo
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
#Source0: %{name}-%{version}%{release}.tar.gz
Source1: redhat-boot_config
Copyright: gpl
Group: Applications/Multimedia
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot
#BuildRequires: docbook-utils, wget
Requires: SDL >= 1.2.6, SDL_image >= 1.2.3, SDL_ttf >= 2.0.6, SDL_mixer >= 1.2.5
Requires: smpeg >= 0.4.4, freetype >= 2.1.4, util-linux
Requires: python >= 2.3, python-game >= 1.5.6, python-imaging >= 1.1.4, PyXML
Requires: mmpython >= 0.4.7, mx >= 2.0.5, python-numeric >= 23.1,
Requires: aumix >= 2.8, libjpeg >= 6b, libexif >= 0.5.10
Requires: python-Twisted >= 1.1.0
Requires: lsdvd
Prefix: %{_prefix}
URL:            http://freevo.sourceforge.net/

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

Available rpmbuild rebuild options :
--without: us_defaults use_sysapps compile_obj

#Note: In order to build the source package, you must have an Internet connection.
#If you need to configure a proxy server, set the shell environmental variable 'http_proxy'
#to the URL of the proxy server before rebuilding the package.
#
#E.g. for bash:
## export http_proxy=http://myproxy.server.net:3128

%package boot
Summary: Files to enable a standalone Freevo system (started from initscript)
Group: Applications/Multimedia
Requires:       %{name}

%description boot
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as mplayer and mencoder to play and record
video and audio.

Note: This installs the initscripts necessary for a standalone Freevo system.

%prep
rm -rf $RPM_BUILD_ROOT
#%setup -n freevo-%{version}%{release}
%setup -n freevo-%{version}

%build
find . -name CVS | xargs rm -rf
find . -name ".cvsignore" |xargs rm -f
find . -name "*.pyc" |xargs rm -f
find . -name "*.pyo" |xargs rm -f
find . -name "*.py" |xargs chmod 644

#./autogen.sh

env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

mkdir -p %{buildroot}%{_sysconfdir}/freevo
# The following is needed to let RPM know that the files should be backed up
touch %{buildroot}%{_sysconfdir}/freevo/freevo.conf

# boot scripts
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_bindir}
install -m 755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
#install -m 755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 boot/recordserver %{buildroot}%{_sysconfdir}/rc.d/init.d/freevo_recordserver
install -m 755 boot/webserver %{buildroot}%{_sysconfdir}/rc.d/init.d/freevo_webserver
install -m 755 boot/recordserver_init %{buildroot}%{_bindir}/freevo_recordserver_init
install -m 755 boot/webserver_init %{buildroot}%{_bindir}/freevo_webserver_init
install -m 644 -D %{SOURCE1} %{buildroot}%{_sysconfdir}/freevo/boot_config


mkdir -p %{buildroot}%{_logdir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo/{thumbnails,audio}
mkdir -p %{buildroot}%{_cachedir}/xmltv/logos
chmod 777 %{buildroot}%{_cachedir}/{freevo,freevo/thumbnails,freevo/audio,xmltv,xmltv/logos}
chmod 777 %{buildroot}%{_logdir}/freevo

%install
python setup.py install %{?_without_compile_obj:--no-compile} \
		--root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

install -m 644 local_conf.py.example %{buildroot}%{_docdir}

mkdir -p %{buildroot}%{_contribdir}/lirc
cp -av contrib/lirc %{buildroot}%{_contribdir}

cat >>INSTALLED_FILES <<EOF
#%doc BUGS COPYING ChangeLog FAQ INSTALL README TODO Docs local_conf.py.example
#%doc contrib/lirc 
%attr(644,root,root) %{_docdir}/local_conf.py.example
%attr(755,root,root) %dir %{_docdir}/installation
%attr(755,root,root) %dir %{_docdir}/plugin_writing
%attr(755,root,root) %dir %{_contribdir}/fbcon
%attr(755,root,root) %dir %{_contribdir}/lirc
%attr(644,root,root) %{_contribdir}/lirc/*
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(777,root,root) %dir %{_logdir}/freevo
%attr(777,root,root) %dir %{_cachedir}/freevo
%attr(777,root,root) %dir %{_cachedir}/freevo/audio
%attr(777,root,root) %dir %{_cachedir}/freevo/thumbnails
%attr(777,root,root) %dir %{_cachedir}/xmltv
%attr(777,root,root) %dir %{_cachedir}/xmltv/logos
%attr(644,root,root) %config %{_sysconfdir}/freevo/freevo.conf
#%attr(644,root,root) %config %{_sysconfdir}/freevo/record_config.py

EOF


%post
# Make backup of old freevo.conf here
if [ -s %{_sysconfdir}/freevo/freevo.conf ]; then
   cp %{_sysconfdir}/freevo/freevo.conf %{_sysconfdir}/freevo/freevo.conf.rpmsave
fi

# Copy old local_conf.py to replace dummy file
%{_bindir}/freevo setup --geometry=%{geometry} --display=%{display} \
        --tv=%{tv_norm} --chanlist=%{chanlist} \
	%{!?_without_use_sysapps:--sysfirst}

%preun
# Not safe to run this when upgrading!
#if [ -s %{_sysconfdir}/freevo/freevo.conf ]; then
#   cp %{_sysconfdir}/freevo/freevo.conf %{_sysconfdir}/freevo/freevo.conf.rpmsave
#fi
if [ -s %{_sysconfdir}/freevo/local_conf.py ]; then
   cp %{_sysconfdir}/freevo/local_conf.py %{_sysconfdir}/freevo/local_conf.py.rpmsave
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%files boot
%defattr(644,root,root,755)
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d
%attr(755,root,root) %{_bindir}/freevo_*
%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(644,root,root) %config %{_sysconfdir}/freevo/boot_config

%post boot
# Add the service, but don't automatically invoke it
# user has to enable it via ntsysv
if [ -x /sbin/chkconfig ]; then
     chkconfig --add freevo
     chkconfig --levels 234 freevo off
#     chkconfig --add freevo_dep
     chkconfig --add freevo_recordserver
     chkconfig --levels 234 freevo_recordserver off
     chkconfig --add freevo_webserver
     chkconfig --levels 234 freevo_webserver off
fi
depmod -a

%preun boot
if [ "$1" = 0 ] ; then
  if [ -x /sbin/chkconfig ]; then
     chkconfig --del freevo
#     chkconfig --del freevo_dep
     chkconfig --del freevo_recordserver
     chkconfig --del freevo_webserver
  fi
fi

%changelog
* Wed Nov  3 2004 TC Wan <tcwan@cs.usm.my>
- Updated for 1.5.2

* Mon Jul 19 2004 TC Wan <tcwan@cs.usm.my>
- Built 1.5.0 final

* Fri Jul  2 2004 TC Wan <tcwan@cs.usm.my>
- Added docs subdir for package cleanup, fixed contrib dir build warnings

* Tue Jun 29 2004 TC Wan <tcwan@cs.usm.my>
- Added python-numeric dependency, backup freevo.conf 
  just before creating new default copy

* Fri Jun 18 2004 TC Wan <tcwan@cs.usm.my>
- Updated for 1.5

* Fri Dec 19 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4.1

* Sat Nov 22 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4 final

* Tue Nov 11 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4-rc4 

* Tue Nov  4 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4-rc3 (name change)

* Sat Oct 25 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4-rc2

* Wed Oct  8 2003 TC Wan <tcwan@cs.usm.my>
- Fixed boot scripts for RH 9, disabled freevo_dep since it's obsolete (?)

* Fri Sep 26 2003 TC Wan <tcwan@cs.usm.my>
- Removed testfiles from build since it's no longer part of the package
  Cleaned up conditional flags

* Thu Sep 18 2003 TC Wan <tcwan@cs.usm.my>
- Added supporting directories and files to package

* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
