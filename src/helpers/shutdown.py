# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# shutdown.py - auto shutdown helper
# -----------------------------------------------------------------------------
# $Id$
#
# The shutdown helper will auto shutdown the system when nothing important is
# running right now and set a wakeup timer when needed. It can be used with
# the recordserver to power on and off the pc for recordings.
#
# On startup the helper will wait at least 30 minutes before doing anything.
# After that time, it will send a status rpc to all entities on the mbus.
# it will check 'idle', 'busy' and 'wakeup' from the return. Entities not
# answering will be ignored. 'idle' is the idle time of an entity (e.g. the
# Freevo GUI). When the idletime is less than 30 minutes, the system won't shut
# down. The Freevo GUI will only report an idle time greater zero if it is
# showing the menu and the idle time will be the time between the last event
# and the current time in minutes. The 'busy' attribute is a hint how long
# the entity will be busy (minimum) to give the helper an idea how long to
# wait. The 'wakeup' attribute defines a wakeup time that will be set using an
# external program defined in config.SHUTDOWN_WAKEUP_CMD to schedule the
# wakeup.
#
# If the idle time is lower 30 minutes or an entity is busy, the helper will
# wait min(max(30 - idletime, busy), 30) minutes before the next check. When
# an entity joins or leaves the mbus, the timer for the next check will be set
# to one minute again.
#
# If no entity is against system shutdown the helper will check if important
# programs are running. Some of this programs are defined in the helper, like
# wget, encoder and burning applications. The user can add more programs using
# the config variable SHUTDOWN_IMPORTANT_PROGRAMS. If you use the pc also for
# daily work and you shut down X at the end, the windowmanager is a good
# program to add here.
#
# If also no important programs are running, the helper will check login shells
# using /var/run/utmp using 'who'. An idle time lower 30 minutes on a login
# shell will also prevent system shutdown. This is usefull when you also use
# remote logins on this machine.
#
# When nothing would prevent a shutdown, a timer is started. The helper will
# check all this 5 times with an one minute intervall. If nothing changes on
# the status, the system will shut down.
#
#
# Note: There is a X idletime checker missing. If the user diesn't shut down
# X and uses software suspend, there is no way to detect user activity on X.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

# python imports
import os
import sys
import logging
import popen2
import time

# notifier and mbus
import notifier
import mbus

# freevo imports
import config
import mcomm
import util.popen

# get logging object
log = logging.getLogger()

# important programs that would prevent a shutdown when running. To add
# programs to this list, use the config variable SHUTDOWN_IMPORTANT_PROGRAMS
_important_programs = [ 'wget', 'cdrecord', 'growisofs', 'cdparanoia', 'lame',
                        'mencoder', 'transcode', 'dvdauthor', 'mpeg2enc',
                        'rsync', 'gcc', 'g++', 'make' ]

# internal variables
POLL_INTERVALL          = 60000    #  1 minute
FIRST_START             = 1200000  # 30 minutes
USER_IDLETIME           = 30       # 30 minutes
MAX_ENTITY_IDLETIME     = 30       # 30 minutes


if 0:
    # variables for testing
    POLL_INTERVALL      = 1000     # 1 second
    FIRST_START         = 1000     # 1 second
    USER_IDLETIME       = 1        # 1 minute
    MAX_ENTITY_IDLETIME = 1        # 1 minute


