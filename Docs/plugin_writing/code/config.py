import plugin

class PluginInterface(plugin.Plugin):
    def config(self):
        return [ ('FOO_NAME', 'the default', 'some description'),
                 ('FOO_FUNCTION', foo, 'this is a function') ]
    
