%define name Numeric
%define version 23.1
%define release 1_freevo

Summary: Numerical Extension to Python
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: Numerical Python Developers <numpy-developers@lists.sourceforge.net>
Provides: python-numeric python-numeric-devel
Url: http://numpy.sourceforge.net

%description

Numerical Extension to Python with subpackages.

        
The authors and maintainers of the subpackages are:
        
FFTPACK-3.1
        maintainer = "Numerical Python Developers"
        maintainer_email = "numpy-discussion@lists.sourceforge.net"
        description = "Fast Fourier Transforms"
        url = "http://numpy.sourceforge.net"
        
MA-12.2.0
        author = "Paul F. Dubois"
        description = "Masked Array facility"
        maintainer = "Paul F. Dubois"
        maintainer_email = "dubois@users.sf.net"
        url = "http://sourceforge.net/projects/numpy"
        
RNG-3.1
        author = "Lee Busby, Paul F. Dubois, Fred Fritsch"
        maintainer = "Paul F. Dubois"
        maintainer_email = "dubois@users.sf.net"
        description = "Cray-like Random number package."
        
%prep
%setup

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build


%install
python setup.py install --no-compile --root=$RPM_BUILD_ROOT

cat >INSTALLED_FILES <<EOF
%doc Demo
EOF
find $RPM_BUILD_ROOT -type f | sed -e "s|$RPM_BUILD_ROOT||g" >>INSTALLED_FILES



%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Sat Sep 27 2003 TC Wan <tcwan@cs.usm.my>
- Changed release to denote freevo
