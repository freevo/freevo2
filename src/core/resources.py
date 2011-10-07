# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# resources.py - Resource Management
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

# kaa imports
import kaa

class ResourceHandler(object):
    """
    The ResourceHandler inherit from it if you want to use resources that need
    a specific access rights.
    """
    __resources = {}

    @kaa.coroutine(policy=kaa.POLICY_SYNCHRONIZED)
    def get_resources(self, *resources, **kwargs):
        """
        Reserve a list of resources. If one or more resources can not be
        reserved, the whole operation fails. The function will return the
        list of failed resources with this instance having this resource.
        If the keyword force=True is set, the function will try to suspend
        all modules holding a needed ressource. In this case the function
        returns False on failure (not possible), True when all resources
        are reserved or InProgress if it is possible and takes a while.
        """
        if not hasattr(self, '_ressources_suspended'):
            self._ressources_suspended = []
        blocked = {}
        blocking = []
        for r in resources:
            module = ResourceHandler.__resources.get(r)
            if module is None or module == self:
                continue
            if module.can_suspend():
                blocked[r] = module
                if not module in blocking:
                    blocking.append(module)
            else:
                # TODO: return bad ressources so the app could
                # try to reserve resources without that bad one.
                yield False
        if blocked and not kwargs.get('force'):
            # failed to reserve but it would be possible, return list
            # of blocking resources
            yield blocked
        # suspend modules (if any)
        for module in blocking:
            if not module in self._ressources_suspended:
                self._ressources_suspended.append(module)
            answer = module.suspend()
            if isinstance(answer, kaa.InProgress):
                yield answer
        # since get_resources is decorated with the locking
        # keyword, no other application or plugin could have
        # gotten the ressources we need and we are free to
        # take them.

        # FIXME: what happens if a resumed application will
        # try to get the ressources and can't do that? We
        # need a way for application/plugin x to connect to
        # the _ressources_suspended list of y.

        # reserve all resources
        for r in resources:
            ResourceHandler.__resources[r] = self
        if kwargs.get('force'):
            yield True
        yield {}

    def free_resources(self, resume=False):
        """
        Free all resources blocked by this instance. If resume is True, this
        function will also resume all modules this object has suspended.
        """
        if not hasattr(self, '_ressources_suspended'):
            self._ressources_suspended = []
        for res, app in ResourceHandler.__resources.items()[:]:
            if app == self:
                del ResourceHandler.__resources[res]
        if not resume:
            # done here
            return True
        # resume suspended modules
        for handler in self._ressources_suspended:
            handler.resume()
        # clear list with suspended since all resumed
        self._ressources_suspended = []

    def can_suspend(self):
        """
        Return if it is possible for this handler to release its resource.
        """
        return False

    def suspend(self):
        """
        Suspend this resource handler. Should free all the resources.
        """
        return False

    def resume(self):
        """
        Resume the plugin acquire all the resources again.
        """
        pass
