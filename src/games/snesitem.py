#if 0 /*
# -----------------------------------------------------------------------
# snesitem.py - Item for snes objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.14  2004/01/10 21:25:01  mikeruelle
# zipped rom support for snes and genesis
#
# Revision 1.13  2003/12/29 22:30:35  dischi
# move to new Item attributes
#
# Revision 1.12  2003/12/03 17:25:05  mikeruelle
# they seem to have lost a patch i put in.
#
# Revision 1.11  2003/09/11 17:38:59  mikeruelle
# fix a snes crash
#
# Revision 1.10  2003/09/05 20:48:35  mikeruelle
# new game system
#
# Revision 1.9  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
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

import os

import config
import game

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import rc
import time
import copy

from item import Item
import event as em
from struct import *
from string import *
from re import *
from zipped_rom import unzip_rom

# Extensions used by SNES ROMs
snesromExtensions = ['smc', 'sfc', 'fig']

# Used to detect the internal rome information, as described in 'SNESKART.DOC v1.3'
snesromFileOffset = [33216, 32704, 65472, 65984]
snesRomCountry    = { 0:'Japan', 1:'USA', 2:'Europe, Oceania, Asia', 3:'Sweden', 4:'Finland', 5:'Denmark',
                  6:'France', 7:'Holland', 8:'Spain', 9:'Germany, Austria, Switz', 10:'Italy',
                  11:'Hong Kong, China', 12:'Indonesia', 13:'Korea', 255:'International' }
snesromType     = [ 0, 1, 2, 3, 4, 5, 19, 227, 246]
snesromROMSize  = [ 8, 9, 10, 11, 12]
snesromSRAMSize = [ 0, 1, 2, 3]
snesromLicences = {  0: 'Unknown',
		1: 'Nintendo'                               ,
		5: 'Zamuse'                                 ,
		8: 'Capcom'                                 ,
		9: 'HOT B'                                  ,
		10: 'Jaleco'                                 ,
		11: 'STORM'                                  ,
		15: 'Mebio Software'                         ,
		18: 'Gremlin Graphics'                       ,
		21: 'COBRA Team'                             ,
		22: 'Human/Field'                            ,
		24: 'Hudson Soft'                            ,
		26: 'Yanoman'                                ,
		28: 'Tecmo'                              ,
		30: 'Forum'                                  ,
		31: 'Park Place Productions / VIRGIN'        ,
		33: 'Tokai Engeneering'           ,
		34: 'POW'                                    ,
		35: 'Loriciel / Micro World'                 ,
		38: 'Enix'                                   ,
		40: 'Kemco (1)'                              ,
		41: 'Seta Co.,Ltd.'                          ,
		45: 'Visit Co.,Ltd.'                         ,
		51: 'Nintendo'                        ,
		53: 'HECT'                                   ,
		61: 'Loriciel'                               ,
		64: 'Seika Corp.'                            ,
		65: 'UBI Soft'                               ,
		71: 'Spectrum Holobyte'                      ,
		73: 'Irem'                                   ,
		75: 'Raya Systems/Sculptured Software'       ,
		76: 'Renovation Pruducts'                    ,
		77: 'Malibu Games' ,
		79: 'U.S. Gold'                             ,
		80: 'Absolute Entertainment'                ,
		81: 'Acclaim'                               ,
		82: 'Activision'                            ,
		83: 'American Sammy'                        ,
		84: 'GameTek'                               ,
		85: 'Hi Tech'                               ,
		86: 'LJN Toys'                              ,
		90: 'Mindscape'                             ,
		93: 'Technos Japan Corp. (Tradewest)'       ,
		95: 'American Softworks Corp.'              ,
		96: 'Titus'                                 ,
		97: 'Virgin Games'                          ,
		98: 'Maxis'                                 ,
		103: 'Ocean'                                 ,
		105: 'Electronic Arts'                       ,
		107: 'Laser Beam'                            ,
		110: 'Elite'                                 ,
		111: 'Electro Brain'                         ,
		112: 'Infogrames'                            ,
		113: 'Interplay'                             ,
		114: 'LucasArts'                             ,
		115: 'Sculptured Soft'                       ,
		117: 'STORM (Sales Curve)'               ,
		120: 'THQ Software'                          ,
		121: 'Accolade Inc.'                         ,
		122: 'Triffix Entertainment'                 ,
		124: 'Microprose'                            ,
		127: 'Kemco'                             ,
		129: 'Teichio'                           ,
		130: 'Namcot/Namco Ltd.'                 ,
		132: 'Koei/Koei!'          ,
		134: 'Tokuma Shoten Intermedia'              ,
		136: 'DATAM-Polystar'                        ,
		139: 'Bullet-Proof Software'                 ,
		140: 'Vic Tokai'                             ,
		143: 'I Max'                                 ,
		145: 'CHUN Soft'                             ,
		146: 'Video System Co., Ltd.'                ,
		147: 'BEC'                                   ,
		151: 'Kaneco'                                ,
		153: 'Pack in Video'                         ,
		154: 'Nichibutsu'                            ,
		155: 'TECMO'                             ,
		156: 'Imagineer Co.'                         ,
		160: 'Wolf Team'                             ,
		164: 'Konami'                                ,
		165: 'K.Amusement'                           ,
		167: 'Takara'                                ,
		169: 'Technos Jap.'                     ,
		170: 'JVC'                                   ,
		172: 'Toei Animation'                        ,
		173: 'Toho'                                  ,
		175: 'Namcot/Namco Ltd.'                 ,
		177: 'ASCII Co. Activison'                   ,
		178: 'BanDai America'                        ,
		180: 'Enix'                                  ,
		182: 'Halken'                                ,
		186: 'Culture Brain'                         ,
		187: 'Sunsoft'                               ,
		188: 'Toshiba EMI/System Vision'             ,
		189: 'Sony (Japan) / Imagesoft'              ,
		191: 'Sammy'                                 ,
		192: 'Taito'                                 ,
		194: 'Kemco'                        ,
		195: 'Square'                                ,
		196: 'NHK'                                   ,
		197: 'Data East'                             ,
		198: 'Tonkin House'                          ,
		200: 'KOEI'                                  ,
		202: 'Konami USA'                            ,
		205: 'Meldac/KAZe'                           ,
		206: 'PONY CANYON'                           ,
		207: 'Sotsu Agency'                          ,
		209: 'Sofel'                                 ,
		210: 'Quest Corp.'                           ,
		211: 'Sigma'                                 ,
		214: 'Naxat'                                 ,
		216: 'Capcom'                  ,
		217: 'Banpresto'                             ,
		219: 'Hiro'                                  ,
		221: 'NCS'                                   ,
		222: 'Human Entertainment'                   ,
		223: 'Ringler Studios'                       ,
		224: 'K.K. DCE / Jaleco'                     ,
		226: 'Sotsu Agency'                          ,
		228: 'T&ESoft'                               ,
		229: 'EPOCH Co.,Ltd.'                        ,
		231: 'Athena'                                ,
		232: 'Asmik'                                 ,
		233: 'Natsume'                               ,
		234: 'King/A Wave'                           ,
		235: 'Atlus'                                 ,
		236: 'Sony Music'                            ,
		238: 'Psygnosis / igs'                       ,
		243: 'Beam Software'                         ,
		244: 'Tec Magik'                             ,
		255: 'Hudson Soft'                           }

