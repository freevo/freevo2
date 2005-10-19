# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# singleton.py - the Freevo singleton object
# -----------------------------------------------------------------------------
#
# singleton object based on new style classes.  This object comes from the
# the python docs found at http://www.python.org/2.2/descrintro.html
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dan Casimiro <dan.casimiro@gmail.com>
# Maintainer:    Dan Casimiro <dan.casimiro@gmail.com>
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
class Singleton(object):
    """
    This is a new style singleton class.  The original code is found in the
    python docs at http://www.python.org/2.2/descrintro.html

    To create a singleton class, you subclass from Singleton; each subclass
    will have a single instance, no matter how many times its constructor is
    called. To further initialize the subclass instance, subclasses should
    override 'init' instead of __init__ - the __init__ method is called each
    time the constructor is called. For example:

    >>> class MySingleton(Singleton):
    ...     def init(self):
    ...         print "calling init"
    ...     def __init__(self):
    ...         print "calling __init__"
    ... 
    >>> x = MySingleton()
    calling init
    calling __init__
    >>> assert x.__class__ is MySingleton
    >>> y = MySingleton()
    calling __init__
    >>> assert x is y
    """
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass
