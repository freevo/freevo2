Summary:	Freevo_runtime
Name:		freevo_runtime
Version:	3
Release:	2
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}%{version}.tar.gz
Patch:		%{name}%{version}-cgi.py.patch
URL:		http://freevo.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/%{name}%{version}
%define _sqldir lib/python2.2/site-packages

%description
This package contains the Freevo runtime. It contains an executable,
freevo_python, dynamic link libraries for running Freevo as well as a copy
of the standard Python 2.2 libraries.

You need the main Freevo package (and possibly the freevo_apps package too)
in order to run Freevo. It should be installed in "../freevo".

Please see "../freevo/README" for more information on how to use Freevo,
or the website at http://freevo.sourceforge.net.


%prep
%setup  -n %{name}%{version}
%patch -p1
cd %{_sqldir}; rm -rf *sql* *SQL*

%build
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}

%install
#cp -av . %{buildroot}%{_prefix}
install -s -m 755 *.so* %{buildroot}%{_prefix}
install -m 644 preloads VERSION %{buildroot}%{_prefix}
cp -av freevo_python %{buildroot}%{_prefix}
cp -av lib %{buildroot}%{_prefix}/lib

%clean
rm -rf $RPM_BUILD_ROOT

%post

%preun 

%files
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_prefix}
%attr(755,root,root) %{_prefix}/freevo_python
%attr(755,root,root) %{_prefix}/*.so.*
%attr(644,root,root) %{_prefix}/preloads
%attr(644,root,root) %{_prefix}/VERSION
%attr(755,root,root) %{_prefix}/lib
%doc ChangeLog COPYING README 

%changelog
* Thu Oct 17 2002 TC Wan <tcwan@cs.usm.my>
- Stripped symbols to reduce library size, removed mysql dependency

* Mon Oct 14 2002 TC Wan <tcwan@cs.usm.my>
- Rebuilt for freevo_runtime3

* Fri Aug 23 2002 TC Wan <tcwan@cs.usm.my>
- Initial Spec file for RH 7.3. Can't use install macro as it strips the archived code from freevo_rt
