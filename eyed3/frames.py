#
#  Copyright (C) 2002  Travis Shirk <travis@pobox.com>
#  Copyright (C) 2001  Ryan Finne <ryan@finnie.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import re, zlib, StringIO;
from StringIO import StringIO;
import utils, binfuncs;
from utils import *;
from binfuncs import *;

ARTIST_FIDs  = ["TPE1", "TPE2", "TPE3", "TPE4", "TCOM"];
ALBUM_FID    = "TALB";
TITLE_FID    = "TIT2";
YEAR_FID     = "TYER";  # XXX: Deprecated in ID3 v2.4
COMMENT_FID  = "COMM";
GENRE_FID    = "TCON";
TRACKNUM_FID = "TRCK";
USERTEXT_FID = "TXXX";

NULL_FRAME_FLAGS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

#######################################################################
class Frame:
   header = None;

   dlied = 0;
   groupId = 0;

   def __repr__(self):
      return '<Frame.%s (%s)>' % (self.__class__.__name__, self.header.id);

   def unsynch(self, data):
      if self.header.unsync:
         subs = (0, 0);
         (data, subs[0]) = re.compile("\xff\x00").subn("\xff\x00\x00", data);
         (data, subs[1]) = re.compile("\xff(?=[\xe0-\xff])").subn("\xff\x00",
                                                                   data);

         TRACE_MSG("Unsynchronizing data: " + str(subs));
         if not subs[0] and not subs[1]:
            self.header.unsync = 0;
      return data;

   def deunsynch(self, data):
      if self.header.unsync:
         TRACE_MSG("Frame: [size before deunsynch]: " + str(len(data)));
         data = re.compile("\xff\x00([\xe0-\xff])").sub("\xff\\1", data);
         TRACE_MSG("Frame: [size after stage #1 deunsynch]: " +\
                    str(len(data)));
         data = re.compile("\xff\x00\x00").sub("\xff\x00", data);
         TRACE_MSG("Frame: [size after deunsynch: " + str(len(data)));
      return data;

   def read_group(self, data):
      if self.header.grouped:
         groupPos = len(data) - 1;
         self.groupId = data[groupPos];
         data = data[0:groupPos];
      return data;

   def write_group(self, data):
      if self.header.grouped:
         data += self.groupId;
         self.dlied = 1;
      return data;

   def decompress(self, data):
      if self.header.compressed:
         if self.header.dataLen:
            #TRACE_MSG("data len bit: " + str(self.header.dataLen));
            realData = len(data) - 4;
            data = data[0:realData];
            self.dlied = 1;
         data = zlib.decompress(data);
      return data;

   def compress(self, data):
      origSize = bin2bytes(bin2synchsafe(dec2bin(len(data), 32)));
      if self.header.compressed:
         self.dlied = 1;
         data = zlib.compress(data);

      if self.dlied == 1:
         self.header.dataLen = 1;
         data += origSize;
      return data;

   def assemble_frame(self, data):
      data = self.write_group(data);
      data = self.compress(data);
      #
      # TODO: Encryption goes here.
      #
      if self.header.unsync:
         data = self.unsynch(data);

      flags = bin2bytes(self.header.flags);
      framesize = bin2bytes(bin2synchsafe(dec2bin(len(data), 32)));

      return self.header.id + framesize + flags + data;

   def disassemble_frame(self, data):
      data = self.deunsynch(data);
      #
      # TODO: Decryption goes here.
      #
      data = self.decompress(data);
      data = self.read_group(data);
      # XXX - The original dataSize should be preserved so the tag can
      # advance to the next frame.
      #self.header.dataSize = len(data);
      return data;

#######################################################################
class TextInfo(Frame):
   encoding = '\x00';
   value = "";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      data = self.disassemble_frame(data);
      self.encoding = data[0];
      self.value = data[1:];

   def __repr__(self):
      return '<Frame.%s (%s): %s>' % (self.__class__.__name__, self.header.id,
                                      self.value)

   def render(self):
      data = self.encoding + self.value;
      return self.assemble_frame(data);

#######################################################################
class UserTextInfo(TextInfo):
   description = "";

   def __init__(self, frameHeader, data):
      frameHeader.id = "TXXX";
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      data = self.disassemble_frame(data);
      self.encoding = data[0];
      (self.description, self.value) = data[1:].split('\x00', 1);

   def render(self):
      data = self.encoding + self.description + '\x00' + self.value;
      return self.assemble_frame(data);

#######################################################################
class URL(Frame):
   url = "";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      data = self.disassemble_frame(data);
      self.url = data;

   def render(self):
      data = self.url;
      return self.assemble_frame(data);

#######################################################################
class UserURL(URL):
   description = "";
   encoding = "\x00";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      self.header.id = "WXXX";
      data = self.disassemble_frame(data);

      self.encoding = data[0];
      (self.description, self.url) = data[1:].split('\x00', 1);

   def render(self):
      data = self.encoding + self.description + '\x00' + self.url;
      return self.assemble_frame(data);

