#!/usr/bin/env python

import sys
import os
import time

import notifier
import config
import mcomm

server = None

import pyepg
epg = pyepg.get_epg(os.path.join(config.FREEVO_CACHEDIR, 'epgdb'))

def notification(entity):
    global server
    if not entity.present and entity == server:
        print 'recordserver lost'
        server = None
        return

    if entity.present and entity.matches(mcomm.get_address('recordserver')):
        print 'recordserver found'
        server = entity
        print 'type \'help\' to see possible commands'
        print '> ',
        sys.__stdout__.flush()

def print_result(result):
    # FIXME: doesn't work for epg results
    if isinstance(result, (list, tuple)) and len(result) > 0 and \
           isinstance(result[0], (list, tuple)):
        for r in result:
            print r
    else:
        print result

        
def user_input( socket ):
    input = socket.readline().strip()
    if input == 'help':
        print '\rpossible commands:'
        print
        print 'rssh commands:'
        print '  help                       print this help'
        print '  exit                       exit rssh'
        print '  time(YYYY.MM.DD.HH:MM)     convert into seconds'
        print
        print 'epg commands:'
        print '  epg.search_programs(name)'
        print '  epg.get_programs(channels, start, stop)'
        print
        print 'record commands:'
        print '  recording.list()'
        print '  recording.describe(id)'
        print '  recording.add(name, channel, priority, start, stop, optionals)'
        print '  recording.add(dbid, priority, optionals)'
        print '  recording.remove(id)'
        print
        print 'favorite commands:'
        print '  favorite.update()'
        print '  favorite.list()'
        print '  favorite.add(name, channels, priority, days, times, once)'
        print
        print 'See src/record/server.py for an updated list of commands.'
        print 'A better documentation of possible mbus commands will follow'
        print 'Notice: the code will \'eval\'ed by python so you need to put'
        print 'parameter strings in quotes when calling epg, recording or'
        print 'favorite calls.'
        
    elif input == 'exit':
        print
        sys.exit(0)
    elif input.startswith('time'):
        try:
            s = input[5:-1]
            t = int(time.mktime(time.strptime(s, '%Y.%m.%d.%H:%M')))
            print '\r%s is %s secs' % (s, t)
            print 
        except Exception, e:
            print e
    elif input.startswith('recording.'):
        print '\rcalling rpc'
        try:
            status, result = eval('server.recording_%s' % input[10:])
            if not status:
                print 'failed'
            else:
                print_result(result)
        except Exception, e:
            print e
    elif input.startswith('favorite.'):
        print '\rcalling rpc'
        try:
            status, result = eval('server.favorite_%s' % input[9:])
            if not status:
                print 'failed'
            else:
                print_result(result)
        except Exception, e:
            print e
    elif input.startswith('epg.'):
        print '\rcalling epg command'
        try:
            result = eval(input)
            print_result(result)
        except Exception, e:
            print e
    else:
        print '\runknown command \'%s\'' % input
    print
    print '> ',
    sys.__stdout__.flush()
    
    return True

mcomm.register_entity_notification(notification)
notifier.addSocket( sys.stdin, user_input )

print 'rssh - recordserver shell'
print '-------------------------'
print
print 'waiting for recordserver'
notifier.loop()
