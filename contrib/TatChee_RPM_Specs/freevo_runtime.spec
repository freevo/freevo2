%define _target x11
Summary:	Freevo_runtime
Name:		freevo_runtime
Version:	1
Release:	1
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}%{version}.tar.gz
URL:		http://freevo.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/%{name}%{version}

%description
This package contains the Freevo runtime. It contains an executable,
freevo_rt, and dynamic link libraries for running Freevo.

You need the main Freevo package (and possibly the freevo_apps package too)
in order to run Freevo. It should be installed in "../freevo".

Please see "../freevo/README" for more information on how to use Freevo,
or the website at http://freevo.sourceforge.net.


%prep
%setup  -n %{name}%{version}
#%patch -p1

%build
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}
cp -av . %{buildroot}%{_prefix}

%clean
rm -rf $RPM_BUILD_ROOT

%post

%preun 

%files
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_prefix}
%attr(755,root,root) %dir %{_prefix}/PIL
%attr(755,root,root) %{_prefix}/freevo_rt
%attr(755,root,root) %{_prefix}/*.so
%attr(755,root,root) %{_prefix}/*.so.*
%attr(644,root,root) %{_prefix}/preloads
%attr(644,root,root) %{_prefix}/VERSION
%attr(644,root,root) %{_prefix}/PIL/*.py*
%attr(755,root,root) %{_prefix}/PIL/*.so
%doc ChangeLog COPYING README 

%changelog
* Fri Aug  23 2002 TC Wan <tcwan@cs.usm.my>
Initial Spec file for RH 7.3. Can't use %install as it strips the archived code from freevo_rt
