#!/usr/bin/env python

#
# mp3info.py written by Karol Bryd <kbryd@python.org.pl>
# Xing and Python 2.x fixes by Aubin Paul <aubin@debian.org>
# 
# This programs is licensed under the GNU Public License
#
# You're welcome to redistribute this software under the               
# terms of the GNU General Public Licence version 2.0          
# or, at your option, any higher version.              
#                                              
# the idea is mostly based on sourcecode of Gnapster
# some code is ripped from other places
#

__version__ = "0.0.1"
__doc__ = """

mp3info is a simple class for extracting useful informations from MP3
files, it can get length of the file, calculate average bitrate in
case of VBR files (including Xing) and many other informations including
getting ID3 tags.

usage is quite simple:

  create class instance, give filename as an argument to the
  contructor
  mp3 = mp3header(sys.argv[1])
 
  the info() method gives us length of an MP3 and average bitrate
 
  (m, s, b) = mp3.info()
"""

import string
import os
from stat import *

_freq_arr = [[[11025, 12000, 8000], [0,0,0]], [[22050, 24000, 16000], [44100, 48000, 32000]]]
       
_bitrates= [[[0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
             [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
             [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]],
            [[0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448],
             [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384],
             [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]]
            ];

class mp3header:
    def __init__(self, filename):

        try:
            self.fp = open(filename, "r")
        except IOError, e:
            raise "The file: [%s] does not exist."%filename
        try:
            self.filesize = os.stat(filename)[ST_SIZE]
        except:
            raise "Unable to guage filesize of file [%s]"%filename
        self.frametime = 0.0
        self.framesize = 0
       
    def read_byte(self, prev):
        nextbyte = self.fp.read(1)
        if nextbyte == '':
            return ''
        return (prev << 8) | ord(nextbyte)

    # finds frame marker in MP3 file, does not check if it is
    # a correct one, returns header offset
    def find_marker(self):
        while 1:
            data = (ord(self.fp.read(1)) << 8) | ord(self.fp.read(1))
            self.fp.seek(-1, 1)
            if data & 0xffe0 == 0xffe0:
                self.fp.seek(-1, 1)
                return self.fp.tell()
        return 0
   
    # finds *correct* frame marker in file, returns header offset
    def find_header(self):
        while 1:
            pos = self.find_marker()
            header = self.get_quad()
            if self.decode_header(header):
                self.fp.seek(-4, 1)
                oldpos = self.fp.tell()
                self.fp.seek(self.framesize+self.pad, 1)
                header = self.get_quad()
                if header & 0xffe00000 == 0xffe00000:
                    self.fp.seek(oldpos)
                    return oldpos
            else:
                self.fp.seek(4, 1)
        return 0

    def get_l4 (self, s):
        return reduce (lambda a,b: ((a<<8) + b), map (long, map (ord, s)))

    # finds Xing header and decodes it
    # returns 1 if succesful, 0 otherwise
    def find_xing(self):
        buf = self.fp.read(4096)
        pos = string.find(buf, 'Xing')
        if pos != -1:
            pos = pos + 4
            self.flags = self.get_l4(buf[pos:pos+4]); pos = pos + 4
            self.frames = self.get_l4(buf[pos:pos+4]); pos = pos + 4
            self.bytes = self.get_l4(buf[pos:pos+4]); pos = pos + 4

            self.toc = []
            if self.flags & 0x4:
                for i in range(100):
                    self.toc.append(long((ord(buf[pos:pos+1])/256.0)*self.bytes))
                    pos = pos + 1

            self.fp.seek(0)
            return 1
        return 0

    # gets number of bits from data,'bits' describe how many
    def get_bits(self, data, bits):
        b = data >> (32-bits)
        b = b & 0x000000f
        if b == 0xf:
            b = 1
        return data << bits, b

    # reads 4 bytes from file and returns longword
    def get_quad(self):
        header = 0
        header = self.read_byte(header)
        if header == '':
            return ''
        header = self.read_byte(header)
        if header == '':
            return ''
        header = self.read_byte(header)
        if header == '':
            return ''
        header = self.read_byte(header)
        return header
   
    # decodes header
    def decode_header(self,header):
        (header, bits) = self.get_bits(header, 11)
        self.bits = bits
        (header, index) = self.get_bits(header, 1)
        self.index = index
        (header, id) = self.get_bits(header, 1)
        self.id = id
        (header, layer) = self.get_bits(header, 2)
        self.layer = layer
        (header, prot) = self.get_bits(header, 1)
        self.prot = prot
        (header, bitrate) = self.get_bits(header, 4)
        self.bitrate = bitrate
        (header, freq) = self.get_bits(header, 2)
        self.freq = freq
        (header, pad) = self.get_bits(header, 1)
        self.pad = pad
        (header, priv) = self.get_bits(header, 1)
        self.priv = priv
        (header, mode) = self.get_bits(header, 2)
        self.mode = mode
        (header, mode_ext) = self.get_bits(header, 2)
        self.mode_ext = mode_ext
        (header, copyright) = self.get_bits(header, 1)
        self.copyright = copyright
        (header, original) = self.get_bits(header, 1)
        self.original = original
        (header, emphasis) = self.get_bits(header, 2)
        self.emphasis = emphasis
       
        try:
            self.bitrate = _bitrates[id][3-layer][bitrate]
        except IndexError:
            return 0
           
        try:
            self.frequency = _freq_arr[index][id][freq]
        except IndexError:
            return 0
          
        if self.frequency != 0:
            self.last_freq = self.frequency
        else:
            self.frequency = self.last_freq
           
        if id:
            bid = 144000
            tid = 1152
        else:
            bid = 72000
            tid = 576
           
        self.framesize = ((bid * self.bitrate) / self.frequency)
        if self.framesize == 0:
            return 0
        self.total = (self.filesize / (self.framesize + 1)) - 1
        self.time = (self.total * tid / self.frequency)
        self.frametime = float(float(tid) / float(self.frequency))
       
        return 1

    # processes VBR files using Xing's Table of Contents (TOC)
    # to speed up the process
    def process_xing(self):
        bav = 0
        bcn = 0
        time = 0
        for pos in self.toc:
            self.fp.seek(pos)
            hdr = self.find_header()
            header = self.get_quad()
            if header == '':
                continue

            self.decode_header(header)
            time = time + self.frametime
            bav = bav + self.bitrate
            bcn = bcn + 1

        avtime = int(self.frames * (time/bcn))
        return (avtime/60, avtime%60, int(bav/bcn))
   
    def info(self):
        if self.find_xing():
            return self.process_xing()
        else:
            # get info from the first frame header

            self.fp.seek(0)
            hdr = self.find_header()
            if hdr < 0:
                hdr = 0

            self.fp.seek(hdr)
            header = self.get_quad()
            self.decode_header(header)
            return (self.time/60, self.time%60, self.bitrate)

if __name__ == '__main__':
    import sys
    try:
        mp3 = mp3header(sys.argv[1])
    except IndexError:
        print "Must provide the name of the mp3 file."
    else:
        (m, s, b) = mp3.info()
        print "%d %02d:%02d" % (b, m, s)
