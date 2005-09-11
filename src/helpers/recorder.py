import logging

import config
import kaa
import kaa.record

# mbus support
from mcomm import RPCServer, RPCError, RPCReturn

# get logging object
log = logging.getLogger()

class Recorder(RPCServer):
    def __init__(self):
        RPCServer.__init__(self, 'record-daemon')
        config.detect('tvcards')
        self.cards = []
        self.recordings = {}
        self.server = None
        
        for id, card in config.TV_CARDS.items():
            if id.startswith('dvb'):
                dev = kaa.record.DvbDevice(card.adapter, card.channels_conf)
                dev.name = id
                dev.rating = card.priority
                self.cards.append(dev)
        
    def __rpc_devices_list__(self, addr, val):
        self.server = addr
        return RPCReturn([ x.name for x in self.cards ])


    def __rpc_device_describe__(self, addr, val):
        id = self.parse_parameter(val, ( str, ))
        for card in self.cards:
            if not card.name == id:
                continue
            return RPCReturn((card.name, card.rating, card.get_bouquet_list()))
        return RPCError('%s invalid' % id)


    def __rpc_vdr_record__(self, addr, val):
        device, channel, start, stop, filename, options = \
                self.parse_parameter(val, ( str, str, int, int, str, list ))
        for card in self.cards:
            if card.name == device:
                device = card
                break
        else:
            return RPCError('%s invalid' % id)

        chain = kaa.record.Chain()
        if isinstance(device, kaa.record.DvbDevice):
            chain.append(kaa.record.Remux())
        if filename.startswith('file:/'):
            filename = filename[5:]
        if filename.startswith('udp://') > 0:
            chain.append(kaa.record.UDPSend(filename[6:]))
        else:
            chain.append(kaa.record.Filewriter(filename))
            
        rec = kaa.record.Recording(start, stop, device, channel, chain)
        rec.signals['start'].connect(self.send_event, 'vdr.started', rec.id)
        rec.signals['stop'].connect(self.send_event, 'vdr.stopped', rec.id)
        self.recordings[rec.id] = rec
        return RPCReturn(rec.id)

        
    def __rpc_vdr_remove__(self, addr, val):
        id = self.parse_parameter(val, ( int, ))
        log.info('stop recording %s' % id)
        if id in self.recordings:
            self.recordings[id].remove()
            del self.recordings[id]
            return RPCReturn()
        return RPCError('%s invalid' % id)


    def send_event(self, event, id):
        if not self.server:
            return
        self.mbus_instance.send_event(self.server, event, (id,))
        
r = Recorder()
kaa.main()
