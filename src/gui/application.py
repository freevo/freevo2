# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# application - application widget
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
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

# gui imports
import kaa.candy

from widget import Widget, WidgetStyles

class ApplicationStyles(WidgetStyles):
    """
    Dict to store the different application classes
    """
    candyxml_name = 'application'


class Application(Widget):
    """
    Application base class.
    """
    candyxml_name = 'application'

    def __init__(self, widgets, background=None, context=None):
        if kaa.candy.is_template(background):
            background = background(context=context)
        self.background = background
        super(Application, self).__init__(None, None, widgets, context=context)

    def sync_context(self):
        """
        Adjust to a new context
        """
        super(Application, self).sync_context()
        if not self.background:
            return
        if not self.background.supports_context(self.context):
            new = self.background.__template__(context=self.context)
            self.background.parent.replace(self.background, new)
            self.background = new
        else:
            self.background.context = self.context

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        attrs = super(Application, cls).candyxml_parse(element)
        return kaa.candy.XMLdict(widgets=attrs.get('widgets'), background=attrs.get('background'))
