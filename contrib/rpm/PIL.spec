%define tarballname Imaging
%define version 1.1.4
%define corelib libImaging

Summary:        Python Imaging Library (PIL)
Name:           PIL
Version:        %{version}
Release:        2_freevo
License:        PIL_Freeware
Group:          Development/Libraries
Source:         http://www.pythonware.com/%{tarballname}-%{version}.tar.gz
Patch0:		%{tarballname}-%{version}-setup.patch
Patch1:		%{tarballname}-%{version}-Setup.in.patch
URL:            http://www.pythonware.com/
Provides:	python-imaging, Imaging
Requires:       python
Requires:       libpng
Requires:       libjpeg
Requires:       zlib
BuildRequires:  python
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-devel
BuildRequires:  zlib-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%description
The Python Imaging Library (PIL) adds image processing capabilities to
your Python environment.  This library provides extensive file format
support, an efficient internal representation, and fairly powerful
image processing capabilities.

%prep
%setup -n %{tarballname}-%{version}
%patch0 -p1
%patch1 -p1

%build
pushd %corelib
        %configure
        make
popd

python setup.py build

%install
python setup.py install --no-compile --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

cat >>INSTALLED_FILES <<EOF
%doc Doc Images Scripts
%doc README CONTENTS CHANGES-114
%doc selftest.py doctest.py 
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post

%preun

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Mon Sep 15 2003 TC Wan <tcwan@cs.usm.my>
Initial SPEC file for RH 9

