import sys
import mcomm
import config

server = None

def add_favorite(prog):
    if not server:
        return False, 'Recordserver unavailable'
    try:
        if prog.channel == 'ANY':
            channel = []
            for c in config.TV_CHANNELS:
                channel.append(c[0])
        else:
            channel = [ prog.channel ]
        days = (_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'),
                _('Sat'), _('Sun'))
        if prog.dow in days:
            days = [ Unicode(days.index(prog.dow)) ]
        else:
            days = [ 0, 1, 2, 3, 4, 5, 6 ]
        
        mod = []
        if prog.mod == 'ANY' or 1: # FIXME: add real mod
            mod.append('00:00-23:59')
        return server.favorite_add(prog.title, channel, 50, days, mod, False)
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'
    except Exception, e:
        print 'recordings.add_favorite:', e
        return False, 'Internal client error'

    
def schedule_recording(prog):
    if not server:
        return False, 'Recordserver unavailable'
    info = {}
    print prog['description']
    # if prog['description']:
    #     info['description'] = prog['description']
    # if prog['subtitle']:
    #     info['subtitle'] = prog['subtitle']
    try:
        return server.recording_add(prog['title'], prog['channel'], 1000,
                                    prog['start'], prog['stop'], info)
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'
    except Exception, e:
        print 'recordings.schedule_recording:', e
        return False, 'Internal client error'


def notification(entity):
    global server
    if not entity.present and entity == server:
        print 'recordserver lost'
        server = None
        return

    if entity.present and entity.matches(mcomm.get_address('recordserver')):
        print 'recordserver found'
        server = entity
        try:
            print server.recording_list()  # wait
        except mcomm.MException, e:
            print 'recordings.notification:', e

mcomm.register_entity_notification(notification)