class Shutdown:
    """
    Class handling system shutdown.
    """
    def __init__(self):
        notifier.addTimer(FIRST_START, self.check_mbus)
        # notifier check timer, not set by first FIRST_START waiting
        self.timer = None
        # counter how often the shutdown function warns before real
        # shutdown (6 == 5 minutes)
        self.shutdown_counter = 6
        # last wakeuptime
        self.__last_wakeuptime = 0
        # get entity change notifications
        mcomm.register_entity_notification(self.entity_update)


    def entity_update(self, entity):
        """
        An entity was added/removed from the mbus.
        """
        if not self.timer:
            # we are in the startup mode (30 minutes wait)
            return
        log.warning('entity change, set timer %s seconds' % \
                    (POLL_INTERVALL / 1000))
        notifier.removeTimer(self.timer)
        self.timer = notifier.addTimer(POLL_INTERVALL, self.check_mbus)


    def check_programs(self):
        """
        Check for running programs who could prevent a shutdown.
        """
        for id in os.listdir('/proc'):
            if id.isdigit():
                cmdline = os.path.join('/proc/', id, 'cmdline')
                f = open(cmdline)
                cmd = os.path.basename(f.readline().split('\0')[0])
                if cmd in _important_programs + \
                       config.SHUTDOWN_IMPORTANT_PROGRAMS:
                    log.info('%s is running, not ready for shutdown' % cmd)
                    return False
                f.close()
        return True


    def check_login(self):
        """
        Check /var/run/utmp using 'who' to get the uder idle time
        Note: This is bad, reading /var/run/utmp would be a better idea
        """
        idle = 1000
        child = popen2.Popen3(['who', '-u'])
        while True:
            line = child.fromchild.readline().replace('\n', ' ')
            if not line:
                break
            while line.find('  ') != -1:
                line = line.replace('  ', ' ')
            timer = line.split(' ')[5].split(':')
            if len(timer) != 2:
                # not idle
                idle = 0
                continue
            idle = min(idle, int(timer[0]) * 60 + int(timer[1]))
        child.wait()
        if idle < USER_IDLETIME:
            log.info('user idle time: %s minutes' % idle)
        return idle >= USER_IDLETIME


    def rpcreturn(self, return_list):
        """
        Handle status.return messages.
        """
        if isinstance(return_list, mbus.types.MError):
            # error, entity can't answer to that request
            return

        # some debug
        log.info('Answer from %s' % return_list[0][0])

        # get the attributes as dict
        attributes = dict(return_list[0][2])

        if attributes.has_key('idle'):
            # set minimum entity idletime
            self.idletime = min(self.idletime, attributes['idle'])
        if attributes.has_key('busy'):
            # set maximum busy time
            self.busytime = max(self.busytime, attributes['busy'])
        if attributes.has_key('wakeup'):
            # set minimum wakeup time
            if self.wakeuptime:
                self.wakeuptime = min(attributes['wakeup'], self.wakeuptime)
            else:
                self.wakeuptime = attributes['wakeup']


    def check_mbus(self):
        """
        Send a status request to all mbus entities to get the status.
        """
        if not self.timer and not self.shutdown_counter:
            # looks like we came out of hibernate
            log.info('reset all shutdown timer')
            self.shutdown_counter = 6
            notifier.addTimer(FIRST_START, self.check_mbus)
            return False

        log.info('checking for possible system shutdown')
        # next wakeup
        self.wakeuptime = 0
        # minimum idletime in minutes
        self.idletime   = 1000
        # maximum busy time
        self.busytime   = 0

        for entity in mcomm.instance().entities:
            # ask entity status
            log.info('send status rpc to %s' % entity)
            entity.status(callback=self.rpcreturn)
        # set timer for shutdown in 5 seconds
        self.timer = notifier.addTimer(5000, self.check_shutdown)
        return False


    def check_shutdown(self):
        """
        Check if shutdown is possible and shutdown the system.
        """
        if self.wakeuptime != self.__last_wakeuptime:
            # there is a new wakeup time
            log.info('set wakeup time: %s' % self.wakeuptime)
            self.__last_wakeuptime = self.wakeuptime
            util.popen.Process(config.SHUTDOWN_WAKEUP_CMD % self.wakeuptime)

        wait = 0
        if self.idletime < MAX_ENTITY_IDLETIME:
            log.info('Entity idletime is %s, waiting %s minutes' % \
                     (self.idletime, 30 - self.idletime))
            wait = 30 - self.idletime
        else:
            log.info('Minimum idletime is %s, continue' % self.idletime)
            
        if self.busytime:
            log.info('Entity is busy at least %s minutes' % self.busytime)
            wait = max(wait, self.busytime)

        wakeup = int((self.wakeuptime - time.time()) / 60)
        if wakeup < 0:
            log.error('Correct buggy wakeup time from %s minutes' % wakeup)
            wakeup = 10
            
        if wakeup < 30:
            log.info('Wakeup time is in %s minutes, do not shutdown' % wakeup)
            wait = max(wait, wakeup + 5)

        if wait:
            # wait a maximum of 30 minutes
            wait = min(30, wait)
            log.info('Next check in %s minutes' % wait)
            # set a new timer
            self.timer = notifier.addTimer(wait * 60000, self.check_mbus)
            # reset counter
            self.shutdown_counter = 6
            return False

        # Wakeup seems possible based on the mbus entities, check other
        # stuff like external logins and important programs
        possible = True
        if not self.check_programs():
            possible = False
        else:
            try:
                if not self.check_login():
                    possible = False
            except:
                # maybe the 'who' parser is buggy
                log.exception('who checking, please report this trace')

        if not possible:
            # reschedule checking
            self.timer = notifier.addTimer(POLL_INTERVALL, self.check_mbus)
            # reset counter
            self.shutdown_counter = 6
            return False

        # looks like shutdown is possible
        log.info('shutdown possible')
        # decr. counter
        self.shutdown_counter -= 1

        if self.shutdown_counter:
            # let's warn this time
            log.warning('system shutdown system in %s minutes' % \
                        self.shutdown_counter)
            self.timer = notifier.addTimer(POLL_INTERVALL, self.check_mbus)
            return False

        # ok, do the real shutdown
        log.warning('shutdown system')

        # shutdown the system
        util.popen.Process(config.SHUTDOWN_SYS_CMD)

        # set new timer in case we hibernate, set self.timer so it looks like
        # the normal startup timer
        self.timer = None
        notifier.addTimer(FIRST_START, self.check_mbus)
        return False




