import os
import re
import logging

import config

log = logging.getLogger('config')

#
# Autodetect the CD/DVD drives in the system if not given in local_conf.py
#
# ROM_DRIVES == None means autodetect
# ROM_DRIVES == [] means ignore ROM drives
#

if config.ROM_DRIVES == None:
    config.ROM_DRIVES = []
    if os.path.isfile('/etc/fstab'):        
        re_cd        = re.compile( '^(/dev/cdrom[0-9]*|/dev/[am]?cd[0-9]+[a-z]?)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_cdrec     = re.compile( '^(/dev/cdrecorder[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_dvd       = re.compile( '^(/dev/dvd[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I )
        re_iso       = re.compile( '^([^ \t]+)[ \t]+([^ \t]+)[ \t]+(iso|cd)9660', re.I )
        re_automount = re.compile( '^none[ \t]+([^ \t]+).*supermount.*dev=([^,]+).*', re.I )
        re_bymountcd = re.compile( '^(/dev/[^ \t]+)[ \t]+([^ ]*cdrom[0-9]*)[ \t]+', re.I )
        re_bymountdvd= re.compile( '^(/dev/[^ \t]+)[ \t]+([^ ]*dvd[0-9]*)[ \t]+', re.I )
        fd_fstab = open('/etc/fstab')
        for line in fd_fstab:
            # Match on the devices /dev/cdrom, /dev/dvd, and fstype iso9660
            match_cd        = re_cd.match(line)
            match_cdrec     = re_cdrec.match(line)
            match_dvd       = re_dvd.match(line)
            match_iso       = re_iso.match(line)
            match_automount = re_automount.match(line)
            match_bymountcd = re_bymountcd.match(line)
            match_bymountdvd= re_bymountdvd.match(line)
            mntdir = devname = ''
            if match_cd or match_bymountcd:
                m = match_cd or match_bymountcd
                mntdir = m.group(2)
                devname = m.group(1)
                dispname = 'CD-%s' % (len(config.ROM_DRIVES)+1)
            elif match_cdrec: 
                mntdir = match_cdrec.group(2)
                devname = match_cdrec.group(1)
                dispname = 'CDREC-%s' % (len(config.ROM_DRIVES)+1)
            elif match_dvd or match_bymountdvd:
                m = match_dvd or match_bymountdvd
                mntdir = m.group(2)
                devname = m.group(1)
                dispname = 'DVD-%s' % (len(config.ROM_DRIVES)+1)
            elif match_iso:
                mntdir = match_iso.group(2)
                devname = match_iso.group(1)
                dispname = 'CD-%s' % (len(config.ROM_DRIVES)+1)
            elif match_automount:
                mntdir = match_automount.group(1)
                devname = match_automount.group(2)
                # Must check that the supermount device is cd or dvd
                if devname.lower().find('cd') != -1:
                    dispname = 'CD-%s' % (len(config.ROM_DRIVES)+1)
                elif devname.lower().find('dvd') != -1:
                    dispname = 'DVD-%s' % (len(config.ROM_DRIVES)+1)
	    	elif devname.lower().find('hd') != -1:
		    log.info('Trying to autodetect type of %s' % devname)
		    if os.path.exists('/proc/ide/' + re.sub(r'^(/dev/)', '', devname) +\
                                      '/media'):
		     if open('/proc/ide/'+  re.sub(r'^(/dev/)', '', devname) +\
                             '/media','r').read().lower().find('cdrom') !=1:
			    dispname = 'CD-%s' % (len(config.ROM_DRIVES)+1)
			    log.info("%s is a cdrom drive" %devname)
		    else:
			log.info("%s doesn't seems to be a cdrom drive" %devname)
                    	mntdir = devname = dispname = ''
                else:
                    mntdir = devname = dispname = ''

            if os.uname()[0] == 'FreeBSD':
                # FreeBSD-STABLE mount point is often device name + "c",
                # strip that off
                if devname and devname[-1] == 'c':
                    devname = devname[:-1]
                # Use native FreeBSD device names
                dispname = devname[5:]
 
            # Weed out duplicates
            for rd_mntdir, rd_devname, rd_dispname in config.ROM_DRIVES:
                if os.path.realpath(rd_devname) == os.path.realpath(devname):
                    log.info(('ROM_DRIVES: Auto-detected that %s is the same ' +
                              'device as %s, skipping') % (devname, rd_devname))
                    break
            else:
                # This was not a duplicate of another device
                if mntdir and devname and dispname:
                    config.ROM_DRIVES += [ (mntdir, devname, dispname) ]
                    log.info('Auto-detected and added "%s"' % config.ROM_DRIVES[-1])
        fd_fstab.close()
