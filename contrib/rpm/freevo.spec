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
%define freevover 1.4
%define release rc2
%define runtimever 8.01

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log
%define _optimize 0

Summary:        Freevo
Name: %{name}
Version: %{freevover}
Release: %{release}
#Source0: %{name}-%{freevover}.tar.gz
Source0: %{name}-%{freevover}-%{release}.tgz
Source1: redhat-boot_config.fullbinary
#Patch0: freevo-%{freevover}-%{release}-freevo_dep.patch
Patch1:         %{name}-%{freevover}-runtime.patch

Copyright: gpl
Group: Applications/Multimedia
BuildRoot: %{_tmppath}/%{name}-buildroot
Requires:       %{name}-runtime >= %{runtimever}
%{?_without_use_sysapps:Requires:       %{name}-apps}
BuildRequires: docbook-utils, wget
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

%package runtime
Summary: Libraries used by freevo executable. Must be installed for freevo to work.
Version:        %{runtimever}
Obsoletes: freevo_runtime
Group: Applications/Multimedia
AutoReqProv: no

%description runtime
This directory contains the Freevo runtime. It contains an executable,
freevo_python, dynamic link libraries for running Freevo as well as a copy
of the standard Python 2.2.2 libraries.

Python 2.2.2 modules:
  CDDB DiscID Numeric PIL xmlplus xmms aomodule cdrom fchksum mmpython mx
  ogg pygame pygphoto pylirc pyshift twisted

Please see the website at http://freevo.sourceforge.net for more information
on how to use Freevo. The website also contains links to the source code
for all software included here.

%package apps
Summary: External applications used by freevo executable.
Obsoletes: freevo_apps
Group: Applications/Multimedia
Requires: %{name}-runtime >= %{runtimever}
AutoReqProv: no

%description apps
This directory contains the following external applications used by Freevo:
  oggenc mpe1 lame jpegtran cdparanoia aumix

NOTICE: Binaries of Media Player programs such as Mplayer, Xine and TVTime
are no longer included in the Apps package.
Please read the website at http://freevo.sourceforge.net for information on
where you can obtain these packages.

Note: This package is not manadatory if standalone versions of the external
applications are installed, though configuration issues may be minimized if
it is used.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -n freevo-%{freevover}%{release}
#%setup -n freevo

#%patch0 -p1 
%patch1 -p0 

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

mkdir -p %{buildroot}%{_prefix}/{runtime/apps,runtime/dll,runtime/lib}
install -m 644 runtime/*.py %{buildroot}%{_prefix}/runtime
install -m 644 runtime/preloads %{buildroot}%{_prefix}/runtime
install -m 644 runtime/README %{buildroot}%{_prefix}/runtime
install -m 644 runtime/VERSION %{buildroot}%{_prefix}/runtime
install -m 755 runtime/runapp %{buildroot}%{_prefix}/runtime
cp -av runtime/apps/* %{buildroot}%{_prefix}/runtime/apps
cp -av runtime/dll/* %{buildroot}%{_prefix}/runtime/dll
cp -av runtime/lib/* %{buildroot}%{_prefix}/runtime/lib


%install
#python setup.py install %{?_without_compile_obj:--no-compile} \
#		--root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p %{buildroot}%{_prefix}/contrib
cp -av i18n share src %{buildroot}%{_prefix}
cp -av contrib/examples contrib/fbcon contrib/xmltv %{buildroot}%{_prefix}/contrib
install -m 755 freevo %{buildroot}%{_prefix}
install -m 755 freevo_config.py %{buildroot}%{_prefix}

rm -f INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%{_prefix}/freevo
%{_prefix}/freevo_config.py
%{_prefix}/contrib
%{_prefix}/i18n
%{_prefix}/share
%{_prefix}/src
%doc BUGS COPYING ChangeLog FAQ INSTALL README TODO Docs local_conf.py.example
%doc contrib/lirc 
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

%files runtime
%defattr(644,root,root,755)
%{_prefix}/runtime/*.py
%{_prefix}/runtime/README
%{_prefix}/runtime/VERSION
%{_prefix}/runtime/preloads
%defattr(755,root,root,755)
%{_prefix}/runtime/apps/freevo_python
%{_prefix}/runtime/runapp
%{_prefix}/runtime/dll
%{_prefix}/runtime/lib

%files apps
%defattr(755,root,root,755)
%{_prefix}/runtime/apps/aumix
%{_prefix}/runtime/apps/cdparanoia
%{_prefix}/runtime/apps/jpegtran
%{_prefix}/runtime/apps/lame
%{_prefix}/runtime/apps/matroxset
%{_prefix}/runtime/apps/mp1e
%{_prefix}/runtime/apps/oggenc

%post
# Copy old local_conf.py to replace dummy file
cd %{_prefix}
./freevo setup --geometry=%{geometry} --display=%{display} \
        --tv=%{tv_norm} --chanlist=%{chanlist} \
	%{!?_without_use_sysapps:--sysfirst} 

%if %{!?_without_compile_obj:1}%{?_without_compile_obj:0}
./freevo setup --compile=%{_optimize},%{_prefix}
%endif

%preun
if [ -s %{_sysconfdir}/freevo/local_conf.py ]; then
   cp %{_sysconfdir}/freevo/local_conf.py %{_sysconfdir}/freevo/local_conf.py.rpmsave
fi

find %{_prefix} -name "*.pyc" |xargs rm -f
find %{_prefix} -name "*.pyo" |xargs rm -f

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
* Sat Oct 25 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.4-rc2

* Wed Oct 15 2003 TC Wan <tcwan@cs.usm.my>
- Revised for binary package

* Wed Oct  8 2003 TC Wan <tcwan@cs.usm.my>
- Fixed boot scripts for RH 9, disabled freevo_dep since it's obsolete (?)

* Fri Sep 26 2003 TC Wan <tcwan@cs.usm.my>
- Removed testfiles from build since it's no longer part of the package
  Cleaned up conditional flags

* Thu Sep 18 2003 TC Wan <tcwan@cs.usm.my>
- Added supporting directories and files to package

* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
