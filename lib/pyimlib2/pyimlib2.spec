Summary: Python wrapper for Imlib2
Name: pyimlib2
Version: 0.0.7
Release: 1
License: LGPL
Group: System Environment/Libraries

Source: http://sault.org/mebox/downloads/pyimlib2/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/root-%{name}-%{version}
Prefix: %{_prefix}

BuildRequires: imlib2-devel >= 1.1.1
BuildRequires: python >= 2.2

%description
pyimlib2 is small python module partially wrapping Imlib2. 

Imlib2 is an advanced replacement library for libraries like libXpm that
provides many more features with much greater flexibility and speed than
standard libraries, including font rasterization, rotation, RGBA space
rendering and blending, dynamic binary filters, scripting, and more.

%prep
%setup

%build
python setup.py build

%install
%{__rm} -rf %{buildroot}
python setup.py install --root=%{buildroot} --record=INSTALLED_FILES

cat >>INSTALLED_FILES << EOF
%doc README
EOF

%clean
%{__rm} -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-, root, root, 0755)


%changelog
* Mon Jun 13 2005 Jason Tackaberry <tack@sault.org> - 0.0.7-1
- Update to new directory structure
* Tue Feb 24 2004 Jason Tackaberry <tack@sault.org> - 0.0.1-1
- Initial package
