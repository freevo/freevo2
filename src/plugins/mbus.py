import mcomm
import plugin
import eventhandler
import event

class PluginInterface(plugin.Plugin, mcomm.RPCServer):
    def __init__(self):
        plugin.Plugin.__init__(self)
        mcomm.RPCServer.__init__(self)
        
    def __rpc_play__(self, addr, val):
        file = self.parse_parameter(val, ( str, ))

        if not eventhandler.is_menu():
            return mcomm.RPCError('freevo not in menu mode')

        menuw  = eventhandler.get()
        parent = menuw.menustack[-1].selected
        
        for p in plugin.mimetype(None):
            i = p.get(parent, [ file ] )
            if i and hasattr(i[0], 'play'):
                i[0].play(menuw=menuw)
                return mcomm.RPCReturn()

        return mcomm.RPCError('no player found')


    def __rpc_stop__(self, addr, val):
        eventhandler.post(event.STOP)
        return mcomm.RPCReturn()
