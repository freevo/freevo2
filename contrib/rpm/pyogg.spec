%define name pyogg
%define version 1.3
%define release 1_fc2

Summary: A wrapper for the Ogg libraries.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Andrew Chatham <pyogg@andrewchatham.com>
Url: http://www.andrewchatham.com/pyogg/
Requires: libogg
BuildRequires: libogg

%description
Ogg/Vorbis is available at http://www.xiph.org

There's not a whole lot you can do with this module by itself. You'll
probably also want the ogg.vorbis module, which can be found wherever
you got this.

You can now write Python programs to encode and decode Ogg Vorbis
files (encoding is quite a bit more involved). The module is
self-documenting, though I need to update quite a bit of it.


%prep
%setup

%build
#!/bin/sh

# This is just a simple script to be run before any automatic
# binary distribution building (like bdist or bdist_rpm). You
# probably don't have to worry about it.

python config_unix.py


%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc README AUTHORS COPYING ChangeLog NEWS PKG-INFO
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
