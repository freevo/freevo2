%define name pygoom
%define version 0.1
%define release 1_fc2

Summary: Goom Bindings for Python
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}.tgz
Copyright: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Requires: SDL, glib

%description
Python bindings for Goom.

%prep
%setup -n %{name}

%configure

%build
rm -rf $RPM_BUILD_ROOT
make -C plugins/goom
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc INSTALL
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Fri Jun 18 2004 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for FC 2 
