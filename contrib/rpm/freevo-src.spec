%define _cvsdate %(date +%Y%m%d)

##########################################################################
# Set the following variables for each new build
%define freevoname freevo
%define sourceonly yes
%define freevover 1.3.2
%define freevorel pre5
%define runtimever 7

# Set default freevo parameters
%define geometry 800x600
%define display  x11
%define use_sysapps 0
%define _us_defaults 1
##########################################################################


%if %{_us_defaults}
%define tv_norm  ntsc
%define chanlist us-cable
%else
%define tv_norm  pal
%define chanlist europe-west
%endif

# Use system provided (not binary runtime) apps
%if %{use_sysapps}
%define _sysfirst "--sysfirst"
%else
%define _sysfirst ""
%endif

%define cvsrelease %(echo %{freevorel} | grep -c CVS)
%define prerelease %(echo %{freevorel} | grep -c pre)

# The following is needed as I can't get nested if-else-endif macros to work
%if %{cvsrelease}
%define realrelease 0
%else
%define realrelease %(echo %{prerelease} | grep -cv 1)
%endif

%define includeruntime %(echo %{sourceonly} | grep -cv yes)

%if %{includeruntime}
%define _tgzname freevo
%else
%define _tgzname freevo-src
%endif
##########################################################################

Summary:	Freevo
Name:		%{freevoname}
Version:	%{freevover}
Release:	%{freevorel}
License:	GPL
Group:		Applications/Multimedia
%if %{cvsrelease}
Source:		http://freevo.sourceforge.net/%{_tgzname}-%{version}-%{_cvsdate}.tar.gz
%endif
%if %{prerelease}
Source:		http://freevo.sourceforge.net/%{_tgzname}-%{version}-%{freevorel}.tar.gz
%endif
%if %{realrelease}
Source:		http://freevo.sourceforge.net/%{_tgzname}-%{version}.tar.gz
%endif

URL:		http://freevo.sourceforge.net/
Requires:	%{name}-runtime >= %{runtimever}
Requires:	%{name}-apps
%if %{includeruntime}
Patch0:		%{name}-%{version}-runtime.patch
Patch1:		%{name}-%{version}-Makefile.patch
Patch2:		%{name}-%{version}-mplayer_files.patch
%else
BuildRequires:	%{name}-runtime >= %{runtimever}
%endif
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
%if %{cvsrelease}
%setup  -n %{name}
%endif
%if %{prerelease}
%setup  -n %{name}-%{version}-%{freevorel}
%endif
%if %{realrelease}
%setup  -n %{name}-%{version}
%endif

%if %{includeruntime}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%else
mv runtime runtime-src
ln -s %{_prefix}/runtime .
%endif


%build
find . -name CVS | xargs rm -rf
find . -name ".cvsignore" |xargs rm -f
find . -name "*.pyc" |xargs rm -f
find . -name "*.py" |xargs chmod 644

make clean; make

./freevo setup --geometry=%{geometry} --display=%{display} \
	--tv=%{tv_norm} --chanlist=%{chanlist} %{_sysfirst}

%if %{includeruntime}
%package runtime
Summary: Libraries used by freevo executable. Must be installed for freevo to work.
Version:	%{runtimever}
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
  mplayer mencoder tvtime oggenc mpe1 lame jpegtran cdparanoia fceu aumix 
  
NOTICE: Please do not bug the mplayer developers with issues regarding the
        freevo distributed version of mplayer and mencoder.
	
Note: This package is not manadatory if standalone versions of the external
applications are installed, though configuration issues may be minimized if 
it is used.
%endif

%package boot
Summary: Files to enable a standalone Freevo system (started from initscript)
Group: Applications/Multimedia
Requires:	%{name}

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

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}
mkdir -p %{buildroot}%{_prefix}/fbcon/matroxset
mkdir -p %{buildroot}%{_prefix}/{boot,contrib/lirc,helpers}
%if %{includeruntime}
mkdir -p %{buildroot}%{_prefix}/{runtime/apps,runtime/dll,runtime/lib}
%endif
mkdir -p %{buildroot}%{_prefix}/{src,skins}
mkdir -p %{buildroot}%{_sysconfdir}/freevo
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p %{buildroot}%{_cachedir}/freevo/testfiles/{Images,Mame,Movies,Music,tv-show-images}

