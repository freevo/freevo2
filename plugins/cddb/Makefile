all: cdrom.so

cdrom.so:
	$(CC) -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.2 -c cdrommodule.c -o cdrommodule.o
	$(CC) -shared cdrommodule.o -o cdrom.so

clean:
	-rm -f *.pyc *.o log_main_out log_main_err log.txt runapp cdrom.so cdrommodule.o
