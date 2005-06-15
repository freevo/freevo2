PYMBUS=pyMbus-0.8.6
PYNOTIFIER=pyNotifier-0.3.5
URL=ftp://ftp.mbus.org/tzi/dmn/mbus/python/

all: pyimlib2 mevas pylibvisual pynotifier pymbus
	@echo creating links in site-packages
	@(test -e lib/mmpython && ln -sf ../lib/mmpython site-packages) || true
	@ln -sf ../src site-packages/freevo
	@echo make successfull


pyimlib2 mevas:
	@echo installing $@
	@( cd lib/$@ ; \
	  python setup.py install --install-lib=../../site-packages )

pylibvisual:
	@echo installing $@
	@-( cd lib/$@ ; \
	  python setup.py install --install-lib=../../site-packages )

pymbus: $(PYMBUS).tar.gz
	@( cd lib/$(PYMBUS) ; \
	    PYTHONPATH=../../site-packages python setup.py install \
	    --install-lib=../../site-packages )


pynotifier: $(PYNOTIFIER).tar.gz
	@( cd lib/$(PYNOTIFIER) ; \
	    python setup.py install --install-lib=../../site-packages )

%.tar.gz:
	@echo installing $@
	@(cd lib && test \! -e $@ && wget --passive-ftp $(URL)$@ && tar -zxf $@ ) || true


clean:
	find . -name *.pyo -exec rm {} \;
	find . -name *.so -exec rm {} \;
	find . -type d -name build -exec rm -rf {} 2>/dev/null \; || true
	rm -rf site-packages

install:
	for package in $(PYNOTIFIER) $(PYMBUS) pyepg pyimlib2 mevas \
		pywebinfo pylibvisual; do \
		(cd lib/$$package; \
		 rm -rf build ; \
		 python setup.py install; \
		 rm -rf build ); done

	rm -rf build
	python setup.py install
	rm -rf build
