Name:               freevo
Summary:            A Linux PVR System
Version:            1.4
Release:            4
Source:             %{name}-%{version}rc4.tar.gz
Source1:            README.SUSE
Source2:            freevo.daily
Source3:            freevo.init
Source4:            freevo_record.init
Source5:            sysconfig.freevo
Source6:            freevo_web.init
Patch:              %{name}-1.4rc4-nodocs.patch
Patch1:             %{name}-1.4rc4-nooptimise.patch
Copyright:          GPL
Group:              Development/Libraries/Python
URL:                http://www.freevo.org/
BuildArchitectures: noarch
BuildRoot:          %{_tmppath}/%{name}-buildroot
Prefix:             %{_prefix}
Requires:           python python-mmpython python-imaging python-pygame
Requires:           python-Twisted perl-xmltv MPlayer MPlayer-suite lirc
BuildRequires:      python-devel python-mmpython python-imaging python-pygame
BuildRequires:      python-Twisted

%description
Freevo is an open-source digital video jukebox (PVR, DVR) based on Linux.

Freevo can be used both for a standalone PVR computer with a TV+remote, as
well as on a regular desktop computer using the monitor and keyboard.

Authors:
--------
    Krister Lagerstrom <krister-freevo@kmlager.com>
    Aubin Paul <aubin@outlyer.org>
    Dirk Meyer <dmeyer@tzi.de>
    Gustavo Sverzut Barbieri <gsbarbieri@yahoo.com.br>
    Rob Shortt <rob@tvcentric.com>
    Jason Ball <jason.ball@ce.com.au>
    Thomas Malt <thomas@malt.no>

%prep
%setup -q -n %{name}-%{version}rc4
%patch
%patch1

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -d -m 0755 $RPM_BUILD_ROOT/etc/freevo
install -d -m 1777 $RPM_BUILD_ROOT/var/cache/freevo
install -D -m 0755 %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.daily/freevo
install -D -m 0755 %{SOURCE3} $RPM_BUILD_ROOT/etc/init.d/freevo
install -D -m 0755 %{SOURCE4} $RPM_BUILD_ROOT/etc/init.d/freevo_record
install -D -m 0755 %{SOURCE6} $RPM_BUILD_ROOT/etc/init.d/freevo_web
install -d $RPM_BUILD_ROOT/usr/sbin
ln -sf ../../etc/init.d/freevo $RPM_BUILD_ROOT/usr/sbin/rcfreevo
ln -sf ../../etc/init.d/freevo_record $RPM_BUILD_ROOT/usr/sbin/rcfreevo_record
ln -sf ../../etc/init.d/freevo_web $RPM_BUILD_ROOT/usr/sbin/rcfreevo_web
install -D -m 0644 %{SOURCE5} $RPM_BUILD_ROOT/var/adm/fillup-templates/sysconfig.freevo
cp %{SOURCE1} .
%suse_update_desktop_file -c -i freevo Freevo "Linux PVR" freevo Player Application AudioVideo


%clean
rm -rf $RPM_BUILD_ROOT

%post
%{fillup_only}
echo "Please read /usr/share/doc/packages/freevo/README.SUSE for setup information"

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc BUGS COPYING ChangeLog FAQ INSTALL README TODO local_conf.py.example Docs
%doc README.SUSE
%dir /etc/freevo
%dir /var/cache/freevo
/etc/cron.daily/freevo
%config /etc/init.d/freevo
%config /etc/init.d/freevo_record
%config /etc/init.d/freevo_web
/var/adm/fillup-templates/sysconfig.freevo
/usr/sbin/rcfreevo
/usr/sbin/rcfreevo_record
/usr/sbin/rcfreevo_web
/usr/share/applications/*

%changelog

* Wed Nov 19 2003 - James Oakley <jfunk@funktronics.ca> - 1.4-4
- Added webserver init script

* Mon Nov 17 2003 - James Oakley <jfunk@funktronics.ca> - 1.4-3
- Init script fixes
- Desktop file

* Mon Nov 10 2003 - James Oakley <jfunk@funktronics.ca> - 1.4-2
- Update to 1.4rc4
- Add sysconfig, README.SUSE, and init scripts

* Tue Oct 21 2003 - James Oakley <jfunk@funktronics.ca> - 1.4-1
- Initial release
