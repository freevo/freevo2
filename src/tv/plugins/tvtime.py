#if 0 /*
# -----------------------------------------------------------------------
# tvtime.py - Temporary implementation of a TV function using tvtime
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.36  2004/06/06 17:15:10  mikeruelle
# removed some old bad code. mplayer debug has been superceded by childapp debug. the kill method is just plain bad.
#
# Revision 1.35  2004/05/29 23:01:03  mikeruelle
# make better use of freevo channels. getting better video group support slowly
#
# Revision 1.34  2004/03/22 01:24:40  mikeruelle
# tv channel padding so that the big number in tvtime is what us cable channel it is. channels must be in order to use this
#
# Revision 1.33  2004/03/21 18:30:04  mikeruelle
# allow for some special options during setup
#
# Revision 1.32  2004/02/23 17:56:39  mikeruelle
# add stop_osd=1 for vcr viewing to work. make vcr viewing work. add some commented out ch+/ch- video group handling. it is broken when you use numeric channel changing.
#
# Revision 1.31  2004/02/20 17:41:36  mikeruelle
# initial videogroups support.
#
# Revision 1.30  2004/02/06 01:15:06  mikeruelle
# use new events in tv context
#
# Revision 1.29  2004/01/14 18:39:45  mikeruelle
# suppress debug always showing
#
# Revision 1.28  2004/01/08 22:17:55  mikeruelle
# not needed and is now annoying because of new osd behavior in new tvtime releases.
#
# Revision 1.27  2004/01/06 00:58:40  mikeruelle
# better osd message support
#
# Revision 1.26  2004/01/06 00:29:45  mikeruelle
# fix regex for version detect and start osd message support
#
# Revision 1.25  2003/12/17 16:58:37  mikeruelle
# xmltv autochannel detect still occasionally sets things to numbers instead of strings
#
# Revision 1.24  2003/12/10 20:40:57  mikeruelle
# remove childthread use new childapp2 class
#
# Revision 1.23  2003/12/03 20:40:34  mikeruelle
# a hack for those who do not use freevo -fs
#
# Revision 1.22  2003/11/16 17:04:13  mikeruelle
# remove stupid found it message
#
# Revision 1.21  2003/11/08 13:23:56  dischi
# use os.path.join for configcmd
#
# Revision 1.20  2003/10/22 17:21:28  mikeruelle
# adding numeric channel changing and previous channel support
#
# Revision 1.19  2003/10/22 00:01:38  mikeruelle
# found another 4suite probelm, gonna look at minidom instead
#
# Revision 1.18  2003/10/15 20:17:07  mikeruelle
#
# new in this release:
# -use new childthread
# -writes tvtime.xml and stationlist.xml files to keep in sync
#  with freevo channels
# -merges stationlist.xml and tvtime.xml if they exist already
# -set tvtime xml parameters if you have 0.9.10 or newer
# -added support for custom tuned channels using FREQUENCY_TABLE
#
# Revision 1.12  2003/10/15 19:00:41  mikeruelle
# ok it should be ready for merge.
#
# Revision 1.17  2003/09/03 17:54:38  dischi
# Put logfiles into LOGDIR not $FREEVO_STARTDIR because this variable
# doesn't exist anymore.
#
# Revision 1.16  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.15  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif


# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

import time, os
import string
import threading
import signal
import cgi
import re
import popen2
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint
from cStringIO import StringIO

import util    # Various utilities
import osd
import rc      # The RemoteControl class.
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide
import event as em
from tv.channels import FreevoChannels

import plugin

# Set to 1 for debug output
DEBUG = config.DEBUG

