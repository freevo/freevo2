#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Perhaps we should move the filetype specific stuff (like the one for vob)
# into the config files...
#
# i.e.
#
# MP_CUSTOM = {
#     '.vob' = '-ac hwac3 ...',
#     '.rm'  = '-forceidx',
#     ...
#     }
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.26  2003/09/23 13:47:48  outlyer
# Remove this for now...
#
# Revision 1.25  2003/09/23 13:39:51  outlyer
# Remove more informational chatter.
#
# Revision 1.24  2003/09/20 17:03:20  dischi
# draw status while connecting and caching for network files
#
# Revision 1.23  2003/09/19 22:09:15  dischi
# use new childapp thread function
#
# Revision 1.22  2003/09/18 17:09:54  gsbarbieri
# Faster version detection + handle for CVS versions.
#
# Revision 1.21  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.20  2003/09/03 17:54:38  dischi
# Put logfiles into LOGDIR not $FREEVO_STARTDIR because this variable
# doesn't exist anymore.
#
# Revision 1.19  2003/09/02 19:10:22  dischi
# Basic mplayer version detection. Convert -vop to -vf if cvs or 1.0pre1
# is used
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
# ----------------------------------------------------------------------- */
#endif


import time, os
import threading, signal
import traceback, popen2

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

from event import *
import plugin

# RegExp
import re

import osd
osd = osd.get_singleton()

