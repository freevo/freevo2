%define name pylirc
%define version 0.0.4
%define release 1_fc2

Summary: Python lirc module. See http://www.lirc.org for more info on lirc
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: lgpl
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Linus McCabe <pylirc.linus@mccabe.nu>

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

%changelog
* Mon May 31 2004  TC Wan <tcwan@cs.usm.my>
- Rebuilt for Fedora Core 2
