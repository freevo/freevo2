#!/usr/bin/env python

#
# osd_sim.py
#
# This is a very simple Xterm VT100 implementation of the Freevo OSD daemon
# It is mainly used for testing when it is inconvenient to run a real OSD
# daemon on a TV.
#
# It is intended to be run in a regular 25x80 Xterm window.
#
# The magic numbers to move the cursor etc are documented in
# "man 5 termcap" and "/etc/termcap" (xterm entry).
#

import sys, os, time
import socket
import string, fcntl, select, struct

# We need to use stuff from the main directory
sys.path += [ '..', '.' ]

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Set to 1 for debut output
DEBUG = 1

# ROWS and COLS should match what we decide to use on the real OSD
ROWS = 25
COLS = 80


def clear_screen():
    sys.stdout.write('\033[?25l') # Make cursor invisible
    sys.stdout.write('\033[H\033[2J') # Clear screen
    sys.stdout.flush()


def move_cursor(row, col):
    sys.stdout.write('\033[%03d;%03dH' % (row, col))
    sys.stdout.flush()


def set_mode(mode='end'):
    str = ''
    if mode == 'end':
        str = '\033[m\017'
    elif mode == 'bold':
        str = '\033[1m'
    elif mode == 'underline':
        str = '\033[4m'
    elif mode == 'reverse':
        str = '\033[7m'
    elif mode == 'standout':
        str = '\033[7m'
    sys.stdout.write(str)
    sys.stdout.flush()


def write_string(str, row, col, mode=''):
    move_cursor(row, col)
    if mode:
        set_mode(mode)
    sys.stdout.write(str)
    if mode:
        set_mode('end')
    move_cursor(1,1)
    sys.stdout.flush()
    

#
# row, col is 1-ROWS and 1-COLS
# width is in cols. 10 means that col 1 and 10 will be '|', the rest '-' or '='
# pos is 0-100 percent
#
def display_posbar(row, col, width, pos):
    write_string('[', row, col)
    for i in range(0, width-1):
        if (float(i) / float(width-1)) * 100.0 <= float(pos):
            write_string('=', row, col+i+1)
        else:
            write_string('-', row, col+i+1)
    write_string(']', row, col+width)
    sys.stdout.flush()
    

def handle_request(data):
    #print 'Got request: "%s"' % data

    req = data.split(';')
    
    cmd = req[0]
    
    if cmd == 'clearscreen':
        clear_screen()
    elif cmd == 'drawstring':
        str = req[2]
        col = int(req[3]) / 25
        row = int(req[4]) / 25
        if req[5] != '0':
            mode = 'reverse'
        else:
            mode = ''
        write_string(str, row, col, mode)
    

def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))

    # Receive command packets, handle them
    while 1:
        #print 'Waiting for a request'
        try:
            data = sock.recv(10000)
            if data == '':
                print 'Got null data'
            else:
                try:
                    handle_request(data)
                except:
                    print sys.exc_info()[0]
        except:
            print 'Socket error!'


#
# Test the ASCII text and 'graphics' functions
# 
def test():
    clear_screen()
    write_string('Testing regular', 2, 10, '')
    write_string('Testing bold', 4, 10, 'bold')
    write_string('Testing reverse', 6, 10, 'reverse')
    write_string('Testing underline', 8, 10, 'underline')
    write_string('Testing standout', 10, 10, 'standout')
    time.sleep(5)
    
    clear_screen()
    for width in range(30, 70):
        for pos in range(0,101):
            display_posbar(10, 5, width, pos)
            write_string('Width %d, pos %d     ' % (width, pos), 1, 1)
        time.sleep(1)
        
    time.sleep(3)
    
    clear_screen()
    for cnt in range(1,1000):
        for row in range(1,26):
            write_string('Row %d (%d)' % (row, cnt), row, 1)


    time.sleep(3)
    
    row, col = 1, 1
    while 1:
        clear_screen()
        write_string('Hello from the OSD simulator', row, col)
        row += 1
        col += 1
        if row == ROWS:
            row, col = 1,1
        time.sleep(0.2)


if __name__ == "__main__":
    #test()
    server(config.OSD_PORT)
    


# md   Start bold mode
# me   End all mode like so, us, mb, md and mr
#      me=\033[m\017
# mr   Start reverse mode
#      mr=\033[7m
# so   Start standout mode
# us   Start underlining
# vi   Cursor unvisible
#      vi=\033[?25l
#
# Xterm entry from /etc/termcap
'''
xterm|xterm terminal emulator (X Window System):\
        :am:bs:km:mi:ms:xn:\
        :co#80:it#8:li#24:\
        :AL=\E[%dL:DC=\E[%dP:DL=\E[%dM:DO=\E[%dB:IC=\E[%d@:\
        :K1=\EOH:K2=\EOE:K3=\E[5~:K4=\EOF:K5=\E[6~:LE=\E[%dD:\
        :RI=\E[%dC:UP=\E[%dA:ae=^O:al=\E[L:as=^N:bl=^G:bt=\E[Z:\
        :cd=\E[J:ce=\E[K:cl=\E[H\E[2J:cm=\E[%i%d;%dH:cr=^M:\
        :cs=\E[%i%d;%dr:ct=\E[3g:dc=\E[P:dl=\E[M:do=^J:ec=\E[%dX:\
        :ei=\E[4l:ho=\E[H:ic=\E[@:im=\E[4h:\
        :is=\E[!p\E[?3;4l\E[4l\E>:k0=\E[21~:k1=\E[11~:k2=\E[12~:\
        :k3=\E[13~:k4=\E[14~:k5=\E[15~:k6=\E[17~:k7=\E[18~:\
        :k8=\E[19~:k9=\E[20~:kD=\E[3~:kI=\E[2~:kN=\E[6~:kP=\E[5~:\
        :kb=\177:kd=\EOB:ke=\E[?1l\E>:kh=\EOH:kl=\EOD:kr=\EOC:\
        :ks=\E[?1h\E=:ku=\EOA:le=^H:mb=\E[5m:md=\E[1m:me=\E[m\017:\
        :mr=\E[7m:nd=\E[C:rc=\E8:sc=\E7:se=\E[27m:sf=^J:so=\E[7m:\
        :sr=\EM:st=\EH:ta=^I:te=\E[?1047l\E[?1048l:\
        :ti=\E[?1048h\E[?1047h:ue=\E[24m:up=\E[A:us=\E[4m:\
        :vb=\E[?5h\E[?5l:ve=\E[?25h:vi=\E[?25l:vs=\E[?25h:
'''

