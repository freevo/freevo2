# This is the config file used by record_server.py.

import plugin
plugin.all_plugins = []
plugin.ptl = {}

DEBUG = 0

VCR_CMD = ('/var/media/bin/tvrecord %(channel)s %(seconds)s "%(filename)s"')    

RECORD_SERVER_IP = 'localhost'
RECORD_SERVER_PORT = 18001
RECORD_SCHEDULE = '/var/cache/freevo/record_schedule.xml'

plugin.activate('generic_record')

LOGDIR = '/var/log/freevo'
