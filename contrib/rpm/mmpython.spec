%define name mmpython
%define version 0.1
%define release 1

Summary: Python Media Meta Data module. See http://sourceforge.net/projects/mmpython for more info.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}_%{version}.tar.gz
Copyright: lgpl
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}

%description
MMPython is a Media Meta Data retrieval framework. It retrieves metadata from mp3, ogg, avi,
jpg, tiff and other file formats. Among others it thereby parses ID3v2, ID3v1, EXIF, IPTC
and Vorbis data into an object oriented structure.

Further info can be obtained from http://sourceforge.net/projects/mmpython.

%prep
%setup -n %{name}_%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --no-compile --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Mon Sep  8 2003 TC Wan <tcwan@cs.usm.my>
- Disable generation of .pyc files using --no-compile flag

* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
