# test code, replacing record_client and record_server in the future

if __name__ == '__main__':
    import notifier
    notifier.init( notifier.GENERIC )
    
import mcomm

server = None

def list_recordings_return(return_list, data = None):
    print return_list
    
def notification(entity):
    global server
    if not entity.present and entity == server:
        print 'recordserver lost'
        server = None
        return

    if entity.present and entity.has_key('app') and \
           entity['app'] == 'recordserver':
        print 'recordserver found'
        server = entity
        # server.list_recordings(callback=list_recordings_return)
        # server.list_recordings(list_recordings_return)
        print server.list_recordings()  # wait
        return
    
mcomm.register_entity_notification(notification)

if __name__ == '__main__':
    notifier.loop()
