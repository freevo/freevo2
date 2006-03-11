# /etc/conf.d/freevo: configuration options for the freevo init script.
# Before using this, make sure your settings in /etc/freevo are correct.


# Mode to start Freevo itself. Possible values are
#
# no:     don't start Freevo
# yes:    start Freevo on startup. You should only use this when the
#         computer is for Freevo only or you use Freevo with a DXR3
# daemon: start Freevo in daemon mode. The daemon will wait for you to
#         press QUIT or POWER on your remote and will than start
#         Freevo. After Freevo shut down, the daemon will wait again.
#
# You don't need a X server running to start Freevo from init. If
# needed, Freevo will start a X server on its own. Make sure your X
# server can handle the resolution defined in /etc/freevo/freevo.conf

freevo="no"


# Mode the start the webserver. Possible values are "no" and "yes".
# If you start the webserver with Freevo itself, you should say "no" here.

webserver="no"


# Mode the start the recordserver. Possible values are "no" and "yes". 

recordserver="no"