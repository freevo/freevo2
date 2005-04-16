PYMBUS=pyMbus-0.8.5pre9
PYNOTIFIER=pyNotifier-0.3.3pre1
URL=ftp://ftp.mbus.org/tzi/dmn/mbus/python/

all: extra_packages lib/$(PYMBUS) lib/$(PYNOTIFIER)
	test -e site-packages || mkdir site-packages
	@echo creating links in site-packages
	@ln -sf ../lib/pyimlib2/_Imlib2module.so site-packages/_Imlib2module.so
	@ln -sf ../lib/pyimlib2/Imlib2.py site-packages/Imlib2.py
	@test -e site-packages || mkdir site-packages
	@-(test -e lib/mmpython && ln -sf ../lib/mmpython site-packages)
	@-(test -e lib/pylibvisual/libvisual.so && \
		ln -sf ../lib/pylibvisual/libvisual.so site-packages)
	@ln -sf ../lib/mevas/mevas ../lib/pyepg site-packages
	@ln -sf ../lib/pywebinfo/src site-packages/pywebinfo
	@ln -sf ../src site-packages/freevo
	@ln -sf ../lib/$(PYMBUS)/mbus site-packages
	@ln -sf ../lib/$(PYNOTIFIER)/notifier site-packages
	@echo make successfull


extra_packages:
	(cd lib/pyimlib2 ; make)
	-(cd lib/pylibvisual ; make)


clean:
	(cd lib/pyimlib2 ; make clean)
	-(cd lib/pylibvisual ; make clean )
	rm -rf site-packages


lib/$(PYMBUS):
	@echo installing $(PYMBUS)
	@(cd lib && wget --passive-ftp $(URL)$(PYMBUS).tar.gz && \
		tar -zxf $(PYMBUS).tar.gz && rm $(PYMBUS).tar.gz )


lib/$(PYNOTIFIER):
	@echo installing $(PYNOTIFIER)
	@(cd lib && wget --passive-ftp $(URL)$(PYNOTIFIER).tar.gz && \
		tar -zxf $(PYNOTIFIER).tar.gz && rm $(PYNOTIFIER).tar.gz )

install:
	for package in $(PYNOTIFIER) $(PYMBUS) pyepg pyimlib2 mevas pywebinfo; do \
		(cd lib/$$package; \
		 rm -rf build ; \
		 python setup.py install; \
		 rm -rf build ); done

	rm -rf build
	python setup.py install
	rm -rf build
