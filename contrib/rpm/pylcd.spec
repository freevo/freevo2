%define name pylcd
%define version 0.2
%define release 1_fc2

Summary: Library interface for LCDproc daemon
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Tobias Klausmann <klausman-spam@schwarzvogel.de>
Url: http://www.schwarzvogel.de/software-pylcd.shtml
Requires: lcdproc

%description
PyLCD is a Library that interfaces with the LCDproc daemon. It abstracts the
network connection handling and provides a remap function for special
characters.

Information on LCDproc can be found at http://lcdproc.omnipotent.net

%prep
%setup

%build


%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc README COPYING Changes PKG-INFO 
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Thu Jun  3 2004 TC Wan <tcwan@cs.usm.my>
- Rebuilt for Fedora Core 2

* Fri Sep 26 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for RH 9 
