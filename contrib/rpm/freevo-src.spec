##########################################################################
# Set default freevo parameters
%define geometry 800x600
%define display  x11
%define use_sysapps 1
%define _us_defaults 1
##########################################################################


%if %{_us_defaults}
%define tv_norm  ntsc
%define chanlist us-cable
%else
%define tv_norm  pal
%define chanlist europe-west
%endif

##########################################################################
%define name freevo-src
%define version 1.4
%define release 1

Summary:        Freevo
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Copyright: gpl
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
URL:            http://freevo.sourceforge.net/

%description
Freevo is a Linux application that turns a PC with a TV capture card
and/or TV-out into a standalone multimedia jukebox/VCR. It builds on
other applications such as xine, mplayer, tvtime and mencoder to play
and record video and audio.

%prep
%setup -n %{name}_%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

#./freevo setup --geometry=%{geometry} --display=%{display} \
#        --tv=%{tv_norm} --chanlist=%{chanlist} %{_sysfirst}

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Fri Sep  5 2003 TC Wan <tcwan@cs.usm.my>
- Initial SPEC file for python site-packages installation
