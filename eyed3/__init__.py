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

import re, os, string, stat;
import utils, frames, binfuncs, mp3;
from utils import *;
from binfuncs import *;
from frames import *;
from stat import *;

# Program meta info.
version = utils.version;
maintainer = utils.maintainer;

# Constants
ID3_ANY = 0;
ID3_V1  = 1;
ID3_V2  = 2;

#######################################################################
class TagException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

#######################################################################
class FrameException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

#######################################################################
class TagHeader:
   TAG_HEADER_SIZE = 10;

   majorVersion = None;
   minorVersion = None;
   revVersion = None;

   # Flag bits
   unsync = 0;
   extended = 0;
   experimental = 0;
   # v2.4 addition
   footer = 0;

   tagSize = 0;
   
   # Constructor
   def __init__(self):
      self.clear();

   def clear(self):
      self.majorVersion = None;
      self.minorVersion = None;
      self.revVersion = None;
      self.unsync = 0;
      self.extended = 0;
      self.experimental = 0;
      self.tagSize = 0;

   # Given a file handle this method attempts to identify and then parse
   # a ID3 v2 header.  If successful, the parsed values are stored in
   # the instance variable.  If the files does not contain an ID3v2 tag
   # false is returned. A TagException is thrown if a tag is found, but is
   # not valid or corrupt.
   def parse(self, f):
      self.clear();

      # The first three bytes of a v2 header is "ID3".
      if f.read(3) != "ID3":
         return 0;
      TRACE_MSG("Located ID3 v2 tag");

      # The next 2 bytes are the minor and revision versions.
      version = f.read(2);
      self.majorVersion = major = 2;
      self.minorVersion = minor = ord(version[0]);
      self.revVersion = ord(version[1]);
      TRACE_MSG("TagHeader [major]: " + str(self.majorVersion));
      TRACE_MSG("TagHeader [minor]: " + str(self.minorVersion));
      TRACE_MSG("TagHeader [revis]: " + str(self.revVersion));
      if not (major == 2 and (minor == 3 or minor == 4)):
         raise TagException("ID3 v" + str(major) + "." + str(minor) +\
                            " is not supported.");


      # The first 3 bits of the next byte are flags.
      (self.unsync,
       self.extended,
       self.experimental,
       self.footer,
       None, None, None, None) = bytes2bin(f.read(1));
      TRACE_MSG("TagHeader [flags]: unsync(%d) extended(%d) "\
                "experimental(%d) footer(%d)" % (self.unsync, self.extended,
                                                 self.experimental,
                                                 self.footer));

      # The size of the optional extended header, frames, and padding
      # afer unsynchronization.  This is a sync safe integer, so only the
      # bottom 7 bits of each byte are used.
      self.tagSize = bin2dec(bytes2bin(f.read(4), 7));
      TRACE_MSG("TagHeader [size]: %d (0x%X)" % (self.tagSize, self.tagSize));

      # TODO: Read the extended header if present.
      if self.extended:
         raise TagException("Extended headers not supported.");

      return 1;

