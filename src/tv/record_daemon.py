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

    def __init__(self, start_time, cmd):
        # Convert start_time to Unix time if needed
        if type(start_time) == type(''):
            t = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            self.start_time = time.mktime(t)
        else:
            self.start_time = int(start_time)
        self.cmd = cmd

    def __str__(self):
        t = time.localtime(self.start_time)
        ts = time.strftime('%Y-%m-%d %H:%M:%S', t)
        s = '%s %s' % (ts, self.cmd)
        return s

    
def main():
    log('=' * 80)
    log('started at %s' % time.ctime())

    # Is the schedule file present?
    if not os.path.isfile(SCHEDULE):
        log('no schedule, exiting')
        fd = open(SCHEDULE, 'w')
        fd.write('#TIMESTAMP ')
        fd.write(time.strftime('%Y-%m-%d %H:%M:%S'))
        fd.write('\n')
        fd.close()
        sys.exit()

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
        item = ScheduleItem(vals[0], vals[1])
        log('Parsed entry %s: "%s"' % (num, item))

        # Should this item be started?
        tdiff = item.start_time - time.time()
        if -59 <= tdiff < 0:
            log('  Starting item')
            os.system(item.cmd + ' >& /dev/null &')
            s = '#' + s
        else:
            log('  Item tdiff = %s seconds, will not start' % tdiff)
        log()
        num += 1

        new_schedule += s

    fd = open(SCHEDULE, 'w')
    fd.write(new_schedule)
    fd.close()
    
    log('Done, exiting')
    

def schedule_recording(start_time, cmd):
    '''Schedule a new recording. The time is a time tuple.'''

    ts = time.strftime('%Y-%m-%d %H:%M:%S', start_time)
    s = '%s,%s\n' % (ts, cmd)

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
    