#######################################################################
class Comment(Frame):
   encoding = "\x00";
   lang = "";
   description = "";
   comment = "";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      self.header.id = "COMM";
      data = self.disassemble_frame(data);
      self.encoding = data[0];
      self.lang = data[1:4];
      (self.description, self.comment) = data[4:].split('\x00', 1);

   def __repr__(self):
      return '<Frame.%s (%s): %s [desc: %s] [lang: %s]>' %\
             (self.__class__.__name__, self.header.id, self.comment,
              self.description, self.lang);

   def render(self):
      data = self.encoding + self.lang + self.description + '\x00' +\
             self.comment;
      return self.assemble_frame(data);

#######################################################################
# This class refers to the APIC frame, otherwise known as an "attached picture".
class Image(Frame):
   encoding = "\x00";
   mimeType = None;
   pictureType = None;
   description = "";
   imageData = "";
   # Declared "picture types".
   OTHER               = 0x00;
   ICON                = 0x01; # 32x32 png only.
   OTHER_ICON          = 0x02;
   FRONT_COVER         = 0x03;
   BACK_COVER          = 0x04;
   LEAFLET             = 0x05;
   MEDIA               = 0x06; # label side of cd, picture disc vinyl, etc.
   LEAD_ARTIST         = 0x07;
   ARTIST              = 0x08;
   CONDUCTOR           = 0x09;
   BAND                = 0x0A;
   COMPOSER            = 0x0B;
   LYRICIST            = 0x0C;
   RECORDING_LOCATION  = 0x0D;
   DURING_RECORDING    = 0x0E;
   DURING_PERFORMANCE  = 0x0F;
   VIDEO               = 0x10;
   BRIGHT_COLORED_FISH = 0x11; # Whatever....????
   ILLUSTRATION        = 0x12; 
   BAND_LOGO           = 0x13; 
   PUBLISHER_LOGO      = 0x14; 

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      self.header.id = "APIC";
      data = self.disassemble_frame(data);

      input = StringIO(data);
      TRACE_MSG("APIC frame data size: " + str(len(data)));
      self.encoding = input.read(1);
      TRACE_MSG("APIC encoding: " + str(self.encoding));

      self.mimeType = "";
      ch = input.read(1);
      while ch != "\x00":
         self.mimeType += ch;
         ch = input.read(1);
      TRACE_MSG("APIC mime type: " + self.mimeType);

      self.pictureType = ord(input.read(1));
      TRACE_MSG("APIC picture type: " + str(self.pictureType));

      self.desciption = "";
      ch = input.read(1);
      while ch != "\x00":
         self.description += ch;
         ch = input.read(1);
      TRACE_MSG("APIC description: " + self.description);

      self.imageData = input.read();
      TRACE_MSG("APIC image data: " + str(len(self.imageData)) + " bytes");
      input.close();

      # TODO: Use a better method for naming these files and allow for 
      #       it to be toggled on/off.  In many cases access to the data is
      #       all that is required.
      f = file("./pic.jpg", "wb");
      f.write(self.imageData);
      f.close();

   def render(self):
      data = self.encoding + self.mimeType + "\x00" + self.pictureType +\
             self.description + '\x00' + self.imageData;
      return self.assemble_frame(data);



#######################################################################
class Unknown(Frame):
   data = "";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      data = self.disassemble_frame(data);
      self.data = data;

   def render(self):
      return self.assemble_frame(self.data)

#######################################################################
class MusicCDIdentifier(Frame):
   data = "";
   toc = "";

   def __init__(self, frameHeader, data):
      self.set(frameHeader, data);

   def set(self, frameHeader, data):
      self.header = frameHeader;
      self.header.id = "MCDI";
      data = self.disassemble_frame(data);
      self.toc = data;

   def render(self):
      data = self.data;
      return self.assemble_frame(data);

#######################################################################
# Create and return the appropriate frame.
# Exceptions: ....
def createFrame(frameHeader, data):
   f = None;
   # Text Frames
   if frameHeader.id[0] == 'T':
      if frameHeader.id == 'TXXX':
         f = UserTextInfo(frameHeader, data);
      else:
         f = TextInfo(frameHeader, data);
   # Comment Frames.
   elif frameHeader.id[0] == 'C':
      if frameHeader.id == 'COMM':
         f = Comment(frameHeader, data);
   # URL Frames.
   elif frameHeader.id[0] == 'W':
      if frameHeader.id == 'WXXX':
         f = UserURL(frameHeader, data);
      else:
         f = URL(frameHeader, data);
   # CD ID frame.
   elif frameHeader.id == 'MCDI':
      f = MusicCDIdentifier(frameHeader, data);
   # Attached picture
   elif frameHeader.id == 'APIC':
      f = Image(frameHeader, data);

   if f == None:
     f = Unknown(frameHeader, data);

   return f;

