#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# wap_login.rpy - Wap interface login form.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.2  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */
#endif

from www.wap_types import WapResource, FreevoWapResource

class WLoginResource(FreevoWapResource):

    def _render(self, request):

        fv = WapResource()
        form = request.args

        user = fv.formValue(form, 'user')
        passw = fv.formValue(form, 'passw')
        action = fv.formValue(form, 'action')
        
        fv.printHeader()

        fv.res += '  <card id="card1" title="Freevo Wap">\n'
        fv.res += '   <p><big><strong>Freevo Wap Login</strong></big></p>\n'

        if action <> "submit":

            fv.res += '       <p>User : <input name="user" title="User" size="15"/><br/>\n'
            fv.res += '          Passw : <input name="passw" type="password" title="Password" size="15"/></p>\n'
            fv.res += '   <do type="accept" label="Login">\n'
            fv.res += '     <go href="wap_rec.rpy" method="post">\n'
            fv.res += '       <postfield name="u" value="$user"/>\n'
            fv.res += '       <postfield name="p" value="$passw"/>\n'
            fv.res += '     </go>\n'
            fv.res += '   </do>\n'
            fv.res += '  </card>\n'

        fv.printFooter()

        return String( fv.res )

resource = WLoginResource()
