CFLAGS =
SUBDIRS = fbset matroxset

all: v4l1_to_mga v4l1_to_mga2 mga_bes_off fbset matroxset mga_vid.o

.PHONY: subdirs $(SUBDIRS) clean

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

mga_vid.o: mga_vid.c
	cc -g -O2  -Wall -D__KERNEL__  -DMODULE \
	-include /usr/src/linux/include/linux/modversions.h -I/usr/src/linux/include -c mga_vid.c

v4l1_to_mga: v4l1_to_mga.c frequencies.c frequencies.h
	cc -g -O2 v4l1_to_mga.c frequencies.c -o v4l1_to_mga

v4l1_to_mga2: v4l1_to_mga2.c frequencies.c frequencies.h fb.c fb.h
	cc -g -O2 v4l1_to_mga2.c frequencies.c fb.c -o v4l1_to_mga2

clean:
	-rm -f *.o v4l1_to_mga mga_bes_off v4l1_to_mga2
	cd matroxset ; make clean
	cd fbset ; make clean