class SnesItem(Item):
    def __init__(self, file, cmd = None, args = None, imgpath = None, parent = None):
        Item.__init__(self)
        self.type  = 'snes'            # fix value
        self.mode  = 'file'            # file, dvd or vcd
        self.filename = file
        
        snesFile = None
        unzipped = unzip_rom(file, snesromExtensions)
        if unzipped:
            snesFile = open(unzipped, 'rb')
        else:
            snesFile = open(file, 'rb')

        for offset in snesromFileOffset:
            snesFile.seek(offset)
            romHeader = snesFile.read(32)
            (romName,romHL,romMem,romROM,romSRAM,romCountry,romLic,romVer,romICHK,romCHK) = unpack('21scccccccHH', romHeader)
            # Break now if CHECKSUM is OK
            if (romICHK | romCHK) == 0xFFFF:
                if DEBUG:
                    print 'SNES rom header detected at offset : %d!!!!' % offset
                break
        else:
            for offset in snesromFileOffset:
                snesFile.seek(offset)
                romHeader = snesFile.read(32)
                (romName,romHL,romMem,romROM,romSRAM,romCountry,romLic,romVer,romICHK,romCHK) = unpack('21scccccccHH', romHeader)
                # Some times, the ROM is OK, but the checksum is incorrect, so we do a very dummy ASCII detection
                if match('[a-zA-Z0-9 ]{4}', romName[0:4]) != None:
                    if DEBUG:
                        print 'SNES rom header detected by ASCII name : %d!!!!' % offset
                    break
        snesFile.close()
        if unzipped:
            os.unlink(unzipped)

        if DEBUG:
            print 'SNES rom name : %s - %s -> %s' % (ord(romCountry),os.path.basename(file), romName)

        # Allocate the name according to the country by checking the rom name againts ASCII codes
        if snesromLicences.has_key(ord(romLic)):
            romLicTxt = snesromLicences[ord(romLic)]
        else:
            romLicTxt = 'Unknown'
        if snesRomCountry.has_key(ord(romCountry)):
            romCountryTxt = snesRomCountry[ord(romCountry)]
        else:
            romCountryTxt = 'Unknown'
        if match('[a-zA-Z0-9 ]{4}', romName[0:4]) == None:
            self.name = os.path.splitext(os.path.basename(file))[0]  + ' (' + romCountryTxt + ' - ' + romLicTxt + ')'
        else:
            self.name = capwords(romName) + ' (' + romCountryTxt + ' - ' + romLicTxt + ')'
        self.parent = parent
        
        # find image for this file
        shot = imgpath + '/' + \
               os.path.splitext(os.path.basename(file))[0] + ".png"
        if os.path.isfile(shot):
            self.image = shot
        elif os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"

        command = '--prio=%s %s %s' % (config.GAMES_NICE,
                                       cmd,
                                       args)

        romname = os.path.basename(file)
        romdir = os.path.dirname(file)
        command = '%s "%s"' % (command, file)

        self.command = command

        self.game_player = game.get_singleton()
        

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        return self.name


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        return [ ( self.play, 'Play' ) ]
    

    def play(self, arg=None, menuw=None):
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        if self.menuw.visible:
            self.menuw.hide()

        print "Playing:  %s" % self.filename

        self.game_player.play(self, menuw)


    def stop(self, menuw=None):
        self.game_player.stop()


    def eventhandler(self, event, menuw=None, mythread=None):

        if not mythread == None:
            if event == em.STOP:
                self.stop()
                rc.app(None)
                if not menuw == None:
                    menuw.refresh(reload=1)

            elif event == em.MENU:
                mythread.app.write('M')

            elif event == em.GAMES_CONFIG:
                mythread.cmd( 'config' )

            elif event == em.PAUSE or event == em.PLAY:
                mythread.cmd('pause')

            elif event == em.GAMES_RESET:
                mythread.cmd('reset')

            elif event == em.GAMES_SNAPSHOT:
                mythread.cmd('snapshot')

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)

