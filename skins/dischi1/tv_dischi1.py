
import sys, socket, random, time, os, copy, re
import config

from utils_dischi1 import *

# The OSD class, used to communicate with the OSD daemon
import osd

# Create the OSD object
osd = osd.get_singleton()


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

class Skin_TV:

    tvguide_expand = 0

    def DrawTVGuide(self, settings):
        self.DrawTVGuide_Clear(settings)


    def DrawTVGuide_Clear(self, settings):
        osd.clearscreen(osd.COL_BLACK)

        if settings.background.image:
            apply(osd.drawbitmap, (settings.background.image, -1, -1))

        if settings.background.mask:
            osd.drawbitmap(settings.background.mask,-1,-1)

        DrawLogo(settings.logo)

        # Show title and date
        s = time.strftime('%m/%d %H:%M')
        DrawTextFramed('TV Guide  -  %s' % s, settings.header)


    def DrawTVGuide_getExpand(self, settings):
        return self.tvguide_expand

    def DrawTVGuide_setExpand(self, expand, settings):
        self.tvguide_expand = expand

    def DrawTVGuide_View(self, to_view, settings):
        val = settings.view
        osd.drawbox(val.x, val.y, val.x+val.width, val.y+val.height,
                    color=val.bgcolor, width=-1)
        DrawTextFramed(to_view, val, x=val.x, y=val.y, width=val.width,
                       height=val.height)



    def DrawTVGuide_Info(self, to_info, settings):
        val = settings.info
        osd.drawbox(val.x, val.y, val.x+val.width, val.y+val.height,
                    color=val.bgcolor, width=-1)
        DrawTextFramed(to_info, val, x=val.x, y=val.y, width=val.width,
                       height=val.height)



    def DrawTVGuide_ItemsPerPage(self, settings):
        items = -1
        val = settings.listing 

        str_w_head, str_h_head = osd.stringsize('Ajg', val.head.font, val.head.size)
        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        str_h = max (str_h_head, str_h_selection, str_h_normal )

        if self.DrawTVGuide_getExpand(settings) == 0:
            height = val.height - str_h_head - 2 * val.spacing
        else:
            height = val.expand.height - str_h_head - 2 * val.spacing

        items = height / ( str_h + 2 * val.spacing )

        return int(items)



    def DrawTVGuide_Listing(self, to_listing, settings):
        val = settings.listing 

        if self.DrawTVGuide_getExpand(settings) == 0:
            conf_x = val.x
            conf_y = val.y
            conf_w = val.width
            conf_h = val.height
        else:
            conf_x = val.expand.x
            conf_y = val.expand.y
            conf_w = val.expand.width
            conf_h = val.expand.height


        str_w_head = str_h_head = 0
        str_w_selection = str_h_selection = 0
        str_w_normal = str_h_normal = 0
        val.left_arrow_size = val.right_arrow_size = (0, 0)
        n_cols = len(to_listing[0])-1
        col_time = 30

        str_w_head, str_h_head = osd.stringsize('Ajg', val.head.font, val.head.size)
        str_w_selection, str_h_selection = \
                         osd.stringsize('Ajg', val.selection.font, val.selection.size)
        str_w_normal, str_h_normal = osd.stringsize('Ajg', val.font, val.size)

        left_arrow_size = osd.bitmapsize(val.left_arrow)
        right_arrow_size = osd.bitmapsize(val.right_arrow)


        y_contents = conf_y + str_h_head + 2 * val.spacing
        h_contents = conf_h - str_h_head - 2 * val.spacing
        x_contents = conf_x + val.channel_width
        w_contents = conf_w - val.channel_width

        col_size = int( w_contents / n_cols )
        occupied_height = 0


        # Display the Time on top
        x = conf_x
        y = conf_y
        # Display the Channel on top
        osd.drawbox(x, y, x+val.channel_width, y+str_h_head + 2 * val.spacing,
                    width=-1, color=val.head.bgcolor)
        osd.drawbox(x, y, x+val.channel_width, y+str_h_head + 2 * val.spacing,
                    width=1, color=val.border_color)
        DrawTextFramed(time.strftime("%m/%d",time.localtime(to_listing[0][1])), \
                       val.head, x + val.spacing, y + val.spacing, \
                       val.channel_width - 2 * val.spacing, str_h_head)


        x = x_contents
        head2 = copy.copy(val.head)
        head2.align='left'
        for i in range(n_cols):
            osd.drawbox(x, y, x+col_size, y+ str_h_head + 2 * val.spacing,
                        width=-1, color=val.head.bgcolor)   
            osd.drawbox(x, y, x+col_size, y+ str_h_head + 2 * val.spacing,
                        width=1, color=val.border_color)   
            DrawTextFramed(time.strftime("%H:%M",time.localtime(to_listing[0][i+1])),
                                head2,
                                x + val.spacing, y + val.spacing,
                                col_size - 2 * val.spacing, str_h_head)

            x += col_size

        # define start and stop time
        date = time.strftime("%x", time.localtime())
        start_time = to_listing[0][1]
        stop_time = to_listing[0][len(to_listing[0])-1]
        stop_time += (col_time*60)

        str_h = max( str_h_head, str_h_selection, str_h_normal )

        # 1 sec = x pixels
        prop_1sec = float(w_contents) / float(n_cols * col_time * 60) 

        # selected program:
        selected_prog = to_listing[1]

        y = y_contents
        h = str_h
        for i in range(2,len(to_listing)):
            if occupied_height <= h_contents:
                # draw the channel name/logo/id
                osd.drawbox(conf_x, y, conf_x+val.channel_width, y+str_h + 2 * val.spacing,
                            width=-1, color=val.head.bgcolor)
                osd.drawbox(conf_x, y, conf_x+val.channel_width, y+str_h + 2 * val.spacing,
                            width=1, color=val.border_color)
                # Logo
                channel_logo = config.TV_LOGOS + '/' + to_listing[i].id + '.png'
                if not os.path.isfile(channel_logo):
                    #if DEBUG: print 'skin: Cannot find logo "%s"' % channel_logo
                    channel_logo = None

                padding = 0
                if channel_logo:
                    channel_logo_size = osd.bitmapsize(channel_logo)
                    # XXX The logo was stretched vertically with the old code. /Krister
                    padding = channel_logo_size[0]
                    osd.drawbitmap(util.resize(channel_logo, padding, padding),
                                   conf_x + val.spacing, y + val.spacing + \
                                   (str_h - padding)/2)

                DrawTextFramed(to_listing[i].displayname, val.head,
                               conf_x + val.spacing + padding, y + val.spacing,
                               val.channel_width - 2 * val.spacing - padding, str_h)




                if to_listing[i].programs:
                    for prg in to_listing[i].programs:
                        val2 = copy.copy(val)
                        val2.selection = copy.copy(val.selection)

                        str = ''
                        x = 0
                        w = 0
                        flag_left = 0
                        flag_right = 0
                        if prg.start < start_time:
                            flag_left = 1
                            x = x_contents
                            t_start = start_time
                        else:
                            x = x_contents + int( float(prg.start - start_time) * \
                                                  prop_1sec )
                            t_start = prg.start

                        str += prg.title

                        if prg.stop > stop_time:
                            flag_right = 1
                            w = w_contents + x_contents - x                        
                        else:
                            w = int( (prg.stop - t_start) * prop_1sec )

                        if prg.title == 'This channel has no data loaded':
                            val2.align='center'
                            val2.selection.align='center'


                        if prg.title == selected_prog.title and \
                           prg.channel_id == selected_prog.channel_id and \
                           prg.start == selected_prog.start and \
                           prg.stop == selected_prog.stop:

                            osd.drawbox(x, y, x+w, y+h + 2 * val2.spacing,
                                        width=-1, color=val2.selection.bgcolor)
                            osd.drawbox(x, y, x+w, y+h + 2 * val2.spacing,
                                        width=1, color=val2.border_color)
                            DrawTextFramed(str, val2.selection,
                                           x+val2.spacing + flag_left * \
                                           left_arrow_size[0],
                                           y+val2.spacing,
                                           w - 2 * val2.spacing - flag_left * \
                                           left_arrow_size[0] - flag_right * \
                                           right_arrow_size[0], h)
                        else:
                            osd.drawbox(x, y, x+w, y+h + 2 * val2.spacing,
                                        width=-1, color=val2.bgcolor)
                            osd.drawbox(x, y, x+w, y+h + 2 * val2.spacing,
                                        width=1, color=val2.border_color)
                            DrawTextFramed(str, val2,
                                           x+val2.spacing + flag_left * \
                                           left_arrow_size[0], y+val2.spacing,
                                           w - 2 * val2.spacing - flag_left * \
                                           left_arrow_size[0] - flag_right * \
                                           right_arrow_size[0], h)


                        if flag_left == 1:
                            osd.drawbitmap(val2.left_arrow, x, \
                                           y+int((str_h - left_arrow_size[1])/2.0))
                        if flag_right == 1:
                            osd.drawbitmap(val2.right_arrow, \
                                           x+w-right_arrow_size[0], \
                                           y+int((str_h - right_arrow_size[1])/2.0))
                else:
                    osd.drawbox(x_contents, y, x_contents+w_contents, \
                                y+h + 2 * val2.spacing,
                                width=-1, color=val2.bgcolor)
                    osd.drawbox(x_contents, y, x_contents+w_contents, \
                                y+h + 2 * val2.spacing,
                                width=1, color=val2.border_color)

                    DrawTextFramed('-[ NO DATA ]-', val, x_contents+val2.spacing,
                                   y+val2.spacing,
                                   w_contents - 2 * val2.spacing, h)

                occupied_height += str_h + 2 * val2.spacing
                y += str_h + 2 * val2.spacing
            else:
                break


        # draw a border around the contents
        if val.border_size > 0:
            osd.drawbox(conf_x, conf_y, conf_x +conf_w, conf_y + conf_h,
                        width=val.border_size, color=val.border_color)

