#!/usr/bin/env python
import sys,os,time
import string,re
import cPickle as pickle

# Horrible, horrible hack to work on command-line
# Need to figure out how to make config be quiet.
STARTDIR='/usr/local/freevo'
os.environ['FREEVO_STARTDIR'] = STARTDIR
sys.path.append(STARTDIR)
sys.path.append(STARTDIR + '/src')
sys.path.append(STARTDIR + '/src/tv')

import config

sys.stdout = sys.__stdout__

# Had to copy over get_tunerid, progname2filename since including the 
# record_video code resulted in an attempt to open the graphic device. 

def get_tunerid(channel_id):
    tuner_id = None
    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_tuner_id
    return None

def progname2filename(progname):
    '''Translate a program name to something that can be used as a filename.'''

    # Letters that can be used in the filename
    ok = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

    s = ''
    for letter in progname:
        if letter in ok:
            s += letter
        else:
            if s and s[-1] != '_':
                s += '_'
    return s


# A simple version of the code in record_daemon/record_video for building
# a schedule.

def make_schedule (b=None):
    if not b:
        return

    # Time stuff
    #start_time = time.mktime(time.strptime(b.start, '%Y-%m-%d %H:%M'))
    start_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(b.start))



    len_secs = int(b.stop-b.start)
    len_secs = len_secs - 10
    temp = len_secs
    hour = int(temp/3600)
    minu = int(temp/60)
    seco = int(temp%60)
    timecode_format = '%0.2i:%0.2i:%0.2i' % (hour,minu,seco)

    # Channel
    tunerid = get_tunerid(b.channel_id)


    rec_name = b.title
    if b.sub_title:
        rec_name += '_-_' + b.sub_title
    ts_ch = time.strftime('%m-%d_%I:%M_-', time.localtime(b.start))
    rec_name = ts_ch + '_' + progname2filename(rec_name)
    rec_name = os.path.join(config.DIR_RECORD, rec_name)



    cl_options = { 'channel'  : tunerid,
                   'filename' : rec_name,
                   'seconds'  : len_secs,
                   'timecode' : timecode_format }
   
    scheduleline = start_time + "," + str(len_secs) + "," + config.VCR_CMD % cl_options + "," + b.channel_id
    return scheduleline

    #return config.VCR_CMD % cl_options

# Using this is about a million times faster than using XMLTV natively.
#
# hardcoded to -0, some people might not process the guide as root.
#
picklefile = config.FREEVO_CACHEDIR + '/TV.xml-0.pickled'

# Ugly.

if (len(sys.argv) > 2) and ((sys.argv[1] == '-listing') or (sys.argv[1] == '-schedule')):
    pattern = sys.argv[2]
    for m in sys.argv[3:]:
        pattern += '\ ' + m
    ARG = '.*' + pattern + '*.'
    REGEXP = re.compile(ARG,re.IGNORECASE)
else:
    print "Usage: " + str(sys.argv[0]) + " [-listing | -schedule] [TV PROGRAM]"
    sys.exit(1)

# Ugly too, but this works for now. 


m = pickle.load(open(picklefile,'r'))
for a in m.GetPrograms():
    for b in a.programs:
        if REGEXP.match(b.title) and (b.start >= int(time.time())):
            if sys.argv[1] == '-schedule':
                print make_schedule(b)
            elif sys.argv[1] == '-listing':
                print b.start
                if b.sub_title:
                    print str(b) + ' - ' + b.sub_title
                else:
                    print b
