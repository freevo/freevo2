# $Revision$, $Date$
Summary:	List dvd's content
Summary(pl):	Pokazywanie zawarto¶ci dvd
Name:		lsdvd
Version:	0.10
Release:	2_fc2
License:	GPL
Group:		Applications/File
Source0:	http://dl.sf.net/acidrip/lsdvd-%{version}.tar.gz
URL:		http://acidrip.thirtythreeandathird.net/lsdvd.html
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libdvdread-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Lsdvd allows to check the contents of the DVD as well as information
about particular tracks such as audio and subtitle languages etc.
Priceless when you want to play or rip video which is somewhere among
the dozens of useless promotional/trailer tracks.

%description -l pl
Lsdvd pozwala na sprawdzenie zawarto¶ci DVD oraz podaje informacje na
temat poszczególnych ¶cie¿ek, takie jak ilo¶æ i rodzaje ¶cie¿ek audio
czy napisów itd. Nieoceniony w sytuacji kiedy chcemy odtwarzaæ lub
przekodowaæ film, który jest gdzie¶ g³êboko ukryty po¶ród dziesi±tek
bezu¿ytecznych ¶cie¿ek z czo³ówkami i trailerami.

%prep
%setup -q

%configure --disable-dependency-tracking
%build

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog README
%attr(755,root,root) %{_bindir}/*

%define date	%(echo `LC_ALL="C" date +"%a %b %d %Y"`)
%changelog
* %{date} PLD Team <feedback@pld.org.pl>
All persons listed below can be reached at <cvs_login>@pld.org.pl

$Log$
Revision 1.1  2004/06/18 02:28:36  tcwan
Updated spec files for freevo 1.5 dependencies

* Mon May 31 2004 TC Wan <tcwan@cs.usm.my>
- Rebuilt for Fedora Core 2

Revision 1.8.1  2004/05/12 17:00:00  tcwan
- Removed depcomp dependency from build

Revision 1.8  2004/03/17 15:45:50  kloczek
- updated to 0.10.

Revision 1.7  2003/11/08 06:11:07  kloczek
- autoconf is added to BuildRequires (used in %build).

Revision 1.6  2003/11/07 20:48:07  kloczek
- added automake to BuildRequires (aclocal is used in %build).

Revision 1.5  2003/06/27 17:27:22  kloczek
- unifications and cleanups.

Revision 1.4  2003/06/15 15:18:58  kloczek
- unification in SF download URLs (use dl.sf.net only).

Revision 1.3  2003/02/25 12:55:33  qboosh
- working Source URL

Revision 1.2  2003/01/28 08:49:36  rrw
- filled missing information in spec;
- release 1;

Revision 1.1  2003/01/28 07:50:23  rrw
- initial revision;