# contains an initialized MPlayer() object
mplayer = None

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the video player.

    With this plugin Freevo can play all video files defined in
    SUFFIX_VIDEO_FILES. This is the default video player for Freevo.
    """
    def __init__(self):
        global mplayer

        mplayer_version = 0
        # create the mplayer object
        plugin.Plugin.__init__(self)

        child = popen2.Popen3( "%s -v" % config.MPLAYER_CMD, 1, 100)
        data = child.fromchild.readline() # Just need the first line
        if data:
            data = re.search( "^MPlayer (?P<version>\S+)", data )
            if data:                
                _debug_("MPlayer version is: %s" % data.group( "version" ),2)
                data = data.group( "version" )
                if data[ 0 ] == "1":
                    mplayer_version = 1.0
                elif data[ 0 ] == "0":
                    mplayer_version = 0.9
                elif data[ 0 : 7 ] == "dev-CVS":
                    mplayer_version = 9999
                _debug_("MPlayer version set to: %s" % mplayer_version,2)
                    
        child.wait()
        mplayer = util.SynchronizedObject(MPlayer(mplayer_version))

        # register it as the object to play audio
        plugin.register(mplayer, plugin.VIDEO_PLAYER)


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self, version):
        self.thread = childapp.ChildThread()
        self.thread.stop_osd = True

        self.mode = None
        self.filename = None
        self.app_mode = 'video'
        self.version = version
        self.seek = 0
        self.seek_timer = threading.Timer(0, self.reset_seek)

        
    def play(self, filename, options, item, mode = None):
        """
        play a videoitem with mplayer
        """

        self.parameter = (filename, options, item, mode)
        
        if not mode:
            mode = item.mode

        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0
           
        self.filename = filename

        self.mode = mode   # setting global var to mode.

        _debug_('MPlayer.play(): mode=%s, filename=%s' % (mode, filename),2)

        if mode == 'file' and not os.path.isfile(filename) and not network_play:
            # This event allows the videoitem which contains subitems to
            # try to play the next subitem
            return '%s\nnot found' % os.path.basename(filename)
       

        # Build the MPlayer command
        mpl = '--prio=%s %s %s -slave -ao %s' % (config.MPLAYER_NICE,
                                                 config.MPLAYER_CMD,
                                                 config.MPLAYER_ARGS_DEF,
                                                 config.MPLAYER_AO_DEV)

        additional_args = ''

        if mode == 'file':
            try:
                mode = os.path.splitext(filename)[1]
            except:
                pass

        elif mode == 'vcd':
            # Filename is VCD title
            filename = 'vcd://%s' % filename  

        elif mode == 'dvd':
            # Filename is DVD title
            filename = 'dvd://%s' % filename  

            if config.DVD_LANG_PREF:
                # There are some bad mastered DVDs out there. E.g. the specials on
                # the German Babylon 5 Season 2 disc claim they have more than one
                # audio track, even more then on en. But only the second en works,
                # mplayer needs to be started without -alang to find the track
                if hasattr(item, 'mplayer_audio_broken') and item.mplayer_audio_broken:
                    print '*** dvd audio broken, try without alang ***'
                else:
                    additional_args = '-alang %s' % config.DVD_LANG_PREF

            if config.DVD_SUBTITLE_PREF:
                # Only use if defined since it will always turn on subtitles
                # if defined
                additional_args += ' -slang %s' % config.DVD_SUBTITLE_PREF

        else:
            print "Don't know what do play!"
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            return 'Unknown media: %s' % os.path.basename(filename)

        if not config.MPLAYER_ARGS.has_key(mode):
            mode = 'default'

        # Mplayer command and standard arguments
        mpl += (' ' + config.MPLAYER_ARGS[mode] + ' ' + additional_args + \
                ' -v -vo ' + config.MPLAYER_VO_DEV + config.MPLAYER_VO_DEV_OPTS)

        if options:
            mpl += (' ' + options)

        # use software scaler?
        if mpl.find(' -nosws ') > 0:
            mpl = (mpl[:mpl.find(' -nosws ')] + mpl[mpl.find(' -nosws ')+7:])
        elif mpl.find(' -framedrop ') == -1 and mpl.find(' -framedrop ') == -1:
            mpl += (' ' + config.MPLAYER_SOFTWARE_SCALER )
            
        command = mpl + ' "' + filename + '"'

        if config.MPLAYER_AUTOCROP and command.find('crop=') == -1:
            (x1, y1, x2, y2) = (1000, 1000, 0, 0)
            child = popen2.Popen3(self.vop_append('%s -ao null -vo null ' \
                                                  '-ss 60 -frames 20 -vop cropdetect' % \
                                                  command), 1, 100)
            exp = re.compile('^.*-vop crop=([0-9]*):([0-9]*):([0-9]*):([0-9]*).*')
            while(1):
                data = child.fromchild.readline()
                if not data:
                    break
                m = exp.match(data)
                if m:
                    x1 = min(x1, int(m.group(3)))
                    y1 = min(y1, int(m.group(4)))
                    x2 = max(x2, int(m.group(1)) + int(m.group(3)))
                    y2 = max(y2, int(m.group(2)) + int(m.group(4)))

            if x1 < 1000 and x2 < 1000:
                command = '%s -vop crop=%s:%s:%s:%s' % (command, x2-x1, y2-y1, x1, y1)
            
            child.wait()


        command=self.vop_append(command)

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.file = item

        self.thread.start(MPlayerApp, (command, item, network_play))

        self.item  = item

        _debug_('MPlayer.play(): Starting thread, cmd=%s' % command,2)
        rc.app(self)

        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.stop('quit\n')
        rc.app(None)



    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if event == VIDEO_MANUAL_SEEK:
            self.seek = 0
            rc.set_context('input')
            return True
        
        if event.context == 'input':
            if event in INPUT_ALL_NUMBERS:
                self.reset_seek_timeout()
                self.seek = self.seek * 10 + int(event);
                return True
            
            elif event == INPUT_ENTER:
                self.seek_timer.cancel()
                self.seek *= 60
                self.thread.app.write('seek ' + str(self.seek) + ' 2\n')
                _debug_("seek "+str(self.seek)+" 2\n")
                self.seek = 0
                rc.set_context('video')
                return True

            elif event == INPUT_EXIT:
                _debug_('seek stopped')
                self.seek_timer.cancel()
                self.seek = 0
                rc.set_context('video')
                return True

        if event == STOP:
            self.stop()
            return self.item.eventhandler(event)

        if event == 'AUDIO_ERROR_START_AGAIN':
            self.stop()
            self.play(self.parameter[0], self.parameter[1], self.parameter[2],
                      self.parameter[3])
            return True
        
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        try:
            if event == VIDEO_SEND_MPLAYER_CMD:
                self.thread.app.write('%s\n' % event.arg)
                return True

            if event == TOGGLE_OSD:
                self.thread.app.write('osd\n')
                return True

            if event == PAUSE or event == PLAY:
                self.thread.app.write('pause\n')
                return True

            if event == SEEK:
                self.thread.app.write('seek %s\n' % event.arg)
                return True
        except:
            print 'Exception while sending command to mplayer:'
            traceback.print_exc()
            return True
        
        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)

    
    def reset_seek(self):
        _debug_('seek timeout')
        self.seek = 0
        rc.set_context('video')
        
    def reset_seek_timeout(self):
        self.seek_timer.cancel()
        self.seek_timer = threading.Timer(config.MPLAYER_SEEK_TIMEOUT, self.reset_seek)
        self.seek_timer.start()
        
    def vop_append(self, command):
        """
        Change a mplayer command to support more than one -vop
        parameter. This function will grep all -vop parameter from
        the command and add it at the end as one vop argument
        """
        ret = ''
        vop = ''
        next_is_vop = False
    
        for arg in command.split(' '):
            if next_is_vop:
                vop += ',%s' % arg
                next_is_vop = False
            elif (arg == '-vop' or arg == '-vf'):
                next_is_vop=True
            else:
                ret += '%s ' % arg

        if vop:
            if self.version >= 1:
                return '%s -vf %s' % (ret,vop[1:])
            return '%s -vop %s' % (ret,vop[1:])
        return ret



# ======================================================================

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, (app, item, network_play)):
        if config.MPLAYER_DEBUG:
            fname_out = os.path.join(config.LOGDIR, 'mplayer_stdout.log')
            fname_err = os.path.join(config.LOGDIR, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'w')
                self.log_stderr = open(fname_err, 'w')
                print 'MPlayer logging to "%s" and "%s"' % (fname_out, fname_err)
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'MPlayer logging!') % (fname_out, fname_err))
                config.MPLAYER_DEBUG = 0
                
        # DVD items also store mplayer_audio_broken to check if you can
        # start them with -alang or not
        if hasattr(item, 'mplayer_audio_broken') or item.mode != 'dvd':
            self.check_audio = 0
        else:
            self.check_audio = 1

        self.network_play = network_play
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
        self.RE_START = re.compile("^Starting playback\.\.\.").match
        self.RE_EXIT = re.compile("^Exiting\.\.\. \((.*)\)$").match
        self.item = item
        childapp.ChildApp.__init__(self, app)
        self.exit_type = None
        self.osdfont = osd.getfont(config.OSD_DEFAULT_FONTNAME, config.OSD_DEFAULT_FONTSIZE)
                
        
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)
        _debug_('Killing mplayer')

        if config.MPLAYER_DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()


    def stopped(self):
        if self.exit_type == "End of file":
            rc.post_event(PLAY_END)
        elif self.exit_type == "Quit":
            rc.post_event(USER_END)
        else:
            print 'error while playing file'
            rc.post_event(PLAY_END)
                        

    def stdout_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stdout.write(line + '\n')
            except ValueError:
                pass # File closed

        if self.network_play:
            if line.find('Opening audio decoder') == 0:
                osd.clearscreen(osd.COL_BLACK)
                osd.update()
            elif (line.find('Resolving ') == 0 or line.find('Connecting to server') == 0 or \
                  line.find('Cache fill:') == 0) and \
                  line.find('Resolving reference to') == -1:
                if line.find('Connecting to server') == 0:
                    line = 'Connecting to server'
                osd.clearscreen(osd.COL_BLACK)
                osd.drawstringframed(line, config.OVERSCAN_X, config.OVERSCAN_Y,
                                     osd.width - 2 * config.OVERSCAN_X, -1, self.osdfont,
                                     osd.COL_WHITE)
                osd.update()
                
        if line.find("A:") == 0:
            m = self.RE_TIME(line) # Convert decimal
            if hasattr(m,'group'):
                self.item.elapsed = int(m.group(1))+1

        elif line.find("Exiting...") == 0:
            m = self.RE_EXIT(line)
            if m:
                self.exit_type = m.group(1)

        # this is the first start of the movie, parse infos
        elif not self.item.elapsed:
            if self.check_audio:
                if line.find('MPEG: No audio stream found -> no sound') == 0:
                    # OK, audio is broken, restart without -alang
                    self.check_audio = 2
                    self.item.mplayer_audio_broken = True
                    rc.post_event(Event('AUDIO_ERROR_START_AGAIN'))
                
                if self.RE_START(line):
                    if self.check_audio == 1:
                        # audio seems to be ok
                        self.item.mplayer_audio_broken = False
                    self.check_audio = 0


    def stderr_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stderr.write(line + '\n')
            except ValueError:
                pass # File closed
