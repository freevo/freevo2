Summary: Python Media Meta Data module. 
Name: mmpython
Version: 0.2
Release: 1_freevo
Source0: %{name}_%{version}.tar.bz2
Copyright: lgpl
Group: Development/Libraries
URL:  http://sourceforge.net/projects/mmpython
BuildRoot: %{_tmppath}/%{name}-buildroot

%description
MMPython is a Media Meta Data retrieval framework. It retrieves metadata from mp3, ogg, avi,
jpg, tiff and other file formats. Among others it thereby parses ID3v2, ID3v1, EXIF, IPTC
and Vorbis data into an object oriented structure.

Further info can be obtained from http://sourceforge.net/projects/mmpython.

%prep
#%setup -n %{name}_%{version}
%setup -n %{name}

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --no-compile --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Sat Sep 20 2003 TC Wan <tcwan@cs.usm.my>
- Update to version 0.2

* Mon Sep  8 2003 TC Wan <tcwan@cs.usm.my>
- Disable generation of .pyc files using --no-compile flag

* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
