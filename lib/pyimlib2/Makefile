all:
	python setup.py build
# Copy the module to the cwd for easier testing
	cp -f build/lib*/_Imlib2module.so .

install:
	python setup.py install
clean:
	python setup.py clean
	rm -rf build _Imlib2module.so *.pyc
