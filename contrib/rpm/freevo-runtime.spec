%define name freevo-runtime
%define runtimever 0.1
%define release 1

%define _prefix /usr/local/freevo/runtime

Summary: Libraries used by freevo nodeps executable. 
Name: %{name}
Version: %{runtimever}
Release: %{release}
Obsoletes: freevo_runtime
#Source0: %{name}-%{freevover}.tar.gz
Source0: %{name}-%{runtimever}.tgz
Patch0:  %{name}-%{runtimever}.patch

Copyright: gpl
Group: Applications/Multimedia
BuildRoot: %{_tmppath}/%{name}-buildroot
AutoReqProv: no
#BuildRequires: docbook-utils, wget
Prefix: %{_prefix}
URL:            http://freevo.sourceforge.net/

%description 
This directory contains the Freevo runtime. It contains an executable,
freevo_python, dynamic link libraries for running Freevo as well as a copy
of the standard Python 2.2.2 libraries.

External apps used by freevo (other than mplayer or xine) are also included
in the runtime.  Please read the website at http://freevo.sourceforge.net 
for information on where you can obtain these packages.

Please see the website at http://freevo.sourceforge.net for more information
on how to use Freevo. The website also contains links to the source code
for all software included here.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -n runtime

%patch0 -p1 

%build
find . -name CVS | xargs rm -rf
find . -name ".cvsignore" |xargs rm -f
find . -name "*.pyc" |xargs rm -f
find . -name "*.pyo" |xargs rm -f
find . -name "*.py" |xargs chmod 644

mkdir -p %{buildroot}%{_prefix}
install -m 644 *.py %{buildroot}%{_prefix}
install -m 644 preloads %{buildroot}%{_prefix}
install -m 644 README %{buildroot}%{_prefix}
install -m 644 VERSION %{buildroot}%{_prefix}
install -m 755 runapp %{buildroot}%{_prefix}
cp -av apps dll lib %{buildroot}%{_prefix}


%files 
%defattr(644,root,root,755)
%{_prefix}/*.py
%{_prefix}/README
%{_prefix}/VERSION
%{_prefix}/preloads
%defattr(755,root,root,755)
%{_prefix}/apps
%{_prefix}/runapp
%{_prefix}/dll
%{_prefix}/lib

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Nov  3 2003 TC Wan <tcwan@cs.usm.my>
- Stripped out non-runtime related stuff from freevo.spec to create freevo-runtime.spec

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
