# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# system.py - System control
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2011 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

import sys
import os

# kaa imports
import kaa

# freevo imports
import api as freevo

__all__ = ['manager', 'signals']

class BaseSystemManager(kaa.Object):
    """
    Base Class to control the state of the system.
    Concrete instance of this class allow the user to test whether an action is available and also invoke that action.
    This class allows the system to be powered off, rebooted, suspended or hibernated.
    It also allow interested parties to connect to signals to be informed of the change in state or to prevent the state
    change.
    """
    __kaasignals__ = {
        'check-sleep':
            '''
            Emitted when the system manager has been requested to suspend/hibernate. This gives interested parties
            a chance to stop the system sleeping by returning false to this signal.

            .. describe:: def callback(sleep_type)

               :param sleep_type: A string describing the method that is intend to be used to sleep the computer.
               :type sleep_type: str
            ''',
        'sleeping':
            '''
            Emitted when freevo is about to suspend/hibernate the system.

            .. describe:: def callback(sleep_type)

               :param sleep_type: A string describing the method that is intend to be used to sleep the computer.
               :type sleep_type: str
            ''',
        'check-exit':
            '''
            Emitted when the system manager has been requested to exit/shutdown/reboot. This gives interested parties
            a chance to stop the system exiting by returning false to this signal.

            .. describe:: def callback(exit_type)

               :param sleep_type: A string describing the method that is exit freevo (exit/shutdown/reboot).
               :type sleep_type: str
            ''',
        'exiting':
            '''
            Emitted when freevo is about to exit.

            .. describe:: def callback(exit_type)

               :param sleep_type: A string describing the method that is exit freevo (exit/shutdown/reboot).
               :type sleep_type: str
            '''
    }

    def can_suspend(self):
        """
        Returns whether the system can be suspended.
        """
        return False

    def can_hibernate(self):
        """
        Returns whether the system can be hibernated.
        """
        return False

    def can_shutdown(self):
        """
        Returns whether the system can be shutdown/powered off.
        """
        return False

    def can_reboot(self):
        """
        Returns whether the system can be rebooted.
        """
        return False

    def do_suspend(self):
        """
        INTERNAL: This function should be overridden by subclasses to perform the actual action.
        """
        pass
    
    def do_hibernate(self):
        """
        INTERNAL: This function should be overridden by subclasses to perform the actual action.
        """
        pass
    
    def do_shutdown(self):
        """
        INTERNAL: This function should be overridden by subclasses to perform the actual action.
        """
        pass

    def do_reboot(self):
        """
        INTERNAL: This function should be overridden by subclasses to perform the actual action.
        """
        pass

    def exit(self):
        """
        Exit freevo.
        This function should not normally return unless the exit is blocked by another part freevo in which case
        it will return False.
        """
        exit = self.signals['check-exit'].emit('exit')
        if exit:
            self.signals['exiting'].emit('exit')
            sys.exit(0)
        return exit

    def restart(self):
        """
        Restart freevo.
        This function should not normally return unless the exit is blocked by another part freevo in which case
        it will return False.
        """
        exit = self.signals['check-exit'].emit('restart')
        if exit:
            self.signals['exiting'].emit('restarting')
            kaa.main.signals['shutdown'].connect(os.execvp, sys.argv[0], sys.argv)
            sys.exit(0)
        return exit

    def suspend(self):
        """
        Suspend the system.
        If the system is to be suspend True will be return, if another part of freevo blocks the sleep it will return
        False.
        """
        if self.can_suspend():
            suspend = self.signals['check-sleep'].emit('suspend')
            if suspend:
                self.signals['sleeping'].emit('suspend')
                self.do_suspend()
        else:
            suspend = False
        return suspend

    def hibernate(self):
        """
        Hibernate the system.
        If the system is to be hibernated True will be return, if another part of freevo blocks the sleep it will return
        False.
        """
        if self.can_hibernate():
            hibernate = self.signals['check-sleep'].emit('hibernate')
            if hibernate:
                self.signals['sleeping'].emit('hibernate')
                self.do_hibernate()
        else:
            hibernate = False
        return hibernate

    def shutdown(self):
        """
        Shutdown/power off the system.
        If the system is to be shutdown True will be return, if another part of freevo blocks this it will return
        False.
        """
        if self.can_shutdown():
            shutdown = self.signals['check-exit'].emit('shutdown')
            if shutdown:
                self.signals['exiting'].emit('shutdown')
                self.do_shutdown()
        else:
            shutdown = False
        return shutdown

    def reboot(self):
        """
        Reboot the system.
        If the system is to be rebooted True will be return, if another part of freevo blocks this it will return
        False.
        """
        if self.can_reboot():
            reboot = self.signals['check-exit'].emit('reboot')
            if reboot:
                self.signals['exiting'].emit('reboot')
                self.do_reboot()
        else:
            reboot = False
        return reboot

