#if 0 /*
# -----------------------------------------------------------------------
# usb.py - the Freevo usb plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This plugin sends an event if an usb device is added
#        or removed
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/27 17:59:41  dischi
# use new poll interface
#
# Revision 1.1  2003/04/26 15:12:26  dischi
# usb daemon plugin to watch for bus changes
#
#
# ----------------------------------------------------------------------- */
#endif

import plugin
import util
import rc

TRUE  = 1
FALSE = 0

class PluginInterface(plugin.DaemonPlugin):
    """
    This Plugin to scan for usb devices. You should activate this
    plugin if you use mainmenu plugins for special usb devices
    like camera.py.
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.devices = util.list_usb_devices()
        self.poll_interval = 10

    def poll(self, menuw=None, arg=None):
        """
        poll to check for devices
        """

        changes = FALSE

        current_devices = util.list_usb_devices()
        for d in current_devices:
            try:
                self.devices.remove(d)
            except ValueError:
                changes = TRUE
                print 'usb.py: new device %s' %d

        for d in self.devices:
            changes = TRUE
            print 'usb.py: removed device %s' % d

        if changes:
            rc.post_event(plugin.event('USB'))
            
        self.devices = current_devices