install -m 755 freevo freevo_xwin runapp %{buildroot}%{_prefix}
install -m 644 freevo_config.py setup_freevo.py %{buildroot}%{_prefix}
install -m 644 fbcon/fbset.db %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/vtrelease fbcon/*.sh %{buildroot}%{_prefix}/fbcon
install -m 755 fbcon/matroxset/matroxset %{buildroot}%{_prefix}/fbcon/matroxset

cp -av helpers/* %{buildroot}%{_prefix}/helpers

%if %{includeruntime}
install -m 644 runtime/*.py %{buildroot}%{_prefix}/runtime
install -m 644 runtime/preloads %{buildroot}%{_prefix}/runtime
#install -m 644 runtime/README %{buildroot}%{_prefix}/runtime
install -m 644 runtime/VERSION %{buildroot}%{_prefix}/runtime
cp -av runtime/apps/* %{buildroot}%{_prefix}/runtime/apps
cp -av runtime/dll/* %{buildroot}%{_prefix}/runtime/dll
cp -av runtime/lib/* %{buildroot}%{_prefix}/runtime/lib
%endif

cp -av src %{buildroot}%{_prefix}

cp -av skins %{buildroot}%{_prefix}

install -m 644 freevo.conf local_conf.py boot/boot_config %{buildroot}%{_sysconfdir}/freevo
install -m 644 boot/URC-7201B00 %{buildroot}%{_prefix}/boot
install -m 755 boot/freevo %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 boot/freevo_dep %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 contrib/lirc/* %{buildroot}%{_prefix}/contrib/lirc

cp -av testfiles/* %{buildroot}%{_cachedir}/freevo/testfiles

%clean
rm -rf $RPM_BUILD_ROOT

%post
cd %{_prefix}; ./freevo setup --compile=%{_optimize},%{_prefix}
mkdir -p %{_cachedir}/freevo
mkdir -p %{_cachedir}/freevo/{thumbnails,audio}
mkdir -p %{_cachedir}/xmltv/logos
mkdir -p %{_logdir}/freevo
chmod 777 %{_cachedir}/{freevo,freevo/thumbnails,freevo/audio,xmltv,xmltv/logos}
chmod 777 %{_logdir}/freevo

%preun 
rm -rf %{_logdir}/freevo
find %{_prefix} -name "*.pyc" |xargs rm -f

%files
%defattr(-,root,root,755)
%{_prefix}/freevo
%{_prefix}/freevo_xwin
%{_prefix}/runapp
%{_prefix}/fbcon
%{_prefix}/helpers
%{_prefix}/src
%{_prefix}/freevo_config.py
%{_prefix}/setup_freevo.py
%defattr(644,root,root,755)
%{_prefix}/contrib
%{_prefix}/skins

%attr(755,root,root) %dir %{_sysconfdir}/freevo
%attr(644,root,root) %config %{_sysconfdir}/freevo/freevo.conf
%attr(644,root,root) %config %{_sysconfdir}/freevo/local_conf.py
%doc BUGS ChangeLog COPYING FAQ INSTALL README TODO Docs 

%if %{includeruntime}
%files runtime
%defattr(644,root,root,755)
%{_prefix}/runtime/*.py
#%{_prefix}/runtime/README
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
%{_prefix}/runtime/apps/aumix
%{_prefix}/runtime/apps/cdparanoia
%{_prefix}/runtime/apps/fceu
%{_prefix}/runtime/apps/jpegtran
%{_prefix}/runtime/apps/lame
%{_prefix}/runtime/apps/mp1e
%{_prefix}/runtime/apps/oggenc
%defattr(-,root,root,755)
%{_prefix}/runtime/apps/mplayer
%{_prefix}/runtime/apps/tvtime
%endif

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
* Tue Jun 24 2003 TC Wan <tcwan@cs.usm.my>
- 1.3.2-preX and runtime v.7 cleanup

* Mon Apr 28 2003 TC Wan <tcwan@cs.usm.my>
- Rewrite build installation commands to recursively copy folder contents

* Mon Apr 14 2003 TC Wan <tcwan@cs.usm.my>
- Fixed SPEC file for source only builds, minor cleanups

* Tue Feb 25 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.3.2 builds, automatically detect -pre and CVS builds

* Tue Feb 18 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.3.2 cvs build

* Thu Feb 13 2003 TC Wan <tcwan@cs.usm.my>
- Updated for 1.3.1 cvs build
- Requires freevo-runtime for build as setup_build.py needs it
  to execute

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