# Create the OSD object
osd = osd.get_singleton()

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with tvtime.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # get config locations and mod times so we can check if we need
        # to regen xml config files (because they changed)
        self.mylocalconf = self.findLocalConf()
        self.myfconfig = os.environ['FREEVO_CONFIG']
        self.tvtimecache = os.path.join(config.FREEVO_CACHEDIR, 'tvtimecache')
        self.mylocalconf_t = os.path.getmtime(self.mylocalconf)
        self.myfconfig_t = os.path.getmtime(self.myfconfig)

        self.xmltv_supported = self.isXmltvSupported()

        #check/create the stationlist.xml and tvtime.xml
	self.createTVTimeConfig()

        # create the tvtime object and register it
        plugin.register(TVTime(), plugin.TV)

    def isXmltvSupported(self):
        helpcmd = '%s --help' %  config.TVTIME_CMD
        has_xmltv=False
        child = popen2.Popen3( helpcmd, 1, 100)
        data = child.childerr.readline() # Just need the first line
        if data:
            data = re.search( "^(tvtime: )?Running tvtime (?P<major>\d+).(?P<minor>\d+).(?P<version>\d+).", data )
            if data:
                _debug_("major is: %s" % data.group( "major" ))
                _debug_("minor is: %s" % data.group( "minor" ))
                _debug_("version is: %s" % data.group( "version" ))
                major = int(data.group( "major" ))
                minor = int(data.group( "minor" ))
                ver = int(data.group( "version" ))
                if major > 0:
                    has_xmltv=True
                elif major == 0 and minor == 9 and ver >= 10:
                    has_xmltv=True
        child.wait()
        return has_xmltv

    def findLocalConf(self):
        cfgfilepath = [ '.', os.path.expanduser('~/.freevo'), '/etc/freevo' ]
        mylocalconf = ''
        for dir in cfgfilepath:
            mylocalconf = os.path.join(dir,'local_conf.py')
            if os.path.isfile(mylocalconf):
                break
        return mylocalconf

    def createTVTimeConfig(self):
        tvtimedir = os.path.join(os.environ['HOME'], '.tvtime')
        if not os.path.isdir(tvtimedir):
            os.mkdir(tvtimedir)
        if self.needNewConfigs():
            self.writeStationListXML()
            self.writeTvtimeXML()
            self.writeMtimeCache()

    def needNewConfigs(self):
        tvtimedir = os.path.join(os.environ['HOME'], '.tvtime')
        if not os.path.isfile(os.path.join(tvtimedir, 'stationlist.xml')):
            return 1

        if not os.path.isfile(os.path.join(tvtimedir, 'tvtime.xml')):
            return 1

        if not os.path.isfile(self.tvtimecache):
            _debug_('no cache file')
            return 1

        (cachelconf, cachelconf_t, cachefconf_t) = self.readMtimeCache()

        cachelconf = cachelconf.rstrip()
        cachelconf_t = cachelconf_t.rstrip()
        cachefconf_t = cachefconf_t.rstrip()

        if not (cachelconf == self.mylocalconf): 
            _debug_('local_conf changed places')
            return 1

        if (long(self.mylocalconf_t) > long(cachelconf_t)):
            _debug_('local_conf modified')
            return 1

        if (long(self.myfconfig_t) > long(cachefconf_t)):
            _debug_('fconfig modified')
            return 1

	return 0

    def readMtimeCache(self):
	return file(self.tvtimecache, 'rb').readlines()

    def writeMtimeCache(self):
	fp = open(self.tvtimecache, 'wb')
        fp.write(self.mylocalconf)
	fp.write('\n')
        fp.write(str(self.mylocalconf_t))
	fp.write('\n')
        fp.write(str(self.myfconfig_t))
	fp.write('\n')
	fp.close()

    def writeTvtimeXML(self):
        tvtimexml = os.path.join(os.environ['HOME'], '.tvtime', 'tvtime.xml')
	configcmd = os.path.join(os.path.dirname(config.TVTIME_CMD), "tvtime-configure")
        #cf_norm, cf_input, cf_clist, cf_device = config.TV_SETTINGS.split()
	fc = FreevoChannels()
	vg = fc.getVideoGroup(config.TV_CHANNELS[0][2])
	cf_norm = vg.tuner_norm
	cf_input = vg.input_num
	cf_device = vg.vdev
        s_norm = cf_norm.upper()
	daoptions = ''
        if os.path.isfile(tvtimexml):
	    daoptions = ' -F ' + tvtimexml
        if self.xmltv_supported:
            daoptions += ' -d %s -n %s -t %s' % (cf_device, s_norm, config.XMLTV_FILE)
        else:
            daoptions += ' -d %s -n %s' % (cf_device, s_norm)
	if hasattr(config, "TV_TVTIME_SETUP_OPTS") and config.TV_TVTIME_SETUP_OPTS:
            daoptions += ' %s' % config.TV_TVTIME_SETUP_OPTS
        os.system(configcmd+daoptions)

    def writeStationListXML(self):
	self.createChannelsLookupTables()
        norm='freevo'
        tvnorm = config.CONF.tv
        tvnorm = tvnorm.upper()
        tvtimefile = os.path.join(os.environ['HOME'], '.tvtime', 'stationlist.xml')
        if os.path.isfile(tvtimefile):
            self.mergeStationListXML(tvtimefile, tvnorm, norm)
        else:
            self.writeNewStationListXML(tvtimefile, tvnorm, norm)

    def mergeStationListXML(self, tvtimefile, tvnorm, norm):
        _debug_("merging stationlist.xml")
        try:
            os.rename(tvtimefile,tvtimefile+'.bak')
        except OSError:
            return

        reader = Sax2.Reader()
        doc = reader.fromStream(tvtimefile+'.bak')
        mystations = doc.getElementsByTagName('station')
        gotlist = 0
        freevonode = None
        for station in mystations:
            myparent = station.parentNode
            if myparent.getAttribute('norm') == tvnorm and myparent.getAttribute('frequencies') == 'freevo':
                myparent.removeChild(station)
                freevonode = myparent
                gotlist=1
        if not gotlist:
            child = doc.createElement('list')
            freevonode = child
            child.setAttribute('norm', tvnorm)
            child.setAttribute('frequencies', 'freevo')
            doc.documentElement.appendChild(child)
        #put in the new children
        c = 0
        for m in config.TV_CHANNELS:
            mychan = m[2]
	    myband = self.lookupChannelBand(mychan)
            if myband == "Custom":
                mychan = config.FREQUENCY_TABLE.get(mychan)
                mychan = float(mychan)
                mychan = mychan / 1000.0
                mychan = "%.2fMHz" % mychan
            if (hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS and re.search('^\d+$', mychan)):
	        for i in range(c,int(mychan)):
                    fchild =  doc.createElement('station')
                    fchild.setAttribute('channel',str(i))
                    fchild.setAttribute('band',myband)
                    fchild.setAttribute('name',str(i))
                    fchild.setAttribute('active','0')
                    fchild.setAttribute('position',str(i))
                    freevonode.appendChild(fchild)
                    c = c + 1
            fchild =  doc.createElement('station')
            fchild.setAttribute('channel',mychan)
            fchild.setAttribute('band',myband)
            fchild.setAttribute('name',cgi.escape(m[1]))
            fchild.setAttribute('active','1')
            fchild.setAttribute('position',str(c))
            if self.xmltv_supported:
                fchild.setAttribute('xmltvid',m[0])
            freevonode.appendChild(fchild)
            c = c + 1
	# YUCK:
        # PrettyPrint the results to stationlistxml unfortuneately it
	# adds a bunch of stuff in comments at the end of the file
	# that causes the document not to load if we merge again later
	# so I print to a string buffer and then remove the offending
	# comments by truncating the output.
	strIO = StringIO()
        PrettyPrint(doc, strIO)
	mystr = strIO.getvalue()
	myindex = mystr.find('</stationlist>')
	mystr = mystr[:myindex+15]
	# how can 4suite be so stupid and still survive?
	mystr = mystr.replace('<!DOCTYPE stationlist PUBLIC "http://tvtime.sourceforge.net/DTD/stationlist1.dtd" "-//tvtime//DTD stationlist 1.0//EN">','<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">')
        fp = open(tvtimefile,'wb')
	fp.write(mystr)
        fp.close()


    def writeNewStationListXML(self, tvtimefile, tvnorm, norm):
        _debug_("writing new stationlist.xml")
        fp = open(tvtimefile,'wb')
        fp.write('<?xml version="1.0"?>\n')
        fp.write('<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">\n')
        fp.write('<stationlist xmlns="http://tvtime.sourceforge.net/DTD/">\n')
        fp.write('  <list norm="%s" frequencies="%s">\n' % (tvnorm, norm))

        c = 0
        for m in config.TV_CHANNELS:
            mychan = str(m[2])
	    myband = self.lookupChannelBand(mychan)
            if myband == "Custom":
                mychan = config.FREQUENCY_TABLE.get(mychan)
                mychan = float(mychan)
                mychan = mychan / 1000.0
                mychan = "%.2fMHz" % mychan
            if (hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS and re.search('^\d+$', mychan)):
	        for i in range(c,int(mychan)):
                    fp.write('    <station name="%s" active="0" position="%s" band="%s" channel="%s"/>\n' % (i,i,myband,i))
                    c = c + 1
            if self.xmltv_supported:
                fp.write('    <station name="%s" xmltvid="%s" active="1" position="%s" band="%s" channel="%s"/>\n' % (cgi.escape(m[1]), m[0], c, myband, mychan))
            else:
                fp.write('    <station name="%s" active="1" position="%s" band="%s" channel="%s"/>\n' % (cgi.escape(m[1]),c,myband,mychan))
            c = c + 1

        fp.write('  </list>\n')
        fp.write('</stationlist>\n')
        fp.close()

    def lookupChannelBand(self, channel):
        # check if we have custom
       
	#Aubin's auto detection code works only for numeric channels and
	#forces them to int.
	channel = str(channel)
       
        if config.FREQUENCY_TABLE.has_key(channel):
            _debug_("have a custom")
            return "Custom"
        elif (re.search('^\d+$', channel)):
            _debug_("have number")
	    if self.chanlists.has_key(config.CONF.chanlist):
                _debug_("found chanlist in our list")
	        return self.chanlists[config.CONF.chanlist]
	elif self.chans2band.has_key(channel):
            _debug_("We know this channels band.")
            return self.chans2band[channel]
        _debug_("defaulting to USCABLE")
        return "US Cable"

    def createChannelsLookupTables(self):
        chanlisttmp = [ ('us-bcast', 'US Broadcast'), ('us-cable', 'US Cable'), ('us-cable-hrc', 'US Cable'), ('japan-cable', 'Japan Cable'), ('japan-bcast', 'Japan Broadcast'), ('china-bcast', 'China Broadcast') ]
        self.chanlists = dict(chanlisttmp)
        chans_list = [('T' + str(x), 'US Two-Way') for x in range(7, 15)]
        chans_list += [('A' + str(x), 'China Broadcast') for x in range(1, 8)]
        chans_list += [('B' + str(x), 'China Broadcast') for x in range(1, 32)]
        chans_list += [('C' + str(x), 'China Broadcast') for x in range(1, 6)]
        chans_list += [('E' + str(x), 'VHF E2-E12') for x in range(1, 13)]
        chans_list += [('S' + str(x), 'VHF S1-S41') for x in range(1, 42)]
        chans_list += [('Z+1', 'VHF Misc'), ('Z+2', 'VHF Misc')]
        chans_list += [(chr(x), 'VHF Misc') for x in range(88, 91)]
        chans_list += [('K%0.2i' % x, 'VHF France') for x in range(1, 11)]
        chans_list += [('H%0.2i' % x, 'VHF France') for x in range(1, 20)]
        chans_list += [('K' + chr(x), 'VHF France') for x in range(66, 82)]
        chans_list += [('SR' + str(x), 'VHF Russia') for x in range(1, 20)]
        chans_list += [('R' + str(x), 'VHF Russia') for x in range(1, 13)]
        chans_list += [('AS5A', 'VHF Australia'), ('AS9A', 'VHF Australia')]
        chans_list += [('AS' + str(x), 'VHF Australia') for x in range(1, 13)]
        chans_list += [('H1', 'VHF Italy'), ('H2', 'VHF Italy')]
        chans_list += [(chr(x), 'VHF Italy') for x in range(65, 73)]
        chans_list += [('I' + str(x), 'VHF Ireland') for x in range(1, 10)]
        chans_list += [('U' + str(x), 'UHF') for x in range(21, 70)]
        chans_list += [('AU' + str(x), 'UHF Australia') for x in range(28, 70)]
        chans_list += [('O' + str(x), 'Australia Optus') for x in range(1, 58)]
	self.chans2band=dict(chans_list)