#######################################################################
class FrameHeader:
   # The tag header
   tagHeader = None;
   # The 4 character frame ID.
   id = None;
   # An array of 16 "bits"...
   flags = NULL_FRAME_FLAGS;
   # ...and the info they store.
   tagAlter = 0;
   fileAlter = 0;
   readOnly = 0;
   compressed = 0;
   encrypted = 0;
   grouped = 0;
   unsync = 0;
   dataLen = 0;
   # The size of the data following this header.
   dataSize = 0;

   # 2.4 not only added flag bits, but also reordered the previously defined
   # flags.  So these are mapped once we know the version.
   TAG_ALTER   = None;   
   FILE_ALTER  = None;   
   READ_ONLY   = None;   
   COMPRESSION = None;   
   ENCRYPTION  = None;   
   GROUPING    = None;   
   UNSYNC      = None;   
   DATA_LEN    = None;   

   # Constructor.
   def __init__(self, tagHeader):
      self.tagHeader = tagHeader;
      major = tagHeader.majorVersion;
      minor = tagHeader.minorVersion;
      # 1.x tags are converted to 2.4 frames internally.  These frames are
      # created with frame flags \x00.
      if (major == 1 and (minor == 0 or minor == 1)) or \
         (major == 2 and minor == 3):
         self.TAG_ALTER   = 0;   
         self.FILE_ALTER  = 1;   
         self.READ_ONLY   = 2;   
         self.COMPRESSION = 8;   
         self.ENCRYPTION  = 9;   
         self.GROUPING    = 10;   
         # This is not really in 2.3 frame header flags, but there is
         # a "global" unsync bit in the tag header and that is written here
         # so access to the tag header is not required.
         self.UNSYNC      = 14;   
         # And this is mapped to an used bit, so that 0 is returned.
         self.DATA_LEN    = 4;
      elif major == 2 and minor == 4:
         self.TAG_ALTER   = 1;   
         self.FILE_ALTER  = 2;   
         self.READ_ONLY   = 3;   
         self.COMPRESSION = 12;   
         self.ENCRYPTION  = 13;   
         self.GROUPING    = 9;   
         self.UNSYNC      = 14;   
         self.DATA_LEN    = 15;   
      else:
         raise ValueError("ID3 v" + str(major) + "." + str(minor) +\
                          " is not supported.");

   # Returns 1 on success and 0 when a null tag (marking the beginning of
   # padding).  In the case of an invalid frame header, a TagExeption is 
   # thrown.
   def parse(self, f):
      TRACE_MSG("FrameHeader [start byte]: %d (0x%X)" % (f.tell(),
                                                         f.tell()));
      frameId = f.read(4);
      TRACE_MSG("FrameHeader [id]: " + frameId);

      if self.isFrameIdValid(frameId):
         self.id = frameId;
         # dataSize corresponds to the size of the data segment after
         # encryption, compression, and unzynchronization.
         sz = f.read(4);
         # In ID3 v2.4 this value became a synch-safe integer, meaning only
         # the low 7 bits are used per byte.
         if self.tagHeader.minorVersion == 3:
            self.dataSize = bin2dec(bytes2bin(sz, 8));
         else:
            self.dataSize = bin2dec(bytes2bin(sz, 7));
         TRACE_MSG("FrameHeader [data size]: %d (0x%X)" % (self.dataSize,
                                                           self.dataSize));
 
         # Frame flags.
         flags = f.read(2);
         self.flags = bytes2bin(flags);
         self.tagAlter = self.flags[self.TAG_ALTER];
         self.fileAlter = self.flags[self.FILE_ALTER];
         self.readOnly = self.flags[self.READ_ONLY];
         self.compressed = self.flags[self.COMPRESSION];
         self.encrypted = self.flags[self.ENCRYPTION];
         self.grouped = self.flags[self.GROUPING];
         self.unsync = self.flags[self.UNSYNC];
         self.dataLen = self.flags[self.DATA_LEN];
         TRACE_MSG("FrameHeader [flags]: ta(%d) fa(%d) ro(%d) co(%d) "\
                   "en(%d) gr(%d) un(%d) dl(%d)" % (self.tagAlter,
                                                    self.fileAlter,
                                                    self.readOnly,
                                                    self.compressed,
                                                    self.encrypted,
                                                    self.grouped,
                                                    self.unsync,
                                                    self.dataLen));
      elif frameId == '\x00\x00\x00\x00':
         TRACE_MSG("FrameHeader: Null frame id found at byte " +\
                   str(f.tell()));
         return 0;
      else:
         raise TagException("FrameHeader: Illegal Frame ID: " + frameId);
      return 1;


   def isFrameIdValid(self, id):
      return re.compile(r"^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]$").match(id);

   def clearFlags(self):
      flags = [0] * 16;

#######################################################################
# A class for containing and managing ID3v2.Frame objects.
class FrameSet(list):

   def __init__(self, l = None):
      if l:
         for f in l:
            if not isinstance(f, Frame):
               raise TypeError("Invalid type added to FrameSet: " +\
                               f.__class__);
            self.append(f);

   # Setting a FrameSet instance like this 'fs = []' morphs the instance into
   # a list object.
   def clear(self):
      del self[0:];

   # Read frames starting from the current read position of the file object.
   # Returns the amount of padding which occurs after the tag, but before the
   # audio content.  A return valule of 0 DOES NOT imply an error.
   def parse(self, f, tagHeader):
      paddingSize = 0;
      sizeLeft = tagHeader.tagSize;

      while sizeLeft > 0:
         TRACE_MSG("sizeLeft: " + str(sizeLeft));
         TRACE_MSG("FrameSet: Reading Frame #" + str(len(self) + 1));
         frameHeader = FrameHeader(tagHeader);
         if not frameHeader.parse(f):
            paddingSize = sizeLeft;
            break;

         # The tag header has a global unsync flag that overrides the frame
         # header bit, so it's copied.
         if not frameHeader.unsync and tagHeader.unsync:
            frameHeader.unsync = tagHeader.unsync;
            TRACE_MSG("FrameSet: Tag header unsync overridding frame unsync "\
                      "bit.");
 
         # Frame data.
         TRACE_MSG("FrameSet: Reading %d (0x%X) bytes of data from byte "\
                   "pos %d (0x%X)" % (frameHeader.dataSize,
                                      frameHeader.dataSize, f.tell(),
                                      f.tell()));
         data = f.read(frameHeader.dataSize);
           
         frm = createFrame(frameHeader, data);
 
         self.append(frm);
         # Each frame contains dataSize + headerSize(10) bytes.
         sizeLeft -= (frameHeader.dataSize + TagHeader.TAG_HEADER_SIZE);

      return paddingSize;

   #######################################################################
   # Accepts both int and string keys. Throws IndexError and TypeError.
   def __getitem__(self, key):
      if isinstance(key, int):
         if key >= 0 and key < len(self):
            return list.__getitem__(self, key);
         else:
            raise IndexError("FrameSet index out of range");
      elif isinstance(key, str):
         for f in self:
            if f.header.id == key:
               return f;
         return None;
      else:
         raise TypeError("FrameSet key must be type int or string");

