%define name mmpython
%define version 0.4.4
%define release 1_fc2

Summary: Module for retrieving information about media files
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Thomas Schueppel, Dirk Meyer <freevo-devel@lists.sourceforge.net>
Url: http://mmpython.sf.net

%description
UNKNOWN

%prep
%setup

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
