all:
	@python setup.py build
	@cp build/lib*/libvisual.so .
install:
	${MAKE} all
	@cp libvisual.so ../../src/audio/plugins/

test:
	${MAKE} all
	@./test.py
clean:
	@echo "Cleaning files"
	@python setup.py clean
	rm -rf build/
	rm libvisual.so
