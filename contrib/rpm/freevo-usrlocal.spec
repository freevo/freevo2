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
%define name freevo-usrlocal
%define freevoname freevo
%define freevover 1.4
%define release rc2
%define runtimever 0.1

%define _prefix /usr/local/freevo
%define _cachedir /var/cache
%define _logdir /var/log
%define _optimize 0

Summary: Freevo no dependency package
Name: %{name}
Version: %{freevover}
Release: %{release}
#Source0: %{freevoname}-%{freevover}.tar.gz
Source0: %{freevoname}-%{freevover}%{release}.tar.gz
#Source1: redhat-boot_config.fullbinary

Copyright: gpl
Group: Applications/Multimedia
BuildRoot: %{_tmppath}/%{name}-buildroot
Requires:       %{freevoname}-runtime = %{runtimever}
%{?_without_use_sysapps:Requires:       %{name}-apps}
Prefix: %{_prefix}
URL:            http://freevo.sourceforge.net/

%description 
This is the no-dependency (other than freevo-runtime and mplayer/xine) 
freevo package for casual users interested in trying out freevo. 
The freevo package is installed in /usr/local/freevo.

Boot scripts to automatically startup freevo on a dedicated machine are 
not included in this package. To setup a dedicated freevo machine,
please install the respective required dependency packages and use the
normal freevo RPM package.

Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

NOTICE: Binaries of Media Player programs such as Mplayer, Xine and TVTime
are no longer included in the freevo package due to legal issues.
Please read the website at http://freevo.sourceforge.net for information on
where you can obtain these packages.

Available rpmbuild rebuild options :
--without: us_defaults use_sysapps compile_obj 

#Note: In order to build the source package, you must have an Internet connection.
#If you need to configure a proxy server, set the shell environmental variable 'http_proxy'
#to the URL of the proxy server before rebuilding the package.
#
#E.g. for bash:
## export http_proxy=http://myproxy.server.net:3128

%prep
rm -rf $RPM_BUILD_ROOT
%setup -n freevo-%{freevover}%{release}
#%setup -n freevo

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

mkdir -p %{buildroot}%{_logdir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo/{thumbnails,audio}
mkdir -p %{buildroot}%{_cachedir}/xmltv/logos
chmod 777 %{buildroot}%{_cachedir}/{freevo,freevo/thumbnails,freevo/audio,xmltv,xmltv/logos}
chmod 777 %{buildroot}%{_logdir}/freevo

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

%changelog
* Mon Nov  3 2003 TC Wan <tcwan@cs.usm.my>
- 1.4-rc2 usrlocal (no-dependency) package

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
