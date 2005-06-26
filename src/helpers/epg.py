#!/usr/bin/python

import getopt
import os
import sys
import time
import logging
import kaa.epg

import sysconfig
import config

def usage(return_value):
    print '\nUsage: kaa-epg [config] [options]'
    print '\nOptions:'
    print '  -h, --help              Print help and exit.'
    print '  -l, --list              List your channels.'
    print '  -f file, --fill=file    Fill db with xmltv from file.'
    print '  -s prog, --search=prog  Search db for matching program.'
    sys.exit(return_value)


def list_channels():
    """
    List all channels in the database.
    """
    for c in kaa.epg.channels:
        print c


def search_progs(subs):
    """
    Search for programs in database.
    """
    programs = kaa.epg.search(subs)
    for p in programs:
        start = time.strftime('%b %d %H:%M', time.localtime(p.start))
        stop = time.strftime('%H:%M', time.localtime(p.stop))
        channel = p.channel.name.encode('latin-1', 'ignore')
        title   = p.title.encode('latin-1', 'ignore')
        if len(title) > 30:
            title = title[:27] + '...'
        print '%s-%s %-30s on %s (%d)' % (start, stop, title, channel, p.id)


def main():
    options = 'f:hls:'
    long_options = ['fill=', 'help', 'list', 'search=']
    action = None
    action_args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError, e:
        print 'Error:', e
        usage(1)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage(0)

        # options
        if o in ('-f', '--fill'):
            action = kaa.epg.update
            action_args = ['xmltv', a]
        if o in ('-l', '--list'):
            action = list_channels
            action_args = []
        if o in ('-s', '--search'):
            action = search_progs
            action_args = [ a ]

    if not action:
        usage(1)

    kaa.epg.connect('sqlite', sysconfig.datafile('epgdb'))
    # TV_CHANNELS, TV_CHANNELS_EXCLUDE
    kaa.epg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE)

    action(*action_args)



if __name__ == "__main__":
    main()
