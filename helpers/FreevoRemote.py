#! /usr/bin/env python

#if 0 /*
# -----------------------------------------------------------------------
# FreevoRemote.py - a small tkinter example remote program
# -----------------------------------------------------------------------
# $Id$
#
# Notes: very basic layout. need ENABLE_NETWORK_REMOTE = 1 in you local_conf.py
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/06/24 22:59:38  outlyer
# I think this is the last bit of cleanup.
#
# o Moved FreevoRemote "Network" client into helpers
# o Removed old remote code. I think pylirc is working for everyone.
#
# Revision 1.1  2003/05/06 00:05:12  rshortt
# Network remote control app posted by Mike Ruelle.
#
#
# Revision 1.1  2003/05/05 14:30:10  mikeruelle
# A small example program to use the remote control via UDP socket available in
# Freevo. Useful if you remote lacks many buttons.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
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

from Tkinter import *
import sys
import socket

panels = [ ['1','2','3'], ['4','5','6'], ['7','8','9'], ['ENTER','0','EXIT'],
           ['MENU','UP','GUIDE'], ['LEFT','SELECT','RIGHT'], ['DISPLAY','DOWN','SUBTITLE'],
           ['CH+','VOL+','PIP_ONOFF'], ['CH-','VOL-','PIP_SWAP'], ['PREV_CH','MUTE','PIP_MOVE'],
           ['PLAY','PAUSE','REC'], ['REW','STOP','FFWD'], ['EJECT','SLEEP','TV_VCR'] ]

# the big remote. can possibly be embedded in other stuff.
class FreevoRemote(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self,parent)
        self.pack(expand=YES, fill=BOTH)
        self.host = 'localhost'
        self.port = 16310
        # add the power button
        Button(self, text='POWER', command=self.PowerClick).pack(expand=YES, fill=BOTH)
        #create the frame for panel
        bframe = Frame(self)
        rcnt = 0
        for r in panels:
            ccnt = 0
            for b in r:
                #create the button for each element
                btn = Button(bframe, text=b, command=(lambda b=b: self.ButtonClick(b)))
                btn.grid(row=rcnt, column=ccnt, sticky=NSEW)
                    
                ccnt = ccnt + 1
            # add the now complete row to panel
            bframe.rowconfigure(rcnt, weight=1)
            rcnt = rcnt + 1
        bframe.columnconfigure(0, weight=1)
        bframe.columnconfigure(1, weight=1)
        bframe.columnconfigure(2, weight=1)
        #add the panel to self
        bframe.pack(side=TOP, expand=YES, fill=BOTH)

    def PowerClick(self):
        self.ButtonClick('POWER')
        self.quit()
        
    def ButtonClick(self, b):
        print b
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockobj.connect((self.host, self.port))
        sockobj.send(b)
        sockobj.close()
        
if __name__ == '__main__': 
    root = FreevoRemote()
    root.master.title('Freevo Remote')
    if len(sys.argv) > 1:
        root.host = sys.argv[1]
        if len(sys.argv) > 2:
            root.port = int(sys.argv[2])
    root.mainloop()

