#if 0 /*
# -----------------------------------------------------------------------
# schedulefavorites.py - A helper to run in order to schedule any favories
#                        for recording.  This should be ran after updating
#                        your program guide.  This step will eventually be
#                        handled by the recording server.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/06/06 07:32:02  dischi
# fix crash
#
# Revision 1.1  2003/09/08 19:41:55  rshortt
# A helper to schedule your favorites for recording.
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

import config
import tv.record_client as rc

(result, response) = rc.updateFavoritesSchedule()
print response
