import plugin

class PluginInterface(plugin.Plugin):
    def __init__(self, arg1, arg2='foo'):
        plugin.Plugin.__init__(self)


plugin.activate('foo', args=('1',))
plugin.activate('foo', args=('1', 'bar'))

