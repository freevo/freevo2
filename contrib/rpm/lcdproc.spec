
Summary: 	LCDproc displays real-time system information on a 20x4 backlit LCD.
Name:   	lcdproc	
Version:	0.4.5
Release:	1_fc2
License:	GPL
Url:       	http://lcdproc.omnipotent.net
Group:     	Monitoring	
Source:    	http://lcdproc.omnipotent.net.net/%{name}-%{version}.tar.gz
Source1:	LCDd.init
BuildRoot: 	%{_tmppath}/%{name}-buildroot
BuildRequires:	ncurses-devel 

%description
LCDproc is a client/server suite inclduding drivers for all
kinds of nifty LCD displays. The server supports several
serial devices: Matrix Orbital, Crystal Fontz, Bayrad, LB216, 
LCDM001 (kernelconcepts.de), Wirz-SLI and PIC-an-LCD; and some 
devices connected to the LPT port: HD44780, STV5730, T6963, 
SED1520 and SED1330. Various clients are available that display 
things like CPU load, system load, memory usage, uptime, and a lot more. 
See also http://lcdproc.omnipotent.net. 

Available rpmbuild rebuild options :
--with: metar



%prep
rm -rf $RPM_BUILD_ROOT

%setup -q

%configure --enable-stat-nfs --enable-stat-smbfs --enable-drivers=hd44780,lcdm001,mtxorb,cfontz,curses,text,lb216,bayrad,glk,joy,t6963

%build
%{__make} CFLAGS="$RPM_OPT_FLAGS"

%install

%makeinstall
%{__make} install-strip DESTDIR=$RPM_BUILD_ROOT

# init
install -d 		$RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install %SOURCE1	$RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/LCDd

# conf files
install -d		$RPM_BUILD_ROOT%{_sysconfdir}/lcdproc
install LCDd.conf 	$RPM_BUILD_ROOT%{_sysconfdir}/lcdproc/LCDd.conf
touch scripts/lcdproc.conf  	$RPM_BUILD_ROOT%{_sysconfdir}/lcdproc/lcdproc.conf
echo "-s localhost -p 13666 C M X U P S" > \
			$RPM_BUILD_ROOT%{_sysconfdir}/lcdproc/lcdproc.conf


%if %{?_with_metar:0}%{!?_with_metar:1}
rm $RPM_BUILD_ROOT%{_bindir}/lcdmetar.pl
%endif

%post
if [ -x /sbin/chkconfig ]; then
     chkconfig --add LCDd
fi
depmod -a

%preun 
if [ "$1" = 0 ] ; then
  if [ -x /sbin/chkconfig ]; then
     chkconfig --del LCDd
  fi
fi



%clean
rm -rf $RPM_BUILD_ROOT 

%files
%defattr(-, root, root, 0755)
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man?/*
%dir 	%{_sysconfdir}/lcdproc
%config(noreplace)	%{_sysconfdir}/lcdproc/*
%doc README* INSTALL COPYING TODO ChangeLog 
%defattr(-, root, root, 0700)
%config(noreplace)	%{_sysconfdir}/rc.d/init.d/LCDd


%changelog
* Fri Sep 26 2003 TC Wan <tcwan@cs.usm.my>
- Fixed spec file for RH 9, made metar dependency optional

* Sun Oct  6 2002 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 0.4.3-2mdk
- Add docs

* Thu Sep 12 2002 Nicolas Chipaux <chipaux@mandrakesoft.com> 0.4.3-1mdk
- new release

* Fri Oct 26 2001 Rex Dieter <rdieter@unl.edu> 0.4.1-1
- --enable-stat-smbfs
- TODO: make server/client init scripts

* Mon Oct 22 2001 Rex Dieter <rdieter@unl.edu> -0
- first try, 0.4.1 
- --enable-stat-nfs

