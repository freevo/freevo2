##########################################################################
# Set default freevo parameters
%define geometry 800x600
%define display  x11

%define _us_defaults 1
%{?_without_us_defaults:%define _us_defaults 0}

# Use system provided (not binary runtime) apps (default)
%define _sysfirst "--sysfirst"
%{?_without_use_sysapps:%define _sysfirst ""}

# Compile python object files (default)
%{?_without_compile_obj:%define _nopycompile 1}
##########################################################################


%if %{_us_defaults}
%define tv_norm  ntsc
%define chanlist us-cable
%else
%define tv_norm  pal
%define chanlist europe-west
%endif

##########################################################################
%define name freevo-src
%define version 1.4
%define release 3_freevo
%define _cachedir /var/cache
%define _logdir /var/log


Summary:        Freevo
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: gpl
Group: Applications/Multimedia
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
URL:            http://freevo.sourceforge.net/

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

Available rpmbuild rebuild options :
--without: us_defaults use_sysapps compile_obj

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

%package testfiles
Summary: Sample multimedia files to test freevo
Group: Applications/Multimedia

%description testfiles
Test files that came with freevo. Placed in %{_cachedir}/freevo

%prep
rm -rf $RPM_BUILD_ROOT
#%setup -n %{name}_%{version}
%setup -n freevo

%build
find . -name CVS | xargs rm -rf
find . -name ".cvsignore" |xargs rm -f
find . -name "*.pyc" |xargs rm -f
find . -name "*.pyo" |xargs rm -f
find . -name "*.py" |xargs chmod 644

env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

mkdir -p %{buildroot}%{_sysconfdir}/freevo
# The following is needed to let RPM know that the files should be backed up
touch %{buildroot}%{_sysconfdir}/freevo/freevo.conf

# boot scripts
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_bindir}
install -m 755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 boot/record_server %{buildroot}%{_sysconfdir}/rc.d/init.d/freevo_recordserver
install -m 755 boot/webserver %{buildroot}%{_sysconfdir}/rc.d/init.d/freevo_webserver
install -m 755 boot/record_server_init %{buildroot}%{_bindir}/freevo_recordserver_init
install -m 755 boot/webserver_init %{buildroot}%{_bindir}/freevo_webserver_init
install -m 644 boot/boot_config %{buildroot}%{_sysconfdir}/freevo/


mkdir -p %{buildroot}%{_logdir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo
mkdir -p %{buildroot}%{_cachedir}/freevo/{thumbnails,audio}
mkdir -p %{buildroot}%{_cachedir}/xmltv/logos
chmod 777 %{buildroot}%{_cachedir}/{freevo,freevo/thumbnails,freevo/audio,xmltv,xmltv/logos}
chmod 777 %{buildroot}%{_logdir}/freevo

# test files
cp -av testfiles %{buildroot}%{_cachedir}/freevo/

%install
python setup.py install %{?_nopycompile:--no-compile} \
		--root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc BUGS COPYING ChangeLog FAQ INSTALL README TODO VERSION Docs local_conf.py.example
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
freevo setup --geometry=%{geometry} --display=%{display} \
        --tv=%{tv_norm} --chanlist=%{chanlist} %{_sysfirst} 

%preun
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

%files testfiles
%defattr(644,root,root,755)
%{_cachedir}/freevo/testfiles

%post boot
if [ -x /sbin/chkconfig ]; then
     chkconfig --add freevo
     chkconfig --add freevo_dep
     chkconfig --add freevo_recordserver
     chkconfig --add freevo_webserver
fi
depmod -a

%preun boot
if [ "$1" = 0 ] ; then
  if [ -x /sbin/chkconfig ]; then
     chkconfig --del freevo
     chkconfig --del freevo_dep
     chkconfig --del freevo_recordserver
     chkconfig --del freevo_webserver
  fi
fi

%changelog
* Thu Sep 18 2003 TC Wan <tcwan@cs.usm.my>
- Added supporting directories and files to package

* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
