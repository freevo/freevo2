# This is the config file used by record_server.py.

import plugin

# We need to remove all of the plugins activated by the main config.
plugin.all_plugins = []
plugin.ptl = {}

DEBUG = 0

# XXX Note:  This VCR_CMD is not used yet, please modify the one in 
# local_conf.py.  Beware that the recording plugin expects a different format,
# 3 options instead of 4: %(channel)s, %(seconds)s, and %(filename)s.
#
# VCR_CMD = ('/var/media/bin/tvrecord %(channel)s %(seconds)s "%(filename)s"')    

RECORD_SERVER_IP = 'localhost'
RECORD_SERVER_PORT = 18001
RECORD_SCHEDULE = '/var/cache/freevo/record_schedule.xml'

plugin.activate('plugins.generic_record')

LOGDIR = '/var/log/freevo'