class TVTime:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.app_mode = 'tv'
	self.fc = FreevoChannels()
        self.current_vg = None

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                return pos
        print 'ERROR: Cannot find tuner channel "%s" in the TV channel listing' % tuner_channel
        return 0

    def TunerGetChannelInfo(self):
        return self.fc.getChannelInfo()

    def TunerGetChannel(self):
        return self.fc.getChannel()

    def Play(self, mode, tuner_channel=None, channel_change=0):

        if not tuner_channel:
            tuner_channel = self.fc.getChannel()
        vg = self.current_vg = self.fc.getVideoGroup(tuner_channel)

        if not vg.group_type == 'normal':
            print 'Tvtime only supports normal. "%s" is not implemented' % vg.group_type
            return

        if mode == 'tv' or mode == 'vcr':
            
            w, h = config.TV_VIEW_SIZE
	    cf_norm = vg.tuner_norm
	    cf_input = vg.input_num
	    cf_device = vg.vdev

            s_norm = cf_norm.upper()

            outputplugin = config.CONF.display
            if config.CONF.display == 'x11':
                outputplugin = 'Xv'
            if config.CONF.display == 'mga':
                outputplugin = 'mga'
            if config.CONF.display == 'dfbmga':
                outputplugin = 'directfb'

            if mode == 'vcr':
	        cf_input = '1'
		if hasattr(config, "TV_VCR_INPUT_NUM") and config.TV_VCR_INPUT_NUM:
		    cf_input = config.TV_VCR_INPUT_NUM

            self.fc.chan_index = self.TunerSetChannel(tuner_channel)

            if hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS:
	        mychan = tuner_channel
            else:
	        mychan = self.fc.chan_index

            _debug_('starting channel is %s' % mychan)

            command = '%s -D %s -k -I %s -n %s -d %s -f %s -c %s -i %s' % (config.TVTIME_CMD,
                                                                   outputplugin,
                                                                   w,
                                                                   s_norm,
                                                                   cf_device,
                                                                   'freevo',
                                                                   mychan,
								   cf_input)

            if osd.get_fullscreen() == 1:
                command += ' -m'
            else:
                command += ' -M'


        else:
            print 'Mode "%s" is not implemented' % mode  # BUG ui.message()
            return

        self.mode = mode

        mixer = plugin.getbyname('MIXER')

        # BUG Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # Start up the TV task
        self.app=TVTimeApp(command)        

        self.prev_app = rc.app() # ???
        rc.app(self)

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # BUG Hm.. This is hardcoded and very unflexible.
        if mixer and mode == 'vcr':
            mixer.setMicVolume(config.VCR_IN_VOLUME)
        elif mixer:
            mixer.setLineinVolume(config.TV_IN_VOLUME)
            mixer.setIgainVolume(config.TV_IN_VOLUME)
            
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        if DEBUG: print '%s: started %s app' % (time.time(), self.mode)
        
        
    def Stop(self, channel_change=0):
        mixer = plugin.getbyname('MIXER')
        if mixer and not channel_change:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.app.stop('quit\n')
        rc.app(self.prev_app)

    def eventhandler(self, event, menuw=None):
        _debug_('%s: %s app got %s event' % (time.time(), self.mode, event))
        if event == em.STOP or event == em.PLAY_END:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return True
        
        elif event == em.TV_CHANNEL_UP or event == em.TV_CHANNEL_DOWN:
            if self.mode == 'vcr':
                return
             
            if event == em.TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
            elif event == em.TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
            nextvg = self.fc.getVideoGroup(nextchan)
            _debug_("nextchan is %s" % nextchan)

            # XXX hazardous to your health. don't use tvtime with anything
            # other than one normal video_group.
            # we lose track of the channel index at some points and
            # chaos ensues
            #if self.current_vg != nextvg:
            #    self.Stop(channel_change=1)
            #    self.Play('tv', nextchan)
            #    return TRUE

	    self.fc.chanSet(nextchan, app=self.app)
	    #self.current_vg = self.fc.getVideoGroup(self.fc.getChannel())

            # Go to the prev/next channel in the list
            if event == em.TV_CHANNEL_UP:
                self.app.write('CHANNEL_UP\n')
            else:
                self.app.write('CHANNEL_DOWN\n')

            return True
            
        elif event == em.TOGGLE_OSD:
            self.app.write('DISPLAY_INFO\n')
            return True
        
        elif event == em.OSD_MESSAGE:
	    # XXX this doesn't work
            #self.app.write('display_message %s\n' % event.arg)
	    #this does
            os.system('tvtime-command display_message \'%s\'' % event.arg)
            return True
       
        elif event in em.INPUT_ALL_NUMBERS:
            self.app.write('CHANNEL_%s\n' % event.arg)
	    
        elif event == em.BUTTON:
            if event.arg == 'PREV_CH':
                self.app.write('CHANNEL_PREV\n')
                return True
	        

        return False
        
            

