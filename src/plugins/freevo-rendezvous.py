import socket
import Rendezvous
import time
import plugin
from freevo.version import __version__
import config

class PluginInterface(plugin.DaemonPlugin):
    """
    Rendezvous Broadcaster Plugin
    See: http://www.porchdogsoft.com/products/howl/ (Win32 Plugin/Linux/FreeBSD)

    This plugin has been tested with 
       * Safari on Mac OS X Panther
       * IE6 + Howl on Windows XP

    To enable this plugin, add 
        plugin.activate('freevo-rendezvous')
    to your local_conf.py
    """

    r = RendezVous.Rendezvous()

    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        desc = {'version':__version__}
        myip = self.my_ipaddr('localhost')
        info = Rendezvous.ServiceInfo("_http._tcp.local.", "Freevo Web._http._tcp.local.", address=socket.inet_aton(myip), 
            port=config.WWW_PORT, weight=0, priority=0, properties=desc, server=socket.gethostname)
        r.registerService(info)

    def my_ipaddr(self,interface_hostname=None):
        # give the hostname of the interface you want the ipaddr of
        hostname = interface_hostname or socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((hostname, 0))
        ipaddr, port = s.getsockname()
        s.close()
        return ipaddr  # returns 'nnn.nnn.nnn.nnn' (StringType)

    def shutdown(self):
        r.unregisterService(info)
        r.close()





