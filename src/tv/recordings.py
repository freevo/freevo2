import sys
import mcomm

server = None

def schedule_recording(prog):
    if not server:
        return False, 'Recordserver unavailable'
    info = {}
    # if prog['description']:
    #     info['description'] = prog['description']
    try:
        return server.recording_add(prog['title'], prog['channel'],
                                    0, prog['start'], prog['stop'], info)
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'


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

