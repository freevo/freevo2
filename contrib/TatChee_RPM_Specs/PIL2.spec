# Make sure the correct pythonver (1.5, 2.2) and patch commands are enabled
%define pythonver 2.2
%define tarballname Imaging

Summary:	Python Imaging Library (PIL)
Name:		PIL2
Version:	1.1.3
Release:	1
License:	PIL_Freeware
Group:		Development/Libraries
Source:		http://www.pythonware.com/%{tarballname}-%{version}.tar.gz
Patch0:		%{tarballname}-%{version}-Setup.in.patch
Patch1:		%{tarballname}-%{version}-Scripts-1.5.patch
Patch2:		%{tarballname}-%{version}-Makefile.pre.in-2.2.patch
Patch3:		%{tarballname}-%{version}-Scripts-2.2.patch
URL:		http://www.pythonware.com/
Requires:	python
Requires:	libpng
Requires:	libjpeg 
Requires:	zlib
BuildRequires:	python
BuildRequires:	libpng-devel
BuildRequires:	libjpeg-devel 
BuildRequires:	zlib-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%define		_prefix		/usr/lib/python%{pythonver}
%define		corelib		libImaging

%description
The Python Imaging Library (PIL) adds image processing capabilities to
your Python environment.  This library provides extensive file format
support, an efficient internal representation, and fairly powerful
image processing capabilities.


%prep
%setup -n %{tarballname}-%{version}
%patch0 -p1

# For Python 1.5
#%patch1 -p0


# For Python 2.2
%patch2 -p1
%patch3 -p0

%build
pushd %corelib
        %configure
        make 
popd

make -f Makefile.pre.in boot
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_prefix}/site-packages/PIL
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}/MiniTest
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}/Scripts
install -m 644 PIL.pth %{buildroot}%{_prefix}/site-packages
install -m 755 *.so PIL/* %{buildroot}%{_prefix}/site-packages/PIL
install -m 755 MiniTest/* %{buildroot}%{_docdir}/%{name}-%{version}/MiniTest
install -m 755 Scripts/* %{buildroot}%{_docdir}/%{name}-%{version}/Scripts
install -m 644 README CHANGES-113 %{buildroot}%{_docdir}/%{name}-%{version}


%clean
rm -rf $RPM_BUILD_ROOT

%post

%preun 

%files
%defattr(644,root,root,755)
%dir %{_prefix}/site-packages
%dir %{_prefix}/site-packages/PIL
%attr(755,root,root) %{_prefix}/site-packages/PIL.pth
%attr(755,root,root) %{_prefix}/site-packages/PIL/*
%dir %{_docdir}/%{name}-%{version}
%dir %{_docdir}/%{name}-%{version}/MiniTest
%dir %{_docdir}/%{name}-%{version}/Scripts
%attr(644,root,root) %{_docdir}/%{name}-%{version}/*
%attr(755,root,root) %{_docdir}/%{name}-%{version}/MiniTest/*
%attr(755,root,root) %{_docdir}/%{name}-%{version}/Scripts/*

%changelog
* Mon Jul 15 2002 TC Wan <tcwan@cs.usm.my>
Initial SPEC file for RH 7.3
