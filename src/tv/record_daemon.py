'''This is the recording daemon that is run every minute using crontab
to kick off recording of TV programs in the background.

Set up crontab:

* * * * *       ( cd /usr/local/freevo ; ./freevo execute src/tv/record_daemon.py )

This assumes that freevo is installed in /usr/local/freevo!


 Schedule file format:
 start,length in seconds,commandline including args
 YYYY-MM-DD HH:MM,SSS...,/usr/local/freevo_runtime3/mencoder   (cont.)
     -vop tv... -o /movies/snl.avi ...

 The first line is a timestamp of when the daemon last ran (YYYY-MM-DD HH:MM:SS)
 
'''

import sys
import os
import time


SCHEDULE = '/tmp/freevo_record.lst'
LOG_FILE = '/tmp/freevo_record.log'


def log(s=''):
    fd = open(LOG_FILE, 'a')
    fd.write(s + '\n')
    fd.close()
    

class ScheduleItem:

    def __init__(self, start_time, length_secs, cmd):
        # Convert start_time to Unix time if needed
        if type(start_time) == type(''):
            t = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            self.start_time = time.mktime(t)
        else:
            self.start_time = int(start_time)
        self.length_secs = int(length_secs)
        self.cmd = cmd


    def check_time(self):
        '''Should this item be started?
        Returns a boolean.'''

        now = time.time()
        # Don't start anything that is within 30 seconds of the end.
        if self.start_time <= now < (self.start_time + self.length_secs - 30):
            # We're inside the time window for this item
            return 1
        else:
            return 0
        

    def make_cmd(self):
        '''Build the command line for this recording.'''

        # How many seconds are left to record?
        len_secs = int(self.length_secs - (time.time() - self.start_time))

        # Make sure this recording ends before the next one might start
        len_secs -= 30

        cmd = self.cmd + (' -v -endpos %s' % len_secs)

        #cmd += ' >& /dev/null &'
        cmd += ' >& /tmp/freevo_record_%s.log &' % int(time.time())

        return cmd
        
        
    def __str__(self):
        t = time.localtime(self.start_time)
        ts = time.strftime('%Y-%m-%d %H:%M:%S', t)
        s = '%s %s %s' % (ts, self.length_secs, self.cmd)
        return s

    
def main():
    log('=' * 80)
    log('started at %s' % time.ctime())

    schedule_init()
    
    fd = open(SCHEDULE, 'r')
    schedule = fd.readlines()
    fd.close()

    if schedule[0].find('#TIMESTAMP') != 0:
        log('Schedule corrupt! Please fix! Exiting')
        sys.exit()
    else:
        schedule[0] = '#TIMESTAMP ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n'
    
    log('Got %s entries in the schedule:' % (len(schedule)-1))
    log()
    num = 1
    new_schedule = schedule[0]
    for s in schedule[1:]:

        # Old items are marked '#' in the first column
        if s[0] == '#':
            log('Got old item: "%s"' % s.strip())
            log()
            new_schedule += s
            continue

        vals = s.strip().split(',')
        item = ScheduleItem(vals[0], vals[1], vals[2])
        log('Parsed entry %s: "%s"' % (num, item))

        # Should this item be started?
        if item.check_time():
            cmd = item.make_cmd()
            log('  Starting item (%s)' % cmd)
            os.system(cmd)
            s = '#' + s
        log()
        num += 1

        new_schedule += s

    fd = open(SCHEDULE, 'w')
    fd.write(new_schedule)
    fd.close()
    
    log('Done, exiting')


def schedule_init():
    """Create the schedule file if it doesn't exist"""
    
    # Is the schedule file present?
    if not os.path.isfile(SCHEDULE):
        log('no schedule, creating it')
        fd = open(SCHEDULE, 'w')
        fd.write('#TIMESTAMP ')
        fd.write(time.strftime('%Y-%m-%d %H:%M:%S'))
        fd.write('\n')
        fd.close()


def schedule_recording(start_time_s, length_secs, cmd):
    '''Schedule a new recording. The start time is a unix timestamp.'''

    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_s))
    s = '%s,%s,%s\n' % (ts, length_secs, cmd)

    schedule_init()
    
    # Append to the schedule file
    fd = open(SCHEDULE, 'a')
    fd.write(s)
    fd.close()

    log('ADD: %s' % s.strip())

    # Run the scheduler right here in case the recording should be
    # started immediately
    main()
    
    
if __name__ == '__main__':
    main()
    
