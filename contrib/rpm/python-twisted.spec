%define pyver %(python -c 'import sys; print sys.version[:3]')

Summary: Event-based framework for internet applications
Name: python-twisted
Version: 1.0.7
Release: 1_freevo
Source0: Twisted-%{version}.tar.bz2
License: LGPL
Group: Development/Python
URL: http://www.twistedmatrix.com/
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}

%description
It includes a web server, a telnet server, a multiplayer RPG engine, a 
generic client and server for remote object access, and APIs for creating 
new protocols.

%package doc
Summary: Documentation for Twisted (Event-based framework for internet applications)
Group: Development/Python

%description doc
Documentation for Twisted API. 

%prep
%setup -q -n Twisted-%version
mkdir manpages
mv doc/man/*.1 manpages

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --no-compile --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%_mandir/man1
install -m 644 manpages/*.1 $RPM_BUILD_ROOT%_mandir/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%_libdir/python%pyver/site-packages/twisted
%_bindir/*
%_mandir/man1/*
%doc CREDITS LICENSE README ChangeLog

%files doc
%defattr(-,root,root)
%doc doc

%changelog
* Tue Sep 16 2003 TC Wan <tcwan@cs.usm.my>
- Repackaged 1.0.7 for Redhat 

* Sun Aug 24 2003 Frederic Lepied <flepied@mandrakesoft.com> 1.0.6-1mdk
- initial Mandrake Linux packaging

# end of file
