Summary:	Freevo_apps
Name:		freevo_apps
Version:	1
Release:	2
License:	GPL
Group:		Applications/Multimedia
Source:		http://freevo.sourceforge.net/%{name}%{version}.tar.gz
URL:		http://freevo.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define _prefix /usr/local/%{name}

%description
This directory contains the Freevo external applications.
Right now that is only mplayer.

You need the main Freevo package (and possibly the freevo_apps package too)
in order to run Freevo. It should be installed in "../freevo".

Please see "../freevo/README" for more information on how to use Freevo,
or the website at http://freevo.sourceforge.net.


%prep
%setup  -n %{name}
rm -rf `find . -name CVS`

%build
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}

%install
cp -av . %{buildroot}%{_prefix}

%clean
rm -rf $RPM_BUILD_ROOT

%post

%preun 

%files
%defattr(644,root,root,755)
%attr(755,root,root) %dir %{_prefix}
%attr(755,root,root) %{_prefix}/mplayer
%doc README 

%changelog
* Mon Oct 14 2002 TC Wan <tcwan@cs.usm.my>
- Initial Spec file for RH 7.3. 