#######################################################################
# ID3 tag class.  The class is capable of reading v1 and v2 tags.  ID3 v1.x
# are converted to v2 frames.
class Tag:
   # ISO-8859-1
   encoding = '\x00';

   # ID3v1 tags do not contain a header.  The only ID3v1 values stored
   # in this header are the major/minor version.
   header = TagHeader();

   # Contains the tag's frames.  ID3v1 fields are read and converted
   # the the corresponding v2 frame.  
   frames = FrameSet();

   # Optional byte (0x00) padding.
   paddingSize = 0;

   # Used internally for iterating over frames.
   iterIndex = None;

   # The file the Tag is linked to.
   fileName = None;

   # Constructor.  An empty tag is created and the link method is used
   # to read an mp3 file's v1.x or v2.x tag contents.
   def __init__(self):
      pass;

   # Returns an read-only iterator for all frames.
   def __iter__(self):
      if len(self.frames):
         self.iterIndex = 0;
      else:
         self.iterIndex = None;
      return self;

   def next(self):
      if self.iterIndex == None or self.iterIndex == len(self.frames):
         raise StopIteration;
      frm = self.frames[self.iterIndex];
      self.iterIndex += 1;
      return frm;

   # Returns true when an ID3 tag is read from f which may be a file name
   # or an aleady opened file object.  In the latter case, the file object 
   # is not closed by the Tag object.
   #
   # By default, both ID3 v2 and v1 tags are parsed in that order.
   # If a v2 tag is found then a v1 parse is not performed.  This behavior
   # can be refined by passing ID3_V1 or ID3_V2 as the second argument.
   #
   # Converts all ID3v1 data into ID3v2 frames internally.
   # May throw IOError, or TagException if parsing fails.
   def link(self, f, v = ID3_ANY):
      if isinstance(f, file):
         self.fileName = f.name;
      elif isinstance(f, str):
         self.fileName = f;
      else:
         raise TagException("Invalid type passed to Tag.link: " + 
                            str(type(f)));

      TRACE_MSG("Linking File: " + self.fileName);
      self.frames.clear();
      if v == ID3_ANY:
         if self.__loadV2Tag(f) or self.__loadV1Tag(f):
            return 1;
      elif v == ID3_V2:
         if self.__loadV2Tag(f):
            return 1;
      elif v == ID3_V1:
         if self.__loadV1Tag(f):
            return 1;
	 
      return 0;

   #######################################################################
   # Returns false when an ID3 v1 tag is not present, or contains no data.
   def __loadV1Tag(self, f):
      if isinstance(f, str):
         fp = file(f, "rb")
         closeFile = 1;
      else:
         fp = f;
         closeFile = 0;

      # Seek to the end of the file where all ID3v1 tags are written.
      fp.seek(0, 2)
      if fp.tell() > 127:
         fp.seek(-128, 2)
         id3tag = fp.read(128)
         if id3tag[0:3] == "TAG":
            TRACE_MSG("Located ID3 v1 tag");
            # 1.0 is implied until a 1.1 feature is recognized.
            self.header.majorVersion = 1;
            self.header.minorVersion = 0;
            self.header.revVersion = 0;

            title = re.sub("\x00+$", "", id3tag[3:33].strip())
            TRACE_MSG("Tite: " + title);
            if title:
               self.setTitle(title);

            artist = re.sub("\x00+$", "", id3tag[33:63].strip())
            TRACE_MSG("Artist: " + artist);
            if artist:
               self.setArtist(artist);

            album = re.sub("\x00+$", "", id3tag[63:93].strip())
            TRACE_MSG("Album: " + album);
            if album:
               self.setAlbum(album);

            year = re.sub("\x00+$", "", id3tag[93:97].strip())
            TRACE_MSG("Year: " + year);
            if year: #and int(year): # We're ignoring invalid year codes they /should/ be int().
               self.setYear(year);

	    comment = id3tag[97:127] 
	    
	    if ord(comment[-2]) == 0 and ord(comment[-1]) != 0:
	        # Parse track number (added to ID3v1.1) if present
	        track = ord(comment[-1])
		TRACE_MSG("Contains track per v1.1 spec")
		comment = comment[:2]
		TRACE_MSG("Track: " + str(track))
		self.setTrackNum((track, None));
		TRACE_MSG("Setting minor version to 1")
		self.header.minorVersion = 1
            else:
                track = None
                self.header.minorVersion = 0;
            
	    self.setComment(comment);

            genre = ord(id3tag[127:128])
            TRACE_MSG("Genre ID: " + str(genre));
            self.setGenre(genre);

      if closeFile:
         fp.close()
      return len(self.frames);

   #######################################################################
   # Returns false when an ID3 v2 tag is not present, or contains 0 frames.
   def __loadV2Tag(self, f):
      if isinstance(f, str):
         fp = file(f, "rb")
         closeFile = 1;
      else:
         fp = f;
         closeFile = 0;

      try:
         # Look for a tag and if found load it.
         if not self.header.parse(fp):
            return 0;

         # Header is definitely there so at least one frame *must* follow.
         self.paddingSize = self.frames.parse(fp, self.header);
      except TagException:
         f.close();
         raise;

      if closeFile:
         fp.close();
      if len(self.frames) > 0:
         return 1;
      else:
         return 0;
         
   #######################################################################
   def getFrame(self, frameId):
      for f in self.frames:
         if f.header.id == frameId:
            return f;
      return None;
         
   def removeFrame(self, frameId):
      i = 0;
      while i < len(self.frames):
         if self.frames[i].id == frameId:
            del self.frames[i];
            return 1;
         i += 1;
      return 0;

   # Use with care, very low-level wrt data (i.e. encoding bytes and UserText
   # description)
   def setTextFrame(self, frameId, data, frameHeader = None):
      if not re.compile("^T[A-Z0-9][A-Z0-9][A-Z0-9]$").match(frameId):
         raise FrameException("Invalid Frame ID: " + frameId);

      if not frameHeader:
         replaceHeader = 0;
         frameHeader = FrameHeader(self.header);
      else:
         replaceHeader = 1;
      frameHeader.id = frameId;

      if frameHeader.id == USERTEXT_FID:
         userText = 1;
      else:
         userText = 0;

      f = self.getFrame(frameHeader.id);
      if f:
         if replaceHeader:
            f.set(frameHeader, data);
         else:
            f.set(f.header, data);
      else:
         if userText:
            self.frames.append(UserTextInfo(frameHeader, data));
         else:
            self.frames.append(TextInfo(frameHeader, data));
      return 1;

   def setCommentFrame(self, data, frameHeader = None):
      if not frameHeader:
         replaceHeader = 0;
         frameHeader = FrameHeader(self.header);
      else:
         replaceHeader = 1;
      frameHeader.id = "COMM";

      f = self.frames[COMMENT_FID];
      if f:
         if replaceHeader:
            f.set(frameHeader, data);
         else:
            f.set(f.header, data);
      else:
         self.frames.append(Comment(frameHeader, data));

   def getArtist(self):
      # I've seen many different frame IDs for artists in the wild.
      # Look for the common ones, but prefer TPE1
      for fid in ARTIST_FIDs:
         f = self.frames[fid];
         if f:
            return f.value;
      return None; 

   def setArtist(self, a):
      self.setTextFrame(ARTIST_FIDs[0], self.encoding + a);
 
   def getAlbum(self):
      f = self.frames[ALBUM_FID];
      if f:
         return f.value;
      else:
         return None;

   def setAlbum(self, a):
      self.setTextFrame(ALBUM_FID, self.encoding + a);

   def getTitle(self):
      f = self.frames[TITLE_FID];
      if f:
         return f.value;
      else:
         return None;

   def setTitle(self, t):
      self.setTextFrame(TITLE_FID, self.encoding + t);
 
   def getYear(self):
      f = self.frames[YEAR_FID];
      if f:
         return f.value;
      else:
         return None;

   def setYear(self, y):
      self.setTextFrame(YEAR_FID, self.encoding + y);

   # Throws GenreException when the tag contains an unrecognized genre format.
   def getGenre(self):
      f = self.frames[GENRE_FID];
      if f:
         g = Genre();
         g.parse(f.value);
         return g;
      else:
         return None;

   def setGenre(self, g):
      self.setTextFrame(GENRE_FID, self.encoding + str(g));

   # Returns a tuple with the first value containing the track number and the
   # second the total number of tracks.  One or both of these values may be
   # None depending on what is available in the tag. 
   def getTrackNum(self):
      f = self.frames[TRACKNUM_FID];
      if f:
         n = string.split(f.value, '/');
         if len(n) == 2:
            return (n[0], n[1]);
         else:
            return (n[0], None);
      else:
         return (None, None);

   # Accepts a tuple with the first value containing the track number and the
   # second the total number of tracks.  One or both of these values may be
   # None.
   def setTrackNum(self, n):
      if n[0] != None and n[1] != None:
         s = str(n[0]) + "/" + str(n[1]);
      elif n[0] != None and n[1] == None:
         s = str(n[0]);
      else:
         s = None;

      if s:
         self.setTextFrame(TRACKNUM_FID, self.encoding + s);
      else:
         self.removeFrame(TRACKNUM_FID);

   def setComment(self, cmt, desc = "", lang = "eng"):
      if self.isV2():
         data = self.encoding + lang + desc + "\x00" + cmt;
      else:
         data = self.encoding + lang + "" + "\x00" + cmt;
      self.setCommentFrame(data);

   def getComment(self):
      f = self.frames[COMMENT_FID];
      if f:
         return f.comment;
      else:
         return None;

   def getCommentLang(self):
      f = self.frames[COMMENT_FID];
      if f:
         return f.lang;
      else:
         return None;

   def getCommentDesc(self):
      f = self.frames[COMMENT_FID];
      if f:
         return f.description;
      else:
         return None;

   # Test ID3 major version.
   def isV1(self):
      return self.header.majorVersion == 1;
   def isV2(self):
      return self.header.majorVersion == 2;

   def getVersion(self):
      v = str(self.header.majorVersion) + "." + str(self.header.minorVersion);
      if self.header.revVersion:
         v += "." + str(self.header.revVersion);
      return v;


