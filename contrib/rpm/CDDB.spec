%define pyver %(python -c 'import sys; print sys.version[:3]')

Summary: Python modules for fetching information on audio CDs from CDDB
Name: CDDB
Version: 1.4
Release: 1_freevo
Source0: %{name}-%{version}.tar.gz
Copyright: GPL
Group: Development/Libraries
URL: http://sourceforge.net/projects/cddb-py/
BuildRoot: %{_tmppath}/%{name}-buildroot

%description
The dynamic duo of CDDB.py and DiscID.py, along with their side-kick C
module cdrommodule.so, provide an easy way for Python programs to
fetch information on audio CDs from CDDB (http://www.cddb.com/) -- a
very large online database of track listings and other information on
audio CDs.  UNIX platforms and Windows are both supported.


%prep
%setup 

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc README COPYING CHANGES cddb-info.py
EOF


%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Sep 17 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
