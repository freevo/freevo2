from guide import EPGDB
from program import Program

guide = EPGDB()

connect = guide.connect
load    = guide.init

channels = guide.channel_list