#######################################################################
class GenreException(Exception):
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;


#######################################################################
class Genre:
   id = None;
   name = None;

   def __init__(self):
      pass;

   def getId(self):
      return self.id;
   def getName(self):
      return self.name;

   # Sets the genre id.  The objects name field is set to the corresponding
   # value obtained from eyeD3.genres.
   #
   # Throws GenreException when name does not map to a valid ID3 v1.1. id.
   # This behavior can be disabled by passing 0 as the second argument.
   def setId(self, id, verify = 1):
      if not isinstance(id, int):
         raise GenreException("Invalid genre id: " + str(id));

      try:
         name = genres[id];
      except Exception, ex:
         if verify:
            raise GenreException("Invalid genre id: " + str(id));

      if verify and not name:
         raise GenreException("Genre id maps to a null name: " + str(id));

      self.id = id;
      self.name = name;

   # Sets the genre name.  The objects id field is set to the corresponding
   # value obtained from eyeD3.genres.
   #
   # Throws GenreException when name does not map to a valid ID3 v1.1. name.
   # This behavior can be disabled by passing 0 as the second argument.
   def setName(self, name, verify = 1):
      if not isinstance(name, str):
         raise GenreException("Invalid genre name: " + str(name));

      try:
         id = genres[name];
         # Get titled case.
         name = genres[id];
      except:
         if verify:
            raise GenreException("Invalid genre name: " + name);

      self.id = id;
      self.name = name;


   # Sets the genre id and name. 
   #
   # Throws GenreException when eyeD3.genres[id] != name (case insensitive). 
   # This behavior can be disabled by passing 0 as the second argument.
   def set(self, id, name, verify = 1):
      if not isinstance(id, int):
         raise GenreException("Invalid genre id: " + id);
      if not isinstance(name, str):
         raise GenreException("Invalid genre name: " + str(name));

      if not verify:
         self.id = id;
         self.name = name;
      else:
         try:
            if genres[name] != id:
               raise GenreException("eyeD3.genres[" + str(id) + "] " +\
                                    "does not match " + name);
            self.id = id;
            self.name = name;
         except:
            raise GenreException("eyeD3.genres[" + str(id) + "] " +\
                                 "does not match " + name);
      
   # Parses genre information from genreStr. 
   # The following formats are supported:
   # 01, 2, 23, 125 - ID3 v1 style.
   # (01), (2), (129)Hardcore, (9)Metal - ID3 v2 style with and without
   #                                      refinement.
   #
   # Throws GenreException when an invalid string is passed.
   def parse(self, genreStr, verify = 1):
      if not isinstance(genreStr, str):
         raise TypeError("genreStr must be a string");

      genreStr = genreStr.strip();

      if not genreStr:
         self.id = None;
         self.name = None;
         return;

      # ID3 v1 style.
      # Match 03, 34, 129.
      regex = re.compile("[0-9][0-9]?[0-9]?$");
      if regex.match(genreStr):
         if len(genreStr) != 1 and genreStr[0] == '0':
            genreStr = genreStr[1:];

         self.setId(int(genreStr), verify);
         return;

      # ID3 v2 style.
      # Match (03), (0)Blues, (15) Rap
      regex = re.compile("\(([0-9][0-9]?[0-9]?)\)(.*)$");
      m = regex.match(genreStr);
      if m:
         (id, name) = m.groups();
         if len(id) != 1 and id[0] == '0':
            id = id[1:];
            
         if id and name:
            self.set(int(id), name.strip(), verify);
         else:
            self.setId(int(id), verify);
         return;

      # Non standard, but witnessed.
      # Match genreName alone.  e.g. Rap, Rock, blues.
      regex = re.compile("[A-Z]+$", re.IGNORECASE);
      if regex.match(genreStr):
         self.setName(genreStr, verify);
         return;

      raise GenreException("Genre string cannot be parsed: " + genreStr);

   def __str__(self):
      return str(self.id) + ": " + self.name;

