%define pyver %(python -c 'import sys; print sys.version[:3]')

Summary: Python fast checksum module
Name: python-fchksum
Version: 1.7.1
Release: 1_freevo
Source0: %{name}-%{version}.tar.gz
Copyright: GPL2
Group: Development/Libraries
URL: http://www.dakotacom.net/~donut/programs/
BuildRoot: %{_tmppath}/%{name}-buildroot

%description
    This module provides quick and easy functions to find checksums of files.
    It supports md5, crc32, cksum, bsd-style sum, and sysv-style sum.
    The advantage of using fchksum over the python md5 and zlib(.crc32)
    modules is both ease of use and speed.  You only need to tell it the
    filename and the actual work is done by C code.  Compared to the
    implementing a read loop in python with the standard python modules,
    fchksum is up to 2.0x faster in md5 and 1.1x faster in crc32.
    
    All checksum functions take a filename as a string, and optional callback
    function, and callback delay (in seconds), and return a tuple (checksum,
    size).  An empty string may be substituted for filename to read from
    stdin.  The returned size is always a python Long, and the checksum
    return type varies depending on the function.

%prep
%setup 

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --no-compile --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT/%{_includedir}/python%{pyver}
cp *h $RPM_BUILD_ROOT/%{_includedir}/python%{pyver}

cat >>INSTALLED_FILES <<EOF
%{_includedir}/python%{pyver}
%doc README COPYING Changelog PKG-INFO
%doc test
EOF


%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Sep 17 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
