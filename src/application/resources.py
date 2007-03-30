# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# resources.py - Ressource Management
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
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

_resources = {}

def get_resources(instance, *resources):
    """
    Reserve a list of resources. If one or more resources can not be
    reserved, the whole operation fails. The function will return the
    list of failed resources with the instance having this resource.
    """
    blocked = {}
    for r in resources:
        if r in _resources:
            blocked[r] = _resources[r]
    if blocked:
        # failed to reserve
        return blocked
    # reserve all resources
    for r in resources:
        _resources[r] = instance
    return {}


def free_resources(instance, *resources):
    """
    Free all resources blocked by the instance. If not resources are
    provided, free all resources.
    """
    for res, app in _resources.items()[:]:
        if app == instance and (not resources or res in resources):
            del _resources[res]
