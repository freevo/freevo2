# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# listing_area.py - A listing area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2004/09/07 18:45:17  dischi
# some design improvements, needs still much works
#
# Revision 1.8  2004/08/24 16:42:41  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.7  2004/08/22 20:06:18  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.6  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
#
# Revision 1.5  2004/08/05 17:30:24  dischi
# cleanup
#
# Revision 1.4  2004/07/27 18:52:30  dischi
# support more layer (see README.txt in backends for details
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# -----------------------------------------------------------------------


import copy
from mevas.image import CanvasImage
from area import Area


class ItemImage(CanvasImage):
    """
    An image object that can be drawn onto a layer. The difference between this
    and a normal object is that it also has a parameter for shadow values.
    """
    def __init__(self, image, pos, shadow):
        if shadow and shadow.visible and not image.has_alpha:
            # there are shadow informations and the image has no alpha
            # values, so draw a shadow. Bug: this only works for shadow.x
            # and shadow.y both greater 0
            CanvasImage.__init__(self, (image.width + shadow.x, image.height + shadow.y))
            self.draw_rectangle((shadow.x, shadow.y), (image.width, image.height),
                                shadow.color, 1)
            self.draw_image(image)
        else:
            # normal image
            CanvasImage.__init__(self, image)
        # set position of the object
        self.set_pos(pos)


    
class Listing_Area(Area):
    """
    this call defines the listing area
    """

    def __init__(self):
        Area.__init__(self, 'listing')
        self.content           = []
        self.last_listing      = []
        self.last_content_type = ''
        self.last_selection    = None
        self.last_start        = -1
        self.last_max_len      = -1
        self.empty_listing     = None
        self.arrows            = []


    def clear(self, keep_settings=False):
        """
        clear the listing area
        """
        # delete the listing
        for c in self.last_listing:
            for o in c[2]:
                o.unparent()
        self.last_listing = []
        # delete the arrows
        for a in self.arrows:
            a.unparent()
        self.arrows = []
        # reset variables
        if not keep_settings:
            self.last_content_type = ''
            self.last_selection    = None
            self.last_start        = -1
            self.last_max_len      = -1
        # delete 'empty listing' message
        if self.empty_listing:
            self.empty_listing.unparent()
            self.empty_listing = None
        
        
    def text_or_icon(self, string, x, width, font):
        l = string.split('_')
        if len(l) != 4:
            return string
        try:
            height = font.height
            image = os.path.join(self.settings.icon_dir, l[2].lower())
            if os.path.isfile(image + '.jpg'):
                image += '.jpg' 
            if os.path.isfile(image + '.png'):
                image += '.png'
            else:
                image = None
            if image:
                image = self.imagelib.load(image, (None, height))

                x_mod = 0
                if l[1] == 'CENTER':
                    x_mod = (width - image.width) / 2
                if l[1] == 'RIGHT':
                    x_mod = width - image.width
                return x_mod, image

        except KeyError:
            _debug_('no image %s' % l[2])
            pass

        mod_x = width - font.stringsize(l[3])
        if mod_x < 0:
            mod_x = 0
        if l[1] == 'CENTER':
            return mod_x / 2, l[3]
        if l[1] == 'RIGHT':
            return mod_x, l[3]
        return 0, l[3]


    def get_items_geometry(self, settings, menu, area_settings):
        """
        get the geometry of the items. How many items per row/col, spaces
        between each item, etc
        """
        # ok, we use settings + area_settings as key
        # FIXME: is that ok or do we need something else?
        key = '%s-%s-%s' % (settings, area_settings, self.layout.content.type)
        try:
            # returned cached information
            return menu.listing_area_dict[key]
        except (KeyError, AttributeError):
            pass
        
        content = self.calc_geometry(self.layout.content, copy_object=True)

        if content.type == 'text':
            items_w = content.width
            items_h = 0
        elif content.type == 'image' or content.type == 'image+text':
            items_w = 0
            items_h = 0

        # get the list of possible types we need for this
        # menu to draw correctly
        possible_types = {}
        for i in menu.choices:
            if hasattr(i, 'display_type') and i.display_type:
                x = i.display_type
                if content.types.has_key(x) and not possible_types.has_key(x):
                    possible_types[x] = content.types[x]
                x = '%s selected' % i.display_type
                if content.types.has_key(x) and not possible_types.has_key(x):
                    possible_types[x] = content.types[x]
        if content.types.has_key('default'):
            possible_types['default'] = content.types['default']
        if content.types.has_key('selected'):
            possible_types['selected'] = content.types['selected']

        hskip = 0
        vskip = 0
        # get the max height of a text item
        if content.type == 'text':
            for t in possible_types:
                ct = possible_types[t]

                rh = 0
                rw = 0
                if ct.rectangle:
                    rw, rh, r = self.get_item_rectangle(ct.rectangle, content.width,
                                                        ct.font.height)
                    hskip = min(hskip, r.x)
                    vskip = min(vskip, r.y)
                    items_w = max(items_w, r.width)

                items_h = max(items_h, ct.font.height, rh)

        elif content.type == 'image' or content.type == 'image+text':
            for t in possible_types:
                ct = possible_types[t]
                rh = 0
                rw = 0
                if ct.rectangle:
                    if content.type == 'image+text':
                        rw, rh, r = self.get_item_rectangle(ct.rectangle, ct.width,
                                                            max(ct.height,
                                                                int(ct.font.height * 1.1)))
                    else:
                        rw, rh, r = self.get_item_rectangle(ct.rectangle, ct.width,
                                                            ct.height)
                    hskip = min(hskip, r.x)
                    vskip = min(vskip, r.y)

                addh = 0
                if content.type == 'image+text':
                    addh = int(ct.font.height * 1.1)
                    
                items_w = max(items_w, ct.width, rw)
                items_h = max(items_h, ct.height + addh, rh + addh)


        else:
            _debug_('unknown content type %s' % content.type, 0)
            return None
        
        # shrink width for text menus
        width = content.width

        if items_w > width:
            width, items_w = width - (items_w - width), width 

        cols = 0
        rows = 0

        while (cols + 1) * (items_w + content.spacing) - \
              content.spacing <= content.width:
            cols += 1

        while (rows + 1) * (items_h + content.spacing) - \
              content.spacing <= content.height:
            rows += 1

        if not hasattr(menu, 'listing_area_dict'):
            menu.listing_area_dict = {}

        info = cols, rows, items_w + content.spacing, items_h + content.spacing, \
               -hskip, -vskip, width
        menu.listing_area_dict[key] = info
        return info


    def update(self):
        """
        update the listing area
        """
        menu      = self.menu
        settings  = self.settings
        area      = self.area_values
        content   = self.calc_geometry(self.layout.content, copy_object=True)

        if not len(menu.choices):
            if not self.empty_listing:
                self.clear()
                self.empty_listing = self.drawstring(_('This directory is empty'),
                                                     content.font, content)
            return
        
        # delete 'empty listing' message
        if self.empty_listing:
            self.empty_listing.unparent()
            self.empty_listing = None

        cols, rows, hspace, vspace, hskip, vskip, width = \
              self.get_items_geometry(settings, menu, area)

        menu.rows = rows
        menu.cols = cols
        
        if content.align == 'center':
            item_x0 = content.x + (content.width - cols * hspace) / 2
        else:
            item_x0 = content.x

        if content.valign == 'center':
            item_y0 = content.y + (content.height - rows * vspace) / 2
        else:
            item_y0 = content.y

        current_col = 1
        
        if content.type == 'image':
            width  = hspace - content.spacing
            height = vspace - content.spacing
            
        last_tvs      = ('', 0)
        all_tvs       = True
        tvs_shortname = True

        start   = (menu.selected_pos / (cols * rows)) * (cols * rows)
        end     = start + cols * rows
        listing = menu.choices[start:end]

        # do some checking if we have to redraw everything
        # or only update because the selection changed
        if self.last_content_type != content.type or \
           len(listing) != len(self.last_listing) or \
           self.last_start != start or self.last_max_len != len(menu.choices):
            self.last_content_type = content.type
            self.last_start        = start
            self.last_max_len      = len(menu.choices)
            redraw = True
        else:
            redraw = False
            
        if redraw:
            # delete all current gui objects
            self.clear(keep_settings=True)

        for choice in listing:
            draw_this_item = True

            #
            # check if this items needs to be drawn or not
            #
            if redraw:
                self.last_listing.append((choice.name, choice.image, []))
                gui_objects = self.last_listing[-1][2]
            else:
                index = listing.index(choice)
                # check if the item is still the same
                if self.last_listing[index][:2] != (choice.name, choice.image):
                    for o in self.last_listing[index][2]:
                        o.unparent()
                    gui_objects = []
                    self.last_listing[index] = choice.name, choice.image, gui_objects
                elif choice == self.last_selection or choice == menu.selected:
                    gui_objects = self.last_listing[index][2]
                    while len(gui_objects):
                        o = gui_objects.pop()
                        o.unparent()
                else:
                    draw_this_item = False


            # init the 'val' settings
            if draw_this_item:
                if content.types.has_key( '%s selected' % choice.type ):
                    s_val = content.types[ '%s selected' % choice.type ]
                else:
                    s_val = content.types[ 'selected' ]

                if content.types.has_key( choice.type ):
                    n_val = content.types[ choice.type ]
                else:
                    n_val = content.types['default']


                if choice == menu.selected:
                    val = s_val
                else:
                    val = n_val

            #
            # text listing --------------------------------------------------------
            #
            if draw_this_item and content.type == 'text':
                x0     = item_x0
                y0     = item_y0
                icon_x = 0
                icon   = None
                align   = val.align or content.align
                
                icon_type = None
                if hasattr(val, 'icon'):
                    icon_type = val.icon

                text = choice.name
                if not text:
                    text = "unknown"

                if not choice.icon and not icon_type:
                    if choice.type == 'playlist':
                        text = 'PL: %s' % text

                    if choice.type == 'dir' and choice.parent and \
                       choice.parent.type != 'mediamenu':
                        text = '[%s]' % text

                if choice != menu.selected and hasattr( choice, 'outicon' ) and \
                       choice.outicon:
                    icon = self.loadimage(choice.outicon, (vspace-content.spacing,
                                                            vspace-content.spacing))
                elif choice.icon:
                    icon = self.loadimage(choice.icon, (vspace-content.spacing,
                                                         vspace-content.spacing))
                if not icon and icon_type:
                    icon = self.loadimage(settings.icon_dir + '/' + icon_type,
                                          (vspace-content.spacing, vspace-content.spacing))

                #
                # display an icon for the item
                #
                x_icon = 0
                if icon:
                    mx = x0
                    icon_x = vspace
                    x_icon = icon_x
                    if align == 'right':
                        # know how many pixels to offset (dammed negative and max+X
                        # values in (x,y,width) from skin!)
                        r1 = r2 = None
                        if s_val.rectangle:
                            r1 = self.get_item_rectangle(s_val.rectangle,
                                                         width, s_val.font.height)[2]
                        if n_val.rectangle:
                            r2 = self.get_item_rectangle(n_val.rectangle,
                                                         width, n_val.font.height)[2]
                        min_rx = 0
                        max_rw = width
                        if r1:
                            min_rx = min( min_rx, r1.x )
                            max_rw = max( max_rw, r1.width )
                        if r2:
                            min_rx = min( min_rx, r2.x )
                            max_rw = max( max_rw, r2.width )

                        mx = x0 + width + hskip + ( max_rw + min_rx - width ) - icon_x 
                        x_icon = 0
                    gui_objects.append(self.drawimage(icon, (mx, y0)))

                #
                # draw the rectangle below the item
                #
                if val.rectangle:
                    r = self.get_item_rectangle(val.rectangle, width, val.font.height)[2]
                    b = self.drawbox(x0 + hskip + r.x + x_icon - \
                                     self.settings.box_under_icon * x_icon,
                                     y0 + vskip + r.y,
                                     r.width - icon_x + self.settings.box_under_icon * icon_x,
                                     r.height, r)
                    gui_objects.append(b)

                #
                # special handling for tv shows
                #
                if choice.type == 'video' and hasattr(choice,'tv_show') and \
                   choice.tv_show and (val.align=='left' or val.align=='') and \
                   (content.align=='left' or content.align==''):
                    sn = choice.show_name

                    if last_tvs[0] == sn[0]:
                        tvs_w = last_tvs[1]
                    else:
                        season  = 0
                        episode = 0
                        for c in menu.choices:
                            if c.type == 'video' and hasattr(c,'tv_show') and \
                               c.tv_show and c.show_name[0] == sn[0]:
                                # do not use val.font.stringsize because this will
                                # add shadow and outline values we add later for the
                                # normal text again. So just use val.font.font.stringsize
                                stringsize = val.font.font.stringsize
                                season  = max(season, stringsize(c.show_name[1]))
                                episode = max(episode, stringsize(c.show_name[2]))
                                if tvs_shortname and not c.image:
                                    tvs_shortname = False
                            else:
                                all_tvs = False

                        if all_tvs and not tvs_shortname and len(menu.choices) > 5:
                            tvs_shortname = True
                            
                        if all_tvs and tvs_shortname:
                            tvs_w = val.font.stringsize('x') + season + episode
                        else:
                            tvs_w = val.font.stringsize('%s x' % sn[0]) + season + episode
                        last_tvs = (sn[0], tvs_w)
                        
                    s = self.drawstring(' - %s' % sn[3], val.font, content,
                                        x=x0 + hskip + icon_x + tvs_w,
                                        y=y0 + vskip, width=width-icon_x-tvs_w, height=-1,
                                        align_h='left', dim=False, mode='hard')
                    gui_objects.append(s)
                    s = self.drawstring(sn[2], val.font, content,
                                        x=x0 + hskip + icon_x + tvs_w - 100,
                                        y=y0 + vskip, width=100, height=-1,
                                        align_h='right', dim=False, mode='hard')
                    gui_objects.append(s)
                    if all_tvs and tvs_shortname:
                        text = '%sx' % sn[1]
                    else:
                        text = '%s %sx' % (sn[0], sn[1])

                #
                # if the menu has an attr table, the menu is a table. Each
                # item _must_ have that many tabs as the table needs!!!
                #
                if hasattr(menu, 'table'):
                    table_x = x0 + hskip + x_icon
                    table_text = text.split('\t')
                    for i in range(len(menu.table)):
                        table_w = ((width-icon_x-len(table_text)*5)*menu.table[i]) / 100
                        if i != len(menu.table) - 1:
                            table_w += 5
                        x_mod = 0
                        if table_text[i].find('ICON_') == 0:
                            toi = self.text_or_icon(table_text[i], table_x, table_w, val.font)
                            x_mod, table_text[i] = toi
                            if not isstring(table_text[i]):
                                i = self.drawimage(table_text[i],
                                                   (table_x + x_mod, y0 + vskip))
                                gui_objects.append(i)
                                table_text[i] = ''
                                
                        if table_text[i]:
                            s = self.drawstring(table_text[i], val.font, content,
                                                x=table_x + x_mod,
                                                y=y0 + vskip, width=table_w, height=-1,
                                                align_h=val.align, mode='hard', dim=False)
                            gui_objects.append(s)
                        table_x += table_w + 5

                else:
                    #
                    # draw the text
                    #
                    s = self.drawstring(text, val.font, content, x=x0 + hskip + x_icon,
                                        y=y0 + vskip, width=width-icon_x, height=-1,
                                        align_h=val.align, mode='hard', dim=True)
                    gui_objects.append(s)


            #
            # image listing --------------------------------------------------------
            #
            if draw_this_item and content.type == 'image' or content.type == 'image+text':
                rec_h = val.height
                if content.type == 'image+text':
                    rec_h += int(1.1 * val.font.height)

                if val.align == 'center':
                    x0 = item_x0 + (hspace - val.width) / 2
                else:
                    x0 = item_x0 + hskip

                if val.valign == 'center':
                    y0 = item_y0 + (vspace - rec_h) / 2
                else:
                    y0 = item_y0 + vskip

                if val.rectangle:
                    if content.type == 'image+text':
                        r = self.get_item_rectangle(val.rectangle, val.width,
                                                    max(rec_h, int(val.font.height * 1.1)))[2]
                    else:
                        r = self.get_item_rectangle(val.rectangle, val.width, rec_h)[2]
                    b = self.drawbox(x0 + r.x, y0 + r.y, r.width, r.height, r)
                    gui_objects.append(b)

                image = self.imagelib.item_image(choice, (val.width, val.height),
                                                 settings.icon_dir, force=True)
                if image:
                    i_w, i_h = image.width, image.height

                    addx = 0
                    addy = 0
                    if val.align == 'center' and i_w < val.width:
                        addx = (val.width - i_w) / 2

                    if val.align == 'right' and i_w < val.width:
                        addx = val.width - i_w
            
                    if val.valign == 'center' and i_h < val.height:
                        addy = (val.height - i_h) / 2
                        
                    if val.valign == 'bottom' and i_h < val.height:
                        addy = val.height - i_h

                    i = ItemImage(image, (x0 + addx, y0 + addy), val.shadow)
                    self.layer.add_child(i)
                    gui_objects.append(i)
                        
                if content.type == 'image+text':
                    s = self.drawstring(choice.name, val.font, content, x=x0,
                                        y=y0 + val.height, width=val.width, height=-1,
                                        align_h=val.align, mode='hard',
                                        ellipses='', dim=False)
                    gui_objects.append(s)
                    


            #
            # calculate next item position ----------------------------------------
            #
            if current_col == cols:
                if content.align == 'center':
                    item_x0 = content.x + (content.width - cols * hspace) / 2
                else:
                    item_x0 = content.x
                item_y0 += vspace
                current_col = 1
            else:
                item_x0 += hspace
                current_col += 1


        # remember last selection
        self.last_selection = menu.selected

        if redraw:
            # draw the arrows
            try:
                if start > 0 and area.images['uparrow']:
                    self.arrows.append(self.drawimage(area.images['uparrow'].filename,
                                                      area.images['uparrow']))
                if end < len(menu.choices):
                    if isinstance(area.images['downarrow'].y, str):
                        v = copy.copy(area.images['downarrow'])
                        v.y = eval(v.y, {'MAX':(item_y0-vskip)})
                    else:
                        v = area.images['downarrow']
                    self.arrows.append(self.drawimage(area.images['downarrow'].filename, v))
            except Exception, e:
                _debug_(e, 0)
          
