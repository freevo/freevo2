PYTHON_LIB = /usr/local/lib/python2.2

.PHONY: clean mod_deps

all: freevo_rt

# The Installer application sometime misses when stuff has changed,
# so this rule always makes from scratch.
freevo_rt: Makefile clean Installer freevo_rt.py sysmodules.py
	python Installer/Makespec.py freevo_rt.py
	python Installer/Build.py freevo_rt.spec
	cp -a $(PYTHON_LIB)/site-packages/PIL distfreevo_rt
	python dllcopy.py
	mv distfreevo_rt freevo_rt

sysmodules.py: modlist.py
	python modlist.py $(PYTHON_LIB)

Installer: Installer/config.dat

Installer/config.dat:
	tar xvzf Archive/installer_5b3.1.tar.gz
	cp iu2.py Installer/iu.py
	(cd Installer/source/linux ; python Make.py ; make ; \
	cd ../.. ; python Configure.py)

clean:
	-rm -rf buildfreevo_rt distfreevo_rt freevo_rt freevo_rt.spec \
	warnfreevo_rt.txt sysmodules.py *.pyc

realclean:
	-rm -rf Installer

