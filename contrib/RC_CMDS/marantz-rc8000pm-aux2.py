## 2003-01-10
## Hi all,
##
## Here is a remote control key definition for using Freevo with a Marantz
## RC8000PM remote control, as device AUX2. There are not enough keys on
## that remote for all of Freevo's functions, so I discarded the number
## keys and use those keys as arrows (i.e. 8 = up, 2 = down, 6 = right,
## 4 = left, and 5 = SELECT).
##
## If this can help anybody...
##
## Matthieu
##
## --
## (~._.~)    Matthieu Weber - Université de Jyväskylä               (~._.~)
##  ( ? )               email : mweber@mit.jyu.fi                     ( ? )
## ()- -()              public key id : 452AE0AD                     ()- -()
## (_)-(_) "Humor ist, wenn man trotzdem lacht (Germain Muller)"     (_)-(_)

RC_CMDS = {
#    'sleep'       : 'SLEEP',
    'MODE'        : 'MENU',
#    'prog_guide'  : 'GUIDE',
    'MEMO'        : 'EXIT',
    '2'           : 'UP',
    '8'           : 'DOWN',
    '4'           : 'LEFT',
    '6'           : 'RIGHT',
    '5'           : 'SELECT',
    'SOURCE_ON/OFF' : 'POWER',
    'TIME'        : 'MUTE',
    'A.F/P'       : 'VOL+',
    'B.-/--'      : 'VOL-',
    '+'           : 'CH+',
    '-'           : 'CH-',
#    '1'           : '1',
#    '2'           : '2',
#    '3'           : '3',
#    '4'           : '4',
#    '5'           : '5',
#    '6'           : '6',
#    '7'           : '7',
#    '8'           : '8',
#    '9'           : '9',
#    '0'           : '0',
    'TEXT'        : 'DISPLAY',
#    ''            : 'ENTER',
    'prev_ch'     : 'PREV_CH',
    'pip_onoff'   : 'PIP_ONOFF',
    'pip_swap'    : 'PIP_SWAP',
    'pip_move'    : 'PIP_MOVE',
    'tv_vcr'      : 'EJECT',
    '<<'          : 'REW',
    '>'           : 'PLAY',
    '>>'          : 'FFWD',
    '||'          : 'PAUSE',
    '[]'          : 'STOP',
    'rec'         : 'REC',
    'OPEN/CLOSE'  : 'EJECT',
    'subtitle'    : 'SUBTITLE'
    }
