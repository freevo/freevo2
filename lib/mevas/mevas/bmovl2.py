# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bmovl2.py - bmovl2 canvas
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Jason Tackaberry <tack@sault.org>
# Maintainer:    None
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
# -----------------------------------------------------------------------------

# python imports
import os
import string
import time

# mevas imports
import imagelib

# This class speaks bmovl2 over a fifo.  How MPlayer is launched is not the
# responsibility of mevas.

DEBUG = 2

class MPlayerOverlay:

    fifo_id = 0

    def __init__(self):
        self.fifo_fname = "/tmp/bmovl2-fifo-%d-%d" % (os.getpid(),
                                                      MPlayerOverlay.fifo_id)
        MPlayerOverlay.fifo_id += 1

        if os.path.exists(self.fifo_fname):
            os.unlink(self.fifo_fname)
        os.mkfifo(self.fifo_fname)

        self.fifo = os.open(self.fifo_fname, os.O_RDWR, os.O_NONBLOCK)
        self._can_write = False

        self.blitted_ids = {}
        self.deleted_queue = []
        self.buffer = []


    def can_write(self):
        return self._can_write


    def set_can_write(self, can_write):
        self._can_write = can_write


    def __del__(self):
        print "Delete", self.fifo_fname
        self.close()
        os.unlink(self.fifo_fname)


    def idle(self):
        self.flush()


    def write(self, line):
        if self.can_write():
            self.write_buffer(line)
            self.flush()


    def write_buffer(self, line):
        if self.can_write():
            self.buffer.append(line)


    def optimize_buffer(self, buffer):
        """
        Recursively remove adjacent ATOM/ENDATOM.   This doesn't really
        optimize things in terms of performance, but it cleans up the buffer
        a bit by removing extraneous ATOM/ENDATOM pairs and makes debugging
        easier.
        """

        # This code is lame and could probably be done in like one line if I
        # had a better handle on Python's functional constructs. :)

        if buffer == []:
            return buffer

        recurse = False
        new_buffer = []
        pos = 0
        while pos < len(buffer):
            if buffer[pos][:4] == "ATOM":
                # Handle adjacent ATOM/ENDATOM
                if pos + 1 < len(buffer) and buffer[pos + 1][:7] == "ENDATOM":
                    recurse = True
                    pos += 2
                    continue
                # Remove ATOM/ENDATOM from ATOM \ SINGLE COMMAND \ ENDATOM
                if pos + 2 < len(buffer) and buffer[pos + 2][:7] == "ENDATOM":
                    recurse = True
                    new_buffer.append(buffer[pos + 1])
                    pos += 3
                    continue

            new_buffer.append(buffer[pos])
            pos += 1
        if recurse:
            new_buffer = self.optimize_buffer(new_buffer)
        return new_buffer


    def flush(self):
        """
        Flushes the write buffer to the bmovl2 fifo.
        """
        if len(self.buffer) == 0:
            return

        self.buffer = self.optimize_buffer(self.buffer)
        if self.buffer != [] and self.can_write():
            buffer = string.join(self.buffer, "")
            os.write(self.fifo, buffer)

            if DEBUG == 2:
                if len(buffer) > 3000:
                    print "Writing buffer to overlay", len(buffer)
                else:
                    print "Writing buffer to overlay:", buffer
            self.buffer = []


    def atom(self):
        self.write_buffer("ATOM\n")


    def endatom(self):
        self.write_buffer("ENDATOM\n")


    def move(self, id, x, y):
        self.write_buffer("MOVE %s %d %d\n" % (id, x, y))


    def alpha(self, id, alpha):
        self.write_buffer("ALPHA %s %d\n" % (id, alpha))


    def zindex(self, id, index):
        self.write_buffer("ZINDEX %s %d\n" % (id, index))


    def visible(self, id, visibility):
        self.write_buffer("VISIBLE %s %d\n" % (id, visibility))


    def rawimg(self, id, image, reset = 1):
        if image.width <= 0 or image.height <= 0:
            # Little point, isn't there.
            return

        caps = imagelib.get_capabilities()
        if "YV12A" in caps["to-raw-formats"]:
            format = "YV12A"
        else:
            format = caps["preferred-format"]

        shmem_name = None
        if caps["shmem"]:
            shmem_name = image.move_to_shmem(format)
        if not shmem_name:
            shmem_name = "0"

        self.write_buffer("RAWIMG %s %s %d %d %d %s 0\n" % \
                          (id, format, image.width, image.height, reset,
                           shmem_name))
        # If shmem failed, or we don't support shmem, we need to send the
        # image via the fifo
        if shmem_name == "0":
            bytes = image.get_raw_data(format)
            self.write_buffer(str(bytes))

        self.blitted_ids[id] = time.time()


    def rawimg_from_file(self, id, path, reset = 1):
        image = imagelib.open(path)
        self.rawimg(id, image, reset)
        return image


    def delete_all(self):
        """
        Deletes all images from bmovl2.  This should be wrapped in atom() /
        endatom() by the caller.
        """
        for id in self.blitted_ids.keys():
            self.delete(id)
        self.flush()


    def delete(self, id):
        if id in self.blitted_ids:
            self.write_buffer("DELETE %s\n" % id)
            del self.blitted_ids[id]


    def close(self):
        os.close(self.fifo)
        self.set_can_write(False)
