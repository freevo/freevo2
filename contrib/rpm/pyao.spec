%define pyver %(python -c 'import sys; print sys.version[:3]')

%define name pyao
%define version 0.82
%define release 1_fc2

Summary: A wrapper for the ao library
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Andrew Chatham <pyogg@andrewchatham.com>
Url: http://www.andrewchatham.com/pyogg/
Requires: libao
BuildRequires: libao

%description
This is a wrapper for libao, an audio device abstraction
library. libao is available with ogg/vorbis at http://www.xiph.org.


%prep
%setup

%build
#!/bin/sh

python config_unix.py

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT/%{_includedir}/python%{pyver}/%{name}
cp src/*h $RPM_BUILD_ROOT/%{_includedir}/python%{pyver}/%{name}

cat >>INSTALLED_FILES <<EOF
%{_includedir}/python%{pyver}
%doc README AUTHORS COPYING ChangeLog PKG-INFO
%doc test.py
EOF


%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Mon May 31 2004 TC Wan <tcwan@cs.usm.my>
- Rebuilt for Fedora Core 2

* Thu Sep 18 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for RH 9 (revised from version at vorbis.org)
