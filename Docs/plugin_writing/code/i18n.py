class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.translation('my_app')

    def foo(self):
        return self._('Text to translate')
    
