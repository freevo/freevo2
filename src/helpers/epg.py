import getopt
import os
import sys
import time

import config
import sysconfig
import pyepg

pyepg.connect('sqlite', sysconfig.datafile('epgdb'))
pyepg.load(config.TV_CHANNELS, config.TV_CHANNELS_EXCLUDE)


# db.db.db looks a bit rediculous!
print 'Using database: %s' % pyepg.guide.db.db.db.filename


def usage():
    print '\nUsage: freevo epg [options]'
    print '\nOptions:'
    print '  [-h|--help]                       Print help and exit.'
    print '  [-i|--info]                       Print some information.'
    print '  [-l|--list]                       List your channels.'
    print '  [-f|--fill]                       Fill DB with XMLTV data.'
    print '  [-p chan|--list-programs chan]    List programs in a given chan.'
    print '  [-s|--search]                     Search DB for matching program.'
    print '  [-t|--test]                       Developer test function.'
    print '\nDescription:'
    print '      This helper can be used to perform operations on the EPG'
    print '      database.\n'
    sys.exit(0)


def list_channels():
    print 'EPGDB Channels:'
    print '---------------'
    for c in pyepg.channels:
        print '%s: %s' % (c.id, c.title)


def list_programs(channel):
    print 'list_programs() disabled'
    sys.exit(0)
    for c in pyepg.channels:
        print c


def fill_xmltv(xmltv_file):
    if not os.path.isfile(xmltv_file):
        xmltv_file = config.XMLTV_FILE

    print 'FILE: "%s"' % xmltv_file

    pyepg.update('xmltv', xmltv_file)


def info():
    print 'info() disabled'
    sys.exit(0)
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
    print 'list_tables() disabled'
    sys.exit(0)
    rows = epg.execute('select tbl_name from sqlite_master where \
                        type="table" order by tbl_name')
    print 'EPGDB Tables:'
    print '-------------'
    for r in rows:
        print '    %s' % r[0]
   

def search_progs(subs):
    print 'Results:'
    print '--------'
    programs = pyepg.search(subs)
    for p in programs:
        print '%s:%d: %s - %s' % (String(p.channel.id), p.id, 
               String(p.title), 
               time.strftime('%b %d ' + config.TV_TIMEFORMAT, 
                             time.localtime(p.start)))


def test_func():
    pyepg.guide.expire_programs()
    sys.exit(0)


def main():
    update_chan = False
    show_info = False
    show_tables = False
    show_progs = False
    add_xmltv = False
    xmltv_file = ''
    search_subs = ''
    channel = ''

    options = 'cfhilp:s:t'
    long_options = ['update-channels', 'fill', 'help', 'info', 'list', 
                    'list-programs', 'search', 'test']

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
        if o in ('-t', '--test'):
            test_func()

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
