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

    if entity.present and entity.matches(mcomm.get_address('recordserver')):
        print 'recordserver found'
        server = entity
        try:
            print server.list_recordings()  # wait
        except mcomm.MException, e:
            print 'recordings.notification:', e
        return
    
mcomm.register_entity_notification(notification)

if __name__ == '__main__':
    notifier.loop()
