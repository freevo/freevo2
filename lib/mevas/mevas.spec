Summary: Mevas (MeBox Canvas) is a canvas library for Python.
Name: mevas
Version: 0.0.2
Release: 1
License: LGPL
Group: System Environment/Libraries

Source: http://sault.org/mebox/downloads/mevas/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/root-%{name}-%{version}
Prefix: %{_prefix}

BuildRequires: pyimlib2 >= 0.0.6
BuildRequires: python >= 2.2

%description
Mevas (MeBox Canvas) is canvas library for Python that supports
multiple image libraries and display backends.

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
* Sat Aug 14 2004 Jason Tackaberry <tack@sault.org> - 0.0.2-1
- Initial package
