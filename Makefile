#
# Freevo main makefile
# 
# $Id$
#

SUBDIRS = matrox_g400 rc_client osd_server

all: subdirs runapp

.PHONY: all subdirs $(SUBDIRS) clean release install

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	-rm -f *.pyc *.o log_main_out log_main_err log.txt runapp
	cd matrox_g400 ; make clean
	cd rc_client ; make clean
	cd osd_server ; make clean


# XXX Real simple install procedure for now, but freevo is so small it doesn't really
# XXX matter
install: all
	-mv /usr/local/freevo /usr/local/freevo_old_`date +%Y%m%d_%H%M%S`
	-rm -rf /usr/local/freevo
	mkdir /usr/local/freevo
	cp -r * /usr/local/freevo
