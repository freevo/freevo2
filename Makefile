PYMBUS=pyMbus-0.8.6
PYNOTIFIER=pyNotifier-0.3.9
URL=ftp://ftp.mbus.org/tzi/dmn/mbus/python/

all: pylibvisual pynotifier pymbus pywebinfo mmpython
	@echo creating links in site-packages
	@ln -sf ../src site-packages/freevo
	@echo make successfull


pywebinfo:
	@echo installing $@
	@( cd lib/$@ ; \
	  python setup.py install --install-lib=$(PWD)/site-packages )

pylibvisual mmpython:
	echo $(PWD)
	@( test -e lib/$@ && cd lib/$@ && echo installing $@ && \
	  python setup.py install --install-lib=$(PWD)/site-packages \
		--install-scripts=$(PWD)/site-packages/scripts ) || \
	  echo skip $@

pymbus: $(PYMBUS).tar.gz
	@( cd lib/$(PYMBUS) ; \
	    PYTHONPATH=$(PWD)/site-packages python setup.py install \
	    --install-lib=$(PWD)/site-packages )


pynotifier: $(PYNOTIFIER).tar.gz
	@( cd lib/$(PYNOTIFIER) ; \
	    python setup.py install --install-lib=$(PWD)/site-packages )

%.tar.gz:
	@echo installing $@
	@(cd lib && test \! -e $@ && wget --passive-ftp $(URL)$@ && \
		tar -zxf $@ ) || true


clean:
	find . -name *.pyo -exec rm {} \;
	find . -name *.so -exec rm {} \;
	find . -type d -name build -exec rm -rf {} 2>/dev/null \; || true
	rm -rf site-packages

install:
	for package in $(PYNOTIFIER) $(PYMBUS) pywebinfo pylibvisual; do \
		(cd lib/$$package; \
		 rm -rf build ; \
		 python setup.py install; \
		 rm -rf build ); done

	rm -rf build
	python setup.py install
	rm -rf build
