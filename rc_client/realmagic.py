# Model: remote control for the Sigma Designs REALmagic Hollywood Plus DVD card


# Translation lirc -> freevo

RC_CMDS = {
    'QUIT'        : 'EXIT',
    'OSD'         : 'DISPLAY',
    'REV'         : 'REW',
    'FF'          : 'FFWD'
    }


# commands for mplayer
#
# for a list of possible mplayer commands read input/input.c from the
# mplayer source tree -- don't believe the manual ;-)

RC_MPLAYER_CMDS = {
    # lirc comand : ( 'mplayer slave command', 'description')
    'SUB'         : ( 'sub_visibility', 'Toggle subtitle visibility' )
    }