# ======================================================================
class TVTimeApp(childapp.ChildApp2):
    """
    class controlling the in and output from the tvtime process
    """

    def __init__(self, (app)):
        childapp.ChildApp2.__init__(self, app, stop_osd=1)

    def stdout_cb(self, line):
        if not len(line) > 0: return
        # XXX Needed because tvtime grabs focus unless used with freevo -fs
        events = { 'n' : em.MIXER_VOLDOWN,
                   'm' : em.MIXER_VOLUP,
                   'c' : em.TV_CHANNEL_UP,
                   'v' : em.TV_CHANNEL_DOWN,
                   'Escape' : em.STOP,
                   'd' : em.TOGGLE_OSD,
                   '_' : em.Event(em.BUTTON, arg='PREV_CHAN'),
                   '0' : em.INPUT_0,
                   '1' : em.INPUT_1,
                   '2' : em.INPUT_2,
                   '3' : em.INPUT_3,
                   '4' : em.INPUT_4,
                   '5' : em.INPUT_5,
                   '6' : em.INPUT_6,
                   '7' : em.INPUT_7,
                   '8' : em.INPUT_8,
                   '9' : em.INPUT_9,
                   'F3' : em.MIXER_MUTE,
                   's' : em.STOP }

        if DEBUG: print 'TVTIME 1 KEY EVENT: "%s"' % str(list(line))
        if line == 'F10':
            if DEBUG: print 'TVTIME screenshot!'
            self.write('screenshot\n')
        elif line == 'z':
            if DEBUG: print 'TVTIME fullscreen toggle!'
            self.write('toggle_fullscreen\n')
            osd.toggle_fullscreen()
        else:
            event = events.get(line, None)
            if event is not None:
                rc.post_event(event)
                if DEBUG: print 'posted translated tvtime event "%s"' % event
            else:
                if DEBUG: print 'tvtime cmd "%s" not found!' % line
   
