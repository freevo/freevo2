all: site-packages/_Imlib2module.so optional_packages links

links:
	test -e site-packages || mkdir site-packages
	- rm -f site-packages/mmpython site-packages/epeg.so 2>/dev/null
	-(test -e lib/mmpython && ln -sf ../lib/mmpython site-packages)
	-(test -e lib/pyepeg/epeg.so && ln -sf ../lib/pyepeg/epeg.so site-packages)
	-(test -e lib/pylibvisual/libvisual.so && ln -sf ../lib/pylibvisual/libvisual.so site-packages)
	ln -sf ../lib/mevas/mevas ../lib/pyepg site-packages
	ln -sf ../src site-packages/freevo
	echo make successfull

optional_packages:
	-(cd lib/pyepeg ; make )
	-(cd lib/pylibvisual ; make )


lib/pyimlib2/_Imlib2module.so:
	(cd lib/pyimlib2 ; make )

site-packages/_Imlib2module.so: lib/pyimlib2/_Imlib2module.so
	test -e site-packages || mkdir site-packages
	ln -sf ../lib/pyimlib2/_Imlib2module.so site-packages/_Imlib2module.so
	ln -sf ../lib/pyimlib2/Imlib2.py site-packages/Imlib2.py

clean:
	(cd lib/pyimlib2 ; make clean)
	(cd lib/pyepeg ; make clean)
	rm -f site-packages/*
