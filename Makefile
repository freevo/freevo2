PYMBUS=pyMbus-0.8.2
PYNOTIFIER=pyNotifier-0.3.0
URL=ftp://ftp.mbus.org/tzi/dmn/mbus/python/

all: optional_packages links

links: lib/pyimlib2/_Imlib2module.so lib/$(PYMBUS) lib/$(PYNOTIFIER)
	@echo creating links in site-packages
	@ln -sf ../lib/pyimlib2/_Imlib2module.so site-packages/_Imlib2module.so
	@ln -sf ../lib/pyimlib2/Imlib2.py site-packages/Imlib2.py
	@test -e site-packages || mkdir site-packages
	@- rm -f site-packages/mmpython site-packages/epeg.so 2>/dev/null
	@-(test -e lib/mmpython && ln -sf ../lib/mmpython site-packages)
	@-(test -e lib/pyepeg/epeg.so && \
		ln -sf ../lib/pyepeg/epeg.so site-packages)
	@-(test -e lib/pylibvisual/libvisual.so && \
		ln -sf ../lib/pylibvisual/libvisual.so site-packages)
	@ln -sf ../lib/mevas/mevas ../lib/pyepg site-packages
	@ln -sf ../src site-packages/freevo
	@ln -sf ../lib/$(PYMBUS)/mbus site-packages
	@ln -sf ../lib/$(PYNOTIFIER)/notifier site-packages
	@echo make successfull


optional_packages:
	-(cd lib/pyepeg ; make )
	-(cd lib/pylibvisual ; make )


clean:
	(cd lib/pyimlib2 ; make clean)
	(cd lib/pyepeg ; make clean)
	rm -f site-packages/*


lib/pyimlib2/_Imlib2module.so:
	(cd lib/pyimlib2 ; make )


lib/$(PYMBUS):
	@echo installing $(PYMBUS)
	@(cd lib && wget --passive-ftp $(URL)$(PYMBUS).tar.gz && \
		tar -zxf $(PYMBUS).tar.gz && rm $(PYMBUS).tar.gz )


lib/$(PYNOTIFIER):
	@echo installing $(PYNOTIFIER)
	@(cd lib && wget --passive-ftp $(URL)$(PYNOTIFIER).tar.gz && \
		tar -zxf $(PYNOTIFIER).tar.gz && rm $(PYNOTIFIER).tar.gz )
