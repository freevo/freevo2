# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# irsend_echostar.py - Send IR commands to an echostar receiver used by
#                       Dish and ExpressVu sattelite service.  Tested 
#                       using a homebrew infrared transmitter.
# -----------------------------------------------------------------------
# $Id$
#
# Notes: The echostar boxes and lirc don't play naturally together so
#        we do things outside of (most) of the lirc space and talk to
#        the device.
#        This module borrows logic and code from jvc_send.c  Which
#        is Copyright 2002 Karl Bongers, karl@turbobit.com and Copyright 
#        2002 Pyroman, webvcrplus.
#
#        This modules is very young and will be changing to have functions
#        to perform specific tasks and used remotes and codes from your
#        lircd.conf.
#
# Notes from jvc_send.c:
#        Send codes for weird Dish networks box that uses JVC_4700 at 
#        57600 modulation/carrier frequency.
#        Requires multiple back to back signals with accurate
#        timing between signals.
# 
#        Send JVC_4700 signals, try to send out exactly
#        as they come in.  lircd/lirc_serial handling gives inaccurate
#        signal lengths between 16 bit blocks.  The signal we see
#        coming in is back-to-back packets, that is what we
#        try to duplicate.
#
#        lirc_serial.o must be loaded and setup correctly, see LIRC project.
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.1  2003/10/11 15:07:49  rshortt
# Changed this into a plugin.  It is working well but I will be gixing it up
# some more.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file doc/CREDITS for a complete list of authors.
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


import os, sys, fcntl, struct, time, string, StringIO
import array
import util.ioctl, util.lirc
import plugin


LIRC_SET_SEND_CARRIER    = util.ioctl.IOW('i', 0x00000013, 'I')
LIRC_SET_SEND_DUTY_CYCLE = util.ioctl.IOW('i', 0x00000015, 'I')


class PluginInterface(plugin.Plugin):

    MODULATION_FREQ = 57600

    ## 0 to 100, where 100=strongest? 
    DUTY_CYCLE = 50

    ## 1 block takes up 16bits*2+2, or 34 samples.  lirc_serial
    ## has a 256 sample buffer, so we can send max 7 back to back
    ## signals.
    NUM_BACK_TO_BACK = 3

    POWER_BITS = 0xf7ff; ## power button bits 
    PULSE_LEN = 350
    HEADER_SPACE = 6000
    ONE_LEN = 2700
    ZERO_LEN = 1700

    duty_cycle = None
    freq = None
    num_times_to_send = 1

    def __init__(self, conf='/etc/lircd.conf', device='/dev/lirc', remote=None):
        plugin.Plugin.__init__(self)

        self.conf = conf
        self.device = device
        self.remotes = util.lirc.parse_lircd(self.conf)
        util.lirc.dump_remotes(self.remotes)
        self.fd = None

        if not remote and len(self.remotes.values()) > 0:
            remote = self.remotes.values()[0]
        else:
            remote = self.remotes[remote]
        self.remote = remote

        plugin.register(self, 'EXTERNAL_TUNER')


    def setChannel(self, chan):
        chan = str(chan)
        digits = len(chan)

        self.prepareSend()

        for i in range(digits):
            code = long(self.remote.codes.get(chan[i]), 16)
            if not code:
                print 'No code for %s' % chan[i]

            self.transmitSignal(code)

        self.clean()


    def transmitButton(self, button):
        code = long(self.remote.codes.get(button), 16)
        if not code:
            print 'No code for %s' % button

        print 'sending button: %s\n' % button
        print 'sending code: %x\n' % code
        self.prepareSend()
        self.transmitSignal(code)
        self.clean()
    
    
    def prepareSend(self):
        self.fd = os.open(self.device, os.O_RDWR)
        if self.fd < 0:
            sys.exit("Error: %d\n" % fd)
        else:
            print "Lirc Opened at %s" % self.device
    
    
        print 'LIRC_SET_SEND_CARRIER: %s' % LIRC_SET_SEND_CARRIER
        r = fcntl.ioctl(self.fd, long(LIRC_SET_SEND_CARRIER), 
                            struct.pack( "L", self.MODULATION_FREQ))
        print 'LIRC_SET_SEND_CARRIER got %s' % r
        #    printf("couldn't set modulation\n");
    
    
        r = fcntl.ioctl(self.fd, long(LIRC_SET_SEND_DUTY_CYCLE), 
                            struct.pack( "L", self.DUTY_CYCLE))
        print 'LIRC_SET_SEND_DUTY_CYCLE got %s' % r
        #    printf("couldn't set duty cycle");
    

    def clean(self):
        os.close(self.fd)
    

    def transmitSignal(self, code):
        data = []

        ## fill up our buffer with signal data to send driver 
        for k in range(self.NUM_BACK_TO_BACK):
            data.append(self.PULSE_LEN)
            data.append(self.HEADER_SPACE)
    
            v = code
            for i in range(16):
                data.append(self.PULSE_LEN)
                if (v & 0x8000):
                   data.append(self.ONE_LEN)
                else:
                   data.append(self.ZERO_LEN)
                v <<= 1
        
        for i in range(self.num_times_to_send):
            print 'sending code: %x\n' % code
            a1 = array.array('I', data)
            al = a1.itemsize
            print 'al: %s' % al
            m = 0
            tmp = ''
            sio = StringIO.StringIO()
            for stuff in data:
                # print 'data%d: %d' % (m, stuff)
                tmp = struct.pack('I', stuff)
                # print 'tmp: %s' % tmp
                sio.write(tmp)
                sio.flush()
                m += 1
            readnum = (len(data)-1)*al
            print 'readnum: %s' % readnum
            sio.seek(0)
            print 't2: %s' % sio.tell()
            t2 = sio.read(readnum)
            sio.flush()
            print 't2: %s' % sio.tell()
            # print 't2: %s' % t2
            print 'fd: %s' % self.fd
            os.write(self.fd, t2)
            #os.write(fd, sio.read(readnum))
            #print 'total: %s' % total
            # tmp = stuff.tostring()
            # tmp = struct.pack('%sI' % len(data), (data,))
            #tmp = struct.pack('I', stuff)
            #print 'tmp: %s' % tmp
            #blah.write(tmp)
            #os.write(fd, tmp)
            sio.close()
            # os.close(self.fd)
            time.sleep(1)
    

# ir = IRTrans('/etc/lircd-transmit.conf')
# ir.transmit_button('1')
# ir.setChannel('701')
