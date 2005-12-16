#!/usr/bin/env python

import sys
import os
import time

# kaa imports
import kaa.notifier
import kaa.epg

# freevo ui imports
import config

server = None

print 'Broken right now, needs to be converted to new mbus wrapper'
sys.exit(1)

config.detect('channels')

def notification(entity):
    global server
    if not entity.present and entity == server:
        print 'recordserver lost'
        server = None
        return

    if entity.present and entity.matches(mbus.get_address('recordserver')):
        print 'recordserver found'
        server = entity
        print 'type \'help\' to see possible commands'
        print '> ',
        sys.__stdout__.flush()

def print_result(result):
    if isinstance(result, (list, tuple)):
        for r in result:
            print String(unicode(r))
    else:
        print result

        
def user_input():
    input = sys.stdin.readline().strip()
    if input == 'help':
        print '\rpossible commands:'
        print
        print 'rssh commands:'
        print '  help                       print this help'
        print '  exit                       exit rssh'
        print '  time(YYYY.MM.DD.HH:MM)     convert into seconds'
        print
        print 'epg commands:'
        print '  epg.search(name)'
        print '  epg[channel id][start time]'
        print '  epg[channel id][start time:end time]'
        print
        print 'record commands:'
        print '  recording.list()'
        print '  recording.describe(id)'
        print '  recording.add(name, channel, priority, start, stop, optional)'
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
        
    elif input in ('exit', 'byte', 'quit'):
        print
        sys.exit(0)
    elif input == '':
        pass
    elif input.startswith('time'):
        try:
            s = input[5:-1]
            t = int(time.mktime(time.strptime(s, '%Y.%m.%d.%H:%M')))
            print '\r%s is %s secs' % (s, t)
            print 
        except Exception, e:
            print e
    elif input.startswith('recording.') or input.startswith('favorite.'):
        try:
            cmd = input[:input.find('(')]
            arg = eval(input[input.find('('):])
            if not isinstance(arg, tuple):
                arg = (arg, )
            print arg
            print '\rcalling rpc %s' % cmd
            status, result = server.call(cmd, None, *arg)
            if not status:
                print 'failed'
            else:
                print_result(result)
        except Exception, e:
            print e
    elif input.startswith('epg'):
        print '\rcalling epg command'
        try:
            print 
            result = eval('kaa.epg.guide' + String(input[3:]))
            print_result(result)
        except Exception, e:
            print e
    else:
        print '\runknown command \'%s\'' % input
    print
    print '> ',
    sys.__stdout__.flush()
    
    return True

mbus.register_entity_notification(notification)
kaa.notifier.SocketDispatcher(user_input).register(sys.stdin)

print 'rssh - recordserver shell'
print '-------------------------'
print
print 'waiting for recordserver'
kaa.notifier.loop()
