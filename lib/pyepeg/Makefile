all:
	python setup.py build
# Copy the module to the cwd for easier testing
	cp -f build/lib*/*.so .

install:
	python setup.py install
clean:
	python setup.py clean
	rm -rf build *.so *.pyc