#######################################################################
class InvalidAudioFormatException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

#######################################################################
class Mp3AudioFile:
   fileName       = str();
   fileSize       = int();
   header         = mp3.Header();
   xingHeader     = None;
   tag            = Tag();
   invalidFileExc = InvalidAudioFormatException("File is not mp3");
   # Number of seconds required to play the audio file.
   playTime       = None;

   def __init__(self, fileName, tagVersion = ID3_ANY):
      self.playTime = None;
      self.fileName = fileName;
      mp3Match = re.compile(".*\.[Mm][Pp]3$");

      if not mp3Match.match(fileName):
         raise self.invalidFileExc;
      f = file(fileName, "rb");

      # Create ID3 tag.
      tag = Tag();
      hasTag = tag.link(f, tagVersion);
      if not hasTag:
         tag = None;

      # Find the first mp3 frame.
      if tag == None or tag.isV1():
         framePos = 0;
      else:
         # XXX: Note that v2.4 allows for appended tags, and we'll need to 
         # account for that. I've never seen one in the wild though....
         framePos = tag.header.TAG_HEADER_SIZE + tag.header.tagSize;
      f.seek(framePos);
      bString = f.read(4);
      if len(bString) < 4:
         raise InvalidAudioFormatException("Unable to find a valid mp3 "\
                                           "frame");
      frameHead = bin2dec(bytes2bin(bString));
      header = mp3.Header();
      # Keep reading until we find a valid mp3 frame header.
      while not header.isValid(frameHead):
         frameHead <<= 8;
         bString = f.read(1);
         if len(bString) != 1:
            raise InvalidAudioFormatException("Unable to find a valid mp3 "\
                                              "frame");
         frameHead |= ord(bString[0]);
      TRACE_MSG("mp3 header %x found at position: %d (0x%X)" % \
                (frameHead, f.tell() - 4, f.tell() - 4));

      # Decode the header.
      try:
         header.decode(frameHead);
         # Check for Xing header inforamtion which will always be in the
         # first "null" frame.
         f.seek(-4, 1);
         mp3Frame = f.read(header.frameLength);
         if mp3Frame.find("Xing") != -1:
            xingHeader = mp3.XingHeader();
            if not xingHeader.decode(mp3Frame):
               raise InvalidAudioFormatException("Corrupt Xing header");
         else:
            xingHeader = None;
      except mp3.Mp3Exception, ex:
         raise InvalidAudioFormatException(str(ex));

      # Compute track play time.
      tpf = mp3.computeTimePerFrame(header);
      if xingHeader:
         self.playTime = int(tpf * xingHeader.numFrames);
      else:
         length = self.getSize();
         if tag and tag.isV2():
            length -= tag.header.TAG_HEADER_SIZE + tag.header.tagSize;
            # Handle the case where there is a v2 tag and a v1 tag.
            f.seek(-128, 2)
            if f.read(3) == "TAG":
               length -= 128;
         elif tag and tag.isV1():
            length -= 128;
         self.playTime = int((length / header.frameLength) * tpf);    

      self.header = header;
      self.xingHeader = xingHeader;
      self.tag = tag;
      f.close();

   def getTag(self):
      return self.tag;

   def getSize(self):
      if not self.fileSize:
         self.fileSize = os.stat(self.fileName)[ST_SIZE];
      return self.fileSize;

   def getPlayTime(self):
      return self.playTime;

   def getPlayTimeString(self):
      total = self.getPlayTime();
      h = total / 3600;
      m = (total % 3600) / 60;
      s = (total % 3600) % 60;
      if h:
         timeStr = "%d:%.2d:%.2d" % (h, m, s);
      else:
         timeStr = "%d:%.2d" % (m, s);
      return timeStr;

   # Returns a tuple.  The first value is a boolean which if true means the
   # bit rate returned in the second value is variable.
   def getBitRate(self):
      xHead = self.xingHeader;
      if xHead:
         tpf = mp3.computeTimePerFrame(self.header);
         br = int((xHead.numBytes * 8) / (tpf * xHead.numFrames * 1000));
         vbr = 1;
      else:
         br = self.header.bitRate;
         vbr = 0;
      return (vbr, br);

   def getBitRateString(self):
      (vbr, bitRate) = self.getBitRate();
      brs = "%d kb/s" % bitRate;
      if vbr:
         brs = "~" + brs;
      return brs;

