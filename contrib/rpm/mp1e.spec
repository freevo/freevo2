Name: mp1e
Version: 1.9.5cvs
Release: 1_fc2
Summary: Real Time Software MPEG-1 Video/Audio Encoder
Copyright: GPL
Group: Applications/Multimedia
URL: http://zapping.sourceforge.net
Source: http://zapping.sourceforge.net/%{name}-%{version}.tar.bz2
Buildroot: %{_tmppath}/%{name}-root
PreReq: /sbin/install-info
Provides: mp1e

%description
Real Time Software MPEG-1 Video/Audio Encoder.

%prep
%setup -q

%build
%configure
make

%install
rm -rf %{buildroot}
%makeinstall

%clean
rm -rf %{buildroot}

%files
%defattr (-, root, root)
%doc ChangeLog README
%{_bindir}/mp1e
%{_mandir}/*

%changelog
* Tue Jun  1 2004 TC Wan <tcwan@cs.usm.my>
- Rebuilt for 1.9.5cvs on Fedora Core 2

* Mon Sep 15 2003 TC Wan <tcwan@cs.usm.my>
- Rebuilt for 1.9.3

* Fri Jun 7 2002 TC Wan <tcwan@cs.usm.my>
- Added v4l2 patch

* Tue Aug 8 2001 Iñaki García Etxebarria <garetxe@users.sf.net>
- Removed librte installation

* Tue May 8 2001 Iñaki García Etxebarria <garetxe@users.sourceforge.net>
- Created
