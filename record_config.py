# This is the config file used by record_server.py.  If you are using
# record_daemon.py from cron ignore this file.

# XXX TODO: figure out a better way to deal with this plugin stuff and move 
# these config items into freevo_config.py - getting rid of this file.
import plugin

# We need to remove all of the plugins activated by the main config.
plugin.__all_plugins__ = []
plugin.__plugin_type_list__ = {}

DEBUG = 0

if os.path.isdir('/var/cache/freevo'):
    FREEVO_CACHEDIR = '/var/cache/freevo'
else:
    if not os.path.isdir('/var/tmp/freevo/cache'):
        os.makedirs('/var/tmp/freevo/cache')
    FREEVO_CACHEDIR = '/var/tmp/freevo/cache'

RECORD_SCHEDULE = '%s/record_schedule.xml' % FREEVO_CACHEDIR
RECORD_SERVER_IP = 'localhost'
RECORD_SERVER_PORT = 18001

# Config for the generic_record plugin.  To remove comment out the next line.
plugin.activate('plugins.generic_record')

# XXX Note:  This VCR_CMD is not used yet, please modify the one in 
# local_conf.py.  Beware that the recording plugin expects a different format,
# 3 options instead of 4: %(channel)s, %(seconds)s, and %(filename)s.
#
# VCR_CMD is only used by record_server.
# VCR_CMD = ('/var/media/bin/tvrecord %(channel)s %(seconds)s "%(filename)s"')    

# Config for the ivtv_record plugin.
# Use this plugin instead if you have an ivtv based card (PVR-250/350)
# and want freevo to do everthing for you.  TV_SETTINGS must be set up
# right in your local_conf.py
# To activate, uncomment the next line.
# plugin.activate('plugins.ivtv_record')

if os.path.isdir('/var/log/freevo'):
    LOGDIR = '/var/log/freevo'
else:
    LOGDIR = '/tmp/freevo'
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)
