Summary: Simple DirectMedia Layer - Sample TrueType Font Library
Name: SDL_ttf
Version: 2.0.6
Release: 2_freevo
Source0: %{name}-%{version}.tar.gz
Patch0: %{name}-%{version}-freevo.patch
URL: http://www.libsdl.org/
Copyright: LGPL
Group: System Environment/Libraries
BuildRoot: /var/tmp/%{name}-buildroot
Prefix: %{_prefix}
BuildRequires: SDL-devel
BuildRequires: freetype-devel

%description
This library allows you to use TrueType fonts to render text in SDL
applications.

%package devel
Summary: Libraries, includes and more to develop SDL applications.
Group: Development/Libraries
Requires: %{name}
Requires: SDL-devel

%description devel
This library allows you to use TrueType fonts to render text in SDL
applications.

%prep
rm -rf ${RPM_BUILD_ROOT}

%setup
%patch0

%build
CFLAGS="$RPM_OPT_FLAGS" ./configure --prefix=%{prefix}
make

%install
rm -rf $RPM_BUILD_ROOT
make install prefix=$RPM_BUILD_ROOT/%{prefix}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README CHANGES COPYING
%{prefix}/lib/lib*.so.*
%{prefix}/lib/lib*.so

%files devel
%defattr(-,root,root)
%{prefix}/lib/*a
%{prefix}/include/SDL/

%changelog
* Mon Sep 23 2003 Sam Lantinga 
- Rebuilt for Freevo, patched
* Wed Jan 19 2000 Sam Lantinga 
- converted to get package information from configure
* Sun Jan 16 2000 Hakan Tandogan <hakan@iconsult.com>
- initial spec file