def help():
    print 'Freevo shutdown helper'
    print
    print 'usage: freevo shutdown'
    print
    print 'This helper will auto shutdown the pc and schedule a wakeup timer.'
    print 'It is written for the use with the recordserver to power up the pc'
    print 'before a recording starts and shut down later.'
    print 'The helper will check if mbus entities like the Freevo GUI are idle'
    print 'and entities like the recordserver aren\'t busy. It will also check'
    print 'logins on the machine (idle time < 30 minutes will prevent system'
    print 'shutdown) and if important prograns are running.'
    print
    if not hasattr(config, 'SHUTDOWN_IMPORTANT_PROGRAMS'):
        print 'You need to set SHUTDOWN_IMPORTANT_PROGRAMS in local_conf.py to'
        print 'define a list of programs which should prevent a shutdown. When'
        print 'the machine is also used a workstation, the windowmanager is a'
        print 'good program to add here.'
        print
        print 'Examples:'
        print '# no special programs'
        print 'SHUTDOWN_IMPORTANT_PROGRAMS = [ ]'
        print '# sawfish window manager'
        print 'SHUTDOWN_IMPORTANT_PROGRAMS = [ \'sawfish\' ]'
        print
        print 'Besides SHUTDOWN_IMPORTANT_PROGRAMS the following programs will'
        print 'prevent a system shutdown:'
        prg = _important_programs
    else:
        print 'The following programs will prevent system shutdown:'
        prg = _important_programs + config.SHUTDOWN_IMPORTANT_PROGRAMS
    prg = ' '.join(prg)
    while len(prg) > 75:
        line = prg[:prg[:70].rfind(' ')]
        print line
        prg = prg[len(line)+1:]
    print prg
    print
    if not hasattr(config, 'SHUTDOWN_WAKEUP_CMD'):
        print
        print 'Set SHUTDOWN_WAKEUP_CMD in the local_conf.py to a program that'
        print 'can schedule a wakeup. The program is a string with %s as'
        print 'variable for the real wakeup time.'
        print
        print 'Example:'
        print '# use nvram_wakeup:'
        print 'SHUTDOWN_WAKEUP_CMD = \'/usr/local/bin/nvram-wakeup -C \' +'
        print '    \'/etc/nvram-wakeup.conf --directisa -s %s'
        print
    sys.exit(0)




if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
    help()

if not hasattr(config, 'SHUTDOWN_WAKEUP_CMD'):
    print 'Error: SHUTDOWN_WAKEUP_CMD not found.',
    print 'Please read the configuration help.'
    print
    help()

if not hasattr(config, 'SHUTDOWN_IMPORTANT_PROGRAMS'):
    print 'Error: SHUTDOWN_IMPORTANT_PROGRAMS not found',
    print 'Please read the configuration help.'
    print
    help()


# the shutdown object
s = Shutdown()

# start notifier loop
notifier.loop()