#######################################################################
class GenreMap(list):

   #######################################################################
   # Accepts both int and string keys. Throws IndexError and TypeError.
   def __getitem__(self, key):
      if isinstance(key, int):
         if key >= 0 and key < len(self):
            v = list.__getitem__(self, key);
            if v:
               return v.title();
            else:
               return None;
         else:
            raise IndexError("genre index out of range");
      elif isinstance(key, str):
         if key.lower() in self:
            return self.index(key.lower());
         else:
            raise IndexError(key + " genre not found");
      else:
         raise TypeError("genre key must be type int or string");

   def __init__(self):
      # ID3 genres as defined by the v1.1 spec with WinAmp extensions.
      self.append(string.lower('Blues'));
      self.append(string.lower('Classic Rock'));
      self.append(string.lower('Country'));
      self.append(string.lower('Dance'));
      self.append(string.lower('Disco'));
      self.append(string.lower('Funk'));
      self.append(string.lower('Grunge'));
      self.append(string.lower('Hip-Hop'));
      self.append(string.lower('Jazz'));
      self.append(string.lower('Metal'));
      self.append(string.lower('New Age'));
      self.append(string.lower('Oldies'));
      self.append(string.lower('Other'));
      self.append(string.lower('Pop'));
      self.append(string.lower('R&B'));
      self.append(string.lower('Rap'));
      self.append(string.lower('Reggae'));
      self.append(string.lower('Rock'));
      self.append(string.lower('Techno'));
      self.append(string.lower('Industrial'));
      self.append(string.lower('Alternative'));
      self.append(string.lower('Ska'));
      self.append(string.lower('Death Metal'));
      self.append(string.lower('Pranks'));
      self.append(string.lower('Soundtrack'));
      self.append(string.lower('Euro-Techno'));
      self.append(string.lower('Ambient'));
      self.append(string.lower('Trip-Hop'));
      self.append(string.lower('Vocal'));
      self.append(string.lower('Jazz+Funk'));
      self.append(string.lower('Fusion'));
      self.append(string.lower('Trance'));
      self.append(string.lower('Classical'));
      self.append(string.lower('Instrumental'));
      self.append(string.lower('Acid'));
      self.append(string.lower('House'));
      self.append(string.lower('Game'));
      self.append(string.lower('Sound Clip'));
      self.append(string.lower('Gospel'));
      self.append(string.lower('Noise'));
      self.append(string.lower('AlternRock'));
      self.append(string.lower('Bass'));
      self.append(string.lower('Soul'));
      self.append(string.lower('Punk'));
      self.append(string.lower('Space'));
      self.append(string.lower('Meditative'));
      self.append(string.lower('Instrumental Pop'));
      self.append(string.lower('Instrumental Rock'));
      self.append(string.lower('Ethnic'));
      self.append(string.lower('Gothic'));
      self.append(string.lower('Darkwave'));
      self.append(string.lower('Techno-Industrial'));
      self.append(string.lower('Electronic'));
      self.append(string.lower('Pop-Folk'));
      self.append(string.lower('Eurodance'));
      self.append(string.lower('Dream'));
      self.append(string.lower('Southern Rock'));
      self.append(string.lower('Comedy'));
      self.append(string.lower('Cult'));
      self.append(string.lower('Gangsta Rap'));
      self.append(string.lower('Top 40'));
      self.append(string.lower('Christian Rap'));
      self.append(string.lower('Pop / Funk'));
      self.append(string.lower('Jungle'));
      self.append(string.lower('Native American'));
      self.append(string.lower('Cabaret'));
      self.append(string.lower('New Wave'));
      self.append(string.lower('Psychedelic'));
      self.append(string.lower('Rave'));
      self.append(string.lower('Showtunes'));
      self.append(string.lower('Trailer'));
      self.append(string.lower('Lo-Fi'));
      self.append(string.lower('Tribal'));
      self.append(string.lower('Acid Punk'));
      self.append(string.lower('Acid Jazz'));
      self.append(string.lower('Polka'));
      self.append(string.lower('Retro'));
      self.append(string.lower('Musical'));
      self.append(string.lower('Rock & Roll'));
      self.append(string.lower('Hard Rock'));
      self.append(string.lower('Folk'));
      self.append(string.lower('Folk-Rock'));
      self.append(string.lower('National Folk'));
      self.append(string.lower('Swing'));
      self.append(string.lower('Fast  Fusion'));
      self.append(string.lower('Bebob'));
      self.append(string.lower('Latin'));
      self.append(string.lower('Revival'));
      self.append(string.lower('Celtic'));
      self.append(string.lower('Bluegrass'));
      self.append(string.lower('Avantgarde'));
      self.append(string.lower('Gothic Rock'));
      self.append(string.lower('Progressive Rock'));
      self.append(string.lower('Psychedelic Rock'));
      self.append(string.lower('Symphonic Rock'));
      self.append(string.lower('Slow Rock'));
      self.append(string.lower('Big Band'));
      self.append(string.lower('Chorus'));
      self.append(string.lower('Easy Listening'));
      self.append(string.lower('Acoustic'));
      self.append(string.lower('Humour'));
      self.append(string.lower('Speech'));
      self.append(string.lower('Chanson'));
      self.append(string.lower('Opera'));
      self.append(string.lower('Chamber Music'));
      self.append(string.lower('Sonata'));
      self.append(string.lower('Symphony'));
      self.append(string.lower('Booty Bass'));
      self.append(string.lower('Primus'));
      self.append(string.lower('Porn Groove'));
      self.append(string.lower('Satire'));
      self.append(string.lower('Slow Jam'));
      self.append(string.lower('Club'));
      self.append(string.lower('Tango'));
      self.append(string.lower('Samba'));
      self.append(string.lower('Folklore'));
      self.append(string.lower('Ballad'));
      self.append(string.lower('Power Ballad'));
      self.append(string.lower('Rhythmic Soul'));
      self.append(string.lower('Freestyle'));
      self.append(string.lower('Duet'));
      self.append(string.lower('Punk Rock'));
      self.append(string.lower('Drum Solo'));
      self.append(string.lower('A Cappella'));
      self.append(string.lower('Euro-House'));
      self.append(string.lower('Dance Hall'));
      self.append(string.lower('Goa'));
      self.append(string.lower('Drum & Bass'));
      self.append(string.lower('Club-House'));
      self.append(string.lower('Hardcore'));
      self.append(string.lower('Terror'));
      self.append(string.lower('Indie'));
      self.append(string.lower('BritPop'));
      self.append(string.lower('Negerpunk'));
      self.append(string.lower('Polsk Punk'));
      self.append(string.lower('Beat'));
      self.append(string.lower('Christian Gangsta Rap'));
      self.append(string.lower('Heavy Metal'));
      self.append(string.lower('Black Metal'));
      self.append(string.lower('Crossover'));
      self.append(string.lower('Contemporary Christian'));
      self.append(string.lower('Christian Rock'));
      self.append(string.lower('Merengue'));
      self.append(string.lower('Salsa'));
      self.append(string.lower('Thrash Metal'));
      self.append(string.lower('Anime'));
      self.append(string.lower('JPop'));
      self.append(string.lower('Synthpop'));
      
      # This list is extened with None until 'Unknown' is added at index 255.
      self.extend([None] * (256 - len(self) - 1));
      self.append(string.lower('Unknown'));

#
# Module level globals.
#
genres = GenreMap();

