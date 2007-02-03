import os
import freevo.ui

def plugin_finder(plugins, dirname, names):
    names = [ os.path.join(dirname, f) for f in names ]
    if dirname == os.path.dirname(freevo.ui.__file__):
        names = [ f for f in names if os.path.isdir(f) ]
    elif 'plugins' in dirname[len(os.path.dirname(freevo.ui.__file__)):]:
        names = [ f for f in names if f.endswith('.py') and \
                  not f.endswith('__init__.py') ]
    else:
        return
    for filename in names:
        if os.path.isfile(filename):
            f = open(filename)
        else:
            for interface in ('interface.py', '__init__.py'):
                if os.path.isfile(filename + '/' + interface):
                    f = open(filename + '/' + interface)
                    break
            else:
                break
        pname = os.path.splitext(filename)[0]
        pname = pname[len(os.path.dirname(freevo.ui.__file__)):].replace('/', '.')
        iname = pname[1:]
        pname = pname.replace('.plugins.', '.')[1:]
        for line in f.readlines():
            if line.startswith('__plugins__'):
                exec(line)
                for p in __plugins__:
                    plugins.append((iname, p, pname + '.' + p))
                break
            if 'PluginInterface' in line:
                plugins.append((iname, 'PluginInterface', pname))
                break
        f.close()
        
plugins = []
os.path.walk(os.path.dirname(freevo.ui.__file__), plugin_finder, plugins)
print plugins
