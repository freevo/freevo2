# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# rect.py - rectangle calculation functions
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Jason Tackaberry <tack@sault.org>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

import math

empty = (0, 0), (0, 0)

def union(r1, r2):
    r1x, r1y, r1w, r1h = r1[0] + r1[1]
    r2x, r2y, r2w, r2h = r2[0] + r2[1]

    Rx = min(r1x, r2x)
    Ry = min(r1y, r2y)
    Rw = max(r1x+r1w, r2x+r2w) - Rx
    Rh = max(r1y+r1h, r2y+r2h) - Ry

    return (Rx, Ry), (Rw, Rh)


def point_in_rect(pt, r):
    rx, ry, rw, rh = r[0] + r[1]
    px, py = pt

    if px < rx or px > rx + rw or \
           py < ry or py > ry + rh:
        return False

    return True


def intersect(r1, r2):
    r1x, r1y, r1w, r1h = r1[0] + r1[1]
    r2x, r2y, r2w, r2h = r2[0] + r2[1]

    # No intersection for these cases.
    if r1x + r1w < r2x or \
           r1x > r2x + r2w or \
           r1y + r1h < r2y or \
           r1y > r2y + r2h:
        return empty

    Rx = max(r1x, r2x)
    Ry = max(r1y, r2y)
    Rw = min(r1x+r1w, r2x+r2w) - Rx
    Rh = min(r1y+r1h, r2y+r2h) - Ry

    if 0 in (Rw, Rh):
        return empty

    return (Rx, Ry), (Rw, Rh)


def contained_in(r1, r2):
    """
    Returns True if r1 is fully contained in r2.
    """
    return intersect(r1, r2) == r1


def contained_in_list(r, list):
    for rect in list:
        if intersect(r, rect) == r:
            return True
    return False


def offset(r, pos, size = (0, 0)):
    (rx, ry), (rw, rh)= r
    offset_x, offset_y = pos
    offset_w, offset_h = size

    return (rx + offset_x, ry + offset_y), (rw + offset_w, rh + offset_h)


def offset_list(list, pos):
    new_list = []
    for r in list:
        new_list.append( offset(r, pos) )
    return new_list


def clip(r1, r2):
    return intersect(r1, r2)


def clip_list(list, rect):
    new_list = []
    for r in list:
        i = intersect(r, rect)
        if i != empty:
            new_list.append(i)
    return new_list


def translate((pos, size), offset = (0, 0), scale = (1.0, 1.0),
          scale_pos = False, pixel_aspect = 1):
    pos = pos[0] + offset[0], pos[1] + offset[1]
    size = int(math.ceil(size[0] * scale[0])), \
           int(math.ceil(size[1] * scale[1]))
    if scale_pos:
        pos = int(pos[0] * scale[0]), int(pos[1] * scale[1])
    return pos, size


def translate_list(list, offset = (0, 0), scale = (1.0, 1.0),
		   scale_pos = False, pixel_aspect = 1):
    new_list = []
    for r in list:
        new_list.append( translate(r, offset, scale, scale_pos, pixel_aspect) )
    return new_list


def reduce(list):
    """
    Removes redundant rectangles.
    """
    if len(list) == 0:
        return list

    list = list[:]
    new_list = []
    while len(list):
        rect = list.pop()
        if rect[1][0] == 0 or rect[1][1] == 0:
            continue
        if not contained_in_list(rect, new_list) and \
               not contained_in_list(rect, list):
            new_list.append(rect)
    return new_list


def optimize_for_rendering(list):
    list = reduce(list)

    orig_len = len(list)
    new_list = []

    while len(list):
        r1 = list.pop()
        merged = False
        for r2 in list[:]:
            area_r1 = r1[1][0] * r1[1][1]
            area_r2 = r2[1][0] * r2[1][1]

            # If these two rectangles overlap more than half the area of the
            # smaller one, then take the union instead.
            r3 = intersect(r1, r2)
            if r3 != empty:
                area_r3 = r3[1][0] * r3[1][1]
                if area_r3 > min(area_r1, area_r2) / 2:
                    list.remove(r2)
                    new_list.append( union(r1, r2) )
                    merged = True

            # If the union of these two rectangles has an area at most 20%
            # larger than the two rectangles separately, then take the
            # union instead.
            # TODO: test empirically if 50% is a good figure.
            if not merged:
                r3 = union(r1, r2)
                area_r3 = r3[1][0] * r3[1][1]
                if area_r3 < (area_r1 + area_r2) * 1.5:
                    list.remove(r2)
                    new_list.append(r3)
                    merged = True

        if not merged:
            new_list.append(r1)

    if len(new_list) != orig_len:
        # Keep passing over until we stop making progress.
        return optimize_for_rendering(new_list)

    return new_list


def remove_intersections(list):

    # FIXME: this function could be smarter.  Instead of creating a union
    # of two rectangles that intersect, it could create a number of smaller
    # rectangles that represent the same original area but don't intersect
    # if that total area is much less than the union would have been.

    list = reduce(list)

    orig_len = len(list)
    new_list = []
    while len(list):
        r1 = list.pop()
        merged = False
        for r2 in list[:]:
            if intersect(r1, r2) != empty:
                list.remove(r2)
                new_list.append( union(r1, r2) )
                merged = True
        if not merged:
            new_list.append(r1)

    if len(new_list) != orig_len:
        new_list = remove_intersections(new_list)

    return new_list
