%{expand: %%define pyver %(python2 -c 'import sys;print(sys.version[0:3])')}
%define tarballname PyXML

Summary: XML libraries for python2.
Name: PyXML2
Version: 0.7
Release: 4
Source: http://prdownloads.sourceforge.net/pyxml/PyXML-%{version}.tar.gz
License: Apacheish
Group: Development/Libraries
Patch0: PyXML-0.7-bpb.patch
Patch1: PyXML2-0.7-setup.py.patch
Requires: python2
URL: http://pyxml.sourceforge.net/
BuildRequires: python2 python2-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot

%description
An XML package for Python.  The distribution contains a
validating XML parser, an implementation of the SAX and DOM
programming interfaces and an interface to the Expat parser.
This version rebuilt for python2 on RedHat 7.x

%prep
%setup -q -n %{tarballname}-%{version}

%patch0 -p1
%patch1 -p1

pushd scripts
mv xmlproc_parse xmlproc_parse2
mv xmlproc_val xmlproc_val2
popd

%build
CFLAGS="$RPM_OPT_FLAGS" python2 setup.py build   --without-xpath --without-xslt

%install
rm -fr $RPM_BUILD_ROOT
python2 setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES    --without-xpath --without-xslt

python2 -O /usr/lib/python%pyver/compileall.py $RPM_BUILD_ROOT/usr/lib/python%pyver/site-packages
find $RPM_BUILD_ROOT/usr/lib/python%pyver -name "*pyo" | sed "s|$RPM_BUILD_ROOT||" >> INSTALLED_FILES
grep -v /usr/doc INSTALLED_FILES |grep -v LC_MESSAGES > installed_files


%clean
rm -rf $RPM_BUILD_ROOT

%files -f installed_files 
%defattr(-,root,root)
%doc LICENCE ANNOUNCE CREDITS README README.dom README.pyexpat README.sgmlop TODO doc/*
%lang(de) /usr/lib/python%pyver/site-packages/*/dom/de/LC_MESSAGES/4Suite.mo
%lang(en_US) /usr/lib/python%pyver/site-packages/*/dom/en_US/LC_MESSAGES/4Suite.mo
%lang(fr_FR) /usr/lib/python%pyver/site-packages/*/dom/fr_FR/LC_MESSAGES/4Suite.mo

%changelog
* Tue Feb 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 0.7-4
- Rebuild

* Mon Jan 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 0.7-3
- Remove xpath, xslt - use the ones in 4Suite
- patch the build script, it's broken

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Jan  1 2002 Trond Eivind Glomsrød <teg@redhat.com> 0.7-1
- PyXML 0.7

* Wed Dec  5 2001 Trond Eivind Glomsrød <teg@redhat.com> 0.6.6-2
- Add .pyo files
- Don't hardcode python version

* Tue Sep 18 2001 Trond Eivind Glomsrød <teg@redhat.com> 0.6.6-1
- 0.6.6
- Build for python 2.2

* Tue Jul 24 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add python-devel to BuildRequires (#49820)

* Tue Jul 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Mark the locale-specific files as such

* Thu Jun  7 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Don't obsolete itself

* Mon May  7 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Initial build, it's no longer part of 4Suite


