import getopt
import os
import sys
import traceback
import time

import sqlite

import config
from tv.channels import get_epg, get_channels

epg = get_epg()
print 'Using database: %s' % epg.db.db.filename


def usage():
    print '\nUsage:  %s [options]' % sys.argv[0]
    print '\nOptions:'
    print '  [-c|--update-channels]            Use config to add new channels.'
    print '  [-h|--help]                       Print help and exit.'
    print '  [-i|--info]                       Print some information.'
    print '  [-l|--list]                       List your channels.'
    print '  [-f|--fill]                       Fill DB with XMLTV data.'
    print '  [-p chan|--list-programs chan]    List programs in a given chan.'
    print '  [-s|--search]                     Search DB for matching program.'
    print '\nDescription:'
    print '      This helper can be used to perform operations on the EPG'
    print '      database.\n'
    sys.exit(0)


def update_channels():
    for chan in config.TV_CHANNELS:
        epg.add_channel(chan[0], chan[1], chan[2])
        

def list_channels():
    res = epg.execute('select * from channels')
    print 'EPGDB Channels:'
    print '---------------'
    for row in res:
        print '%s: %s' % (row.id, row.call_sign)


def list_programs(channel):
    print epg.get_programs(channel)
    # channels = get_channels()


def fill_xmltv(xmltv_file):
    if not os.path.isfile(xmltv_file):
        xmltv_file = config.XMLTV_FILE

    print 'FILE: "%s"' % xmltv_file

    epg.add_data_xmltv(xmltv_file)


def info():
    print 'Version:'
    print epg.execute('select * from admin')
    print 'Channel Types:'
    print epg.execute('select * from channel_types')
    print 'Categories:'
    print epg.execute('select * from categories')
    print 'Advisories:'
    print epg.execute('select * from advisories')
    print 'Ratings:'
    print epg.execute('select * from ratings')
   

def list_tables():
    rows = epg.execute('select tbl_name from sqlite_master where \
                        type="table" order by tbl_name')
    print 'EPGDB Tables:'
    print '-------------'
    for r in rows:
        print '    %s' % r[0]
   

def search_progs(subs):
    print 'Results:'
    print '--------'
    programs = epg.search_programs(subs)
    for p in programs:
        print '%s: %s - %s' % (p.channel_id, p.title, 
                               time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                                             time.localtime(p.start)))


def main():
    update_chan = False
    show_info = False
    show_tables = False
    show_progs = False
    add_xmltv = False
    xmltv_file = ''
    search_subs = ''
    channel = ''

    options = 'cfhilp:s:'
    long_options = ['update-channels', 'fill', 'help', 'info', 'list', 
                    'list-programs', 'search']

    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ('-c', '--update-channels'):
            update_chan = True
        if o in ('-f', '--fill'):
            add_xmltv = True
            xmltv_file = a
        if o in ('-h', '--help'):
            usage()
        if o in ('-i', '--info'):
            show_info = True
        if o in ('-l', '--list'):
            show_tables = True
        if o in ('-p', '--list-programs'):
            show_progs = True
            channel = a
        if o in ('-s', '--search'):
            search_subs = a

    if update_chan:
        update_channels()

    elif add_xmltv:
        fill_xmltv(xmltv_file)

    elif show_info:
        info()

    elif show_tables:
        list_channels()

    elif show_progs:
        list_programs(channel)

    elif search_subs:
        search_progs(search_subs)

    else:
        usage()



if __name__ == "__main__":
    main()