class ConsoleKitSystemManager(BaseSystemManager):
    """
    System manager that uses the ConsoleKit and UPower dbus interfaces to shutdown/reboot or suspend/hibernate the system.
    """
    def __init__(self):
        super(ConsoleKitSystemManager, self).__init__()
        import dbus
        bus = dbus.SystemBus()
        self.consolekit_proxy = bus.get_object("org.freedesktop.ConsoleKit", "/org/freedesktop/ConsoleKit/Manager")
        self.consolekit_intf = dbus.Interface(self.consolekit_proxy, 'org.freedesktop.ConsoleKit.Manager')
        self.upower_proxy = bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower")
        self.upower_intf = dbus.Interface(self.upower_proxy, 'org.freedesktop.UPower')


    def can_suspend(self):
        return self.upower_intf.SuspendAllowed()

    def can_hibernate(self):
        return self.upower_intf.HibernateAllowed()
    
    def can_shutdown(self):
        return self.consolekit_intf.CanStop()

    def can_reboot(self):
        return self.consolekit_intf.CanRestart()

    def do_suspend(self):
        self.upower_intf.Suspend()

    def do_hibernate(self):
        self.upower_intf.Hibernate()

    def do_shutdown(self):
        self.consolekit_intf.Stop()

    def do_reboot(self):
        self.consolekit_intf.Restart()

class LogindSystemManager(BaseSystemManager):
    """
    System manager that uses the logind dbus interface to shutdown/reboot/suspend or hibernate the system.
    """
    def __init__(self):
        super(LogindSystemManager, self).__init__()
        import dbus
        bus = dbus.SystemBus()
        self.logind_proxy = bus.get_object("org.freedesktop.login1", "/org/freedesktop/login1")
        self.logind_intf = dbus.Interface(self.logind_proxy, 'org.freedesktop.login1.Manager')

    def can_suspend(self):
        return self.logind_intf.CanSuspend()

    def can_hibernate(self):
        return self.logind_intf.CanHibernate()

    def can_shutdown(self):
        return self.logind_intf.CanPowerOff()

    def can_reboot(self):
        return self.logind_intf.CanReboot()

    def do_suspend(self):
        self.logind_intf.Suspend()

    def do_hibernate(self):
        self.logind_intf.Hibernate()

    def do_shutdown(self):
        self.logind_intf.PowerOff()

    def do_reboot(self):
        self.logind_intf.Reboot()

class CommandSystemManager(BaseSystemManager):
    """
    System manager that uses user defined commands to control the system. If a particular command is not specified then
    the associated can_<action> will return false and that action will be disabled.
    """
    def __init__(self, shutdown, reboot, suspend, hibernate):
        super(CommandSystemManager, self).__init__()
        self.shutdown_cmd = shutdown
        self.reboot_cmd = reboot
        self.suspend_cmd = suspend
        self.hibernate_cmd = hibernate

    def can_shutdown(self):
        return self.shutdown_cmd and True or False

    def can_reboot(self):
        return self.reboot_cmd and True or False

    def can_suspend(self):
        return self.suspend_cmd and True or False

    def can_hibernate(self):
        return self.hibernate_cmd and True or False

    def do_shutdown(self):
        os.system(self.shutdown_cmd)

    def do_reboot(self):
        os.system(self.reboot_cmd)

    def do_suspend(self):
        os.system(self.suspend_cmd)

    def do_hibernate(self):
        os.system(self.hibernate_cmd)

# Setup the manager, first if the user has specified custom commands we should use those
if freevo.config.system.shutdown_command or freevo.config.system.reboot_command or\
   freevo.config.system.suspend_command or freevo.config.system.hibernate_command:
    manager = CommandSystemManager(freevo.config.system.shutdown_command, freevo.config.system.reboot_command,
                                   freevo.config.system.suspend_command, freevo.config.system.hibernate_command)
else:
    # If no commands where specified try logind, then console kit and final revert to the BaseSystemManager that
    # can only exit freevo.
    for manager_class in (LogindSystemManager, ConsoleKitSystemManager, BaseSystemManager):
        try:
            manager = manager_class()
            break
        except:
            pass

signals = manager.signals