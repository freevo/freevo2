#!/usr/bin/python
"""Implements a pure Python version of strptime.



Copyright (c) 2001, Brett Cannon
All rights reserved.

Released under the BSD license
(http://www.opensource.org/licenses/bsd-license.html)

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list
of conditions and the following disclaimer.  Redistributions in binary form must
reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the
distribution.   Neither the name of the <ORGANIZATION> nor the names of its
contributors may be used to endorse or promote products derived from this
software without specific prior written permission.  THIS SOFTWARE IS PROVIDED
BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.



The main function of this module is strptime() which attempts to simulate
time.strptime as best as possible while following the explanation of
time.strptime as spelled out by the official Python documentation.

CLASSES:
    TimeObjError -- Exception class for TimeObj object.
    StrptimeError -- Exception class for anything that might be triggered by
            user input.

    TimeObj -- Object for handling basic time manipulation.
    StrpObj -- Subclasses TimeObj to provide functionality for strptime().

FUNCTIONS:
    LocaleAssembly -- Takes in locale-specific information and returns a
                tuple and returns a new dictionary set up for use by strptime.
    strptime -- Acts like time.strptime() function using this module's various
                classes.

VARIABLES:
    CENTURY -- The century value used in conjunction with %y to have a complete
                year representation.
    ENGLISH
    SWEDISH -- Used for locale_setting parameter for strptime().
    AS_IS -- Used for option paramter for strptime() to extrapolate date info
            without checking its validity or  filling in of missing info.
    CHECK -- Used for option parameter for strptime() to check validity of
            extrapolated info.
    FILL_IN -- Used for option parameter for strptime() to check the validity
            of extrapolated info and to fill in missing info for the time.
    
Using from strptime import * will only export strptime().

Language support by this module is dependent on hard-coding it into the
StrpObj.DictAssembly() method.

If you come up with improvements or bug-fixes, please let me know at
drifty@bigfoot.com so I can integrate them into the official version.
Specifically, I am interested in more equations for filling in information and
more locale support.



Thanks has to be given to Andrew Markebo (flognat@fukt.hk-r.se) for his pure
Python version of strptime.  Made me improve locale support.
And obviously thanks has to be given to Guido van Rossum and everyone else who
has contributed to Python.  It is the greatest language I have ever used and I
thank you all for it.

"""
import re
from exceptions import Exception

__all__=['strptime','AS_IS','CHECK','FILL_IN','LocaleAssembly','ENGLISH','SWEDISH']

"""General info about the module"""
__author__='Brett Cannon'
__email__='drifty@bigfoot.com'
__version__='1.5'
__url__='http://www.drifty.org/'


"""Global settings"""
CENTURY=2000

"""Paramter constants"""
AS_IS='AS_IS'

CHECK='CHECK'

FILL_IN='FILL_IN'





def LocaleAssembly(DirectiveDict, MonthDict, DayDict, am_pmTuple):
    """Creates locale tuple for use by strptime.
    Takes in DirectiveDict (locale-specific regexes for extracting info from
    time string), MonthDict (locale full and abbreviated month names), DayDict
    (locale full and abbreviated weekday names), and am_pmDict (locale's valid
    representation of AM and PM).
    
    DirectiveDict, MonthDict, and DayDict are dictionaries while am_pmTuple is a
    tuple.  Look at how the ENGLISH dictionary is created for an example on how
    the passed-in values should be constructed.  Also, make sure that every
    value in your language dictionary has a corresponding version to one in the
    ENGLISH dictionary; leaving any out could cause problems.

    Also note that if there are any values in the BasicDict that you would like
    to override, then put it in the DirectiveDict dictionary that you pass in.
    
    """
    BasicDict={'%d':r'(?P<d>[0-3]\d)', #Day of the month [01,31].
         '%H':r'(?P<H>[0-2]\d)', #Hour (24-h) [00,23].
         '%I':r'(?P<I>[01]\d)', #Hour (12-h) [01,12].
         '%j':r'(?P<j>[0-3]\d\d)', #Day of the year [001,366].
         '%m':r'(?P<m>[01]\d)', #Month [01,12].
         '%M':r'(?P<M>[0-5]\d)', #Minute [00,59].
         '%S':r'(?P<S>[0-6]\d)', #Second [00,61].
         '%U':r'(?P<U>[0-5]\d)', #Week number of the year with Sunday as first day of the week [00,53].
         '%w':r'(?P<w>[0-6])', #Weekday [0(Sunday),6].
         '%W':r'(?P<W>[0-5]\d)', #Week number of the year with Monday as the first day of the week [00,53].
         '%y':r'(?P<y>\d\d)', #Year without century [00,99].
         '%Y':r'(?P<Y>\d\d\d\d)', #Year with century.
         '%Z':r'(?P<Z>(\D+ Time)|([\S\D]{3,3}))', #Time zone name (or no characters if no time zone exists).
         '%%':r'(?P<percent>%)' #Literal "%".  Doesn't matter that group name is not same as directive since literal % will be ignored in the end.
        }
    BasicDict.update(DirectiveDict)

    return (BasicDict,MonthDict,DayDict,am_pmTuple)



"""Built-in locales"""
ENGLISH_Lang=(
    {'%a':r'(?P<a>[^\s\d]{3,3})', #Abbreviated weekday name.
     '%A':r'(?P<A>[^\s\d]{6,9})', #Full weekday name.
     '%b':r'(?P<b>[^\s\d]{3,3})', #Abbreviated month name.
     '%B':r'(?P<B>[^\s\d]{3,9})', #Full month name.
     '%c':r'(?P<m>\d\d)/(?P<d>\d\d)/(?P<y>\d\d) (?P<H>\d\d):(?P<M>\d\d):(?P<S>\d\d)', #Appropriate date and time representation.
     '%p':r'(?P<p>(a|A|p|P)(m|M))', #Equivalent of either AM or PM.
     '%x':r'(?P<m>\d\d)/(?P<d>\d\d)/(?P<y>\d\d)', #Appropriate date representation.
     '%X':r'(?P<H>\d\d):(?P<M>\d\d):(?P<S>\d\d)'}, #Appropriate time representation.
    {'January':1, 'Jan':1,
     'February':2, 'Feb':2,
     'March':3, 'Mar':3,
     'April':4, 'Apr':4,
     'May':5,
     'June':6, 'Jun':6,
     'July':7, 'Jul':7,
     'August':8, 'Aug':8,
     'September':9, 'Sep':9,
     'October':10, 'Oct':10,
     'November':11, 'Nov':11,
     'December':12, 'Dec':12},
    {'Monday':0, 'Mon':0, #Adjusted for Monday-first counting.
     'Tuesday':1, 'Tue':1,
     'Wednesday':2, 'Wed':2,
     'Thursday':3, 'Thu':3,
     'Friday':4, 'Fri':4,
     'Saturday':5, 'Sat':5,
     'Sunday':6, 'Sun':6},
    (('am','AM'),('pm','PM'))
    )
ENGLISH=LocaleAssembly(ENGLISH_Lang[0],ENGLISH_Lang[1],ENGLISH_Lang[2],ENGLISH_Lang[3])

SWEDISH_Lang=(
    {'%a':r'(?P<a>[^\s\d]{3,3})',
     '%A':r'(?P<A>[^\s\d]{6,7})',
     '%b':r'(?P<b>[^\s\d]{3,3})',
     '%B':r'(?P<B>[^\s\d]{3,8})',
     '%c':r'(?P<a>[^\s\d]{3,3}) (?P<d>[0-3]\d) (?P<b>[^\s\d]{3,3}) (?P<Y>\d\d\d\d) (?P<H>[0-2]\d):(?P<M>[0-5]\d):(?P<S>[0-6]\d)',
     '%p':r'(?P<p>(a|A|p|P)(m|M))',
     '%x':r'(?P<m>\d\d)/(?P<d>\d\d)/(?P<y>\d\d)',
     '%X':r'(?P<H>\d\d):(?P<M>\d\d):(?P<S>\d\d)'},
    {'Januari':1, 'Jan':1,
     'Februari':2, 'Feb':2,
     'Mars':3, 'Mar':3,
     'April':4, 'Apr':4,
     'Maj':5, 'Maj':5,
     'Juni':6, 'Jun':6,
     'Juli':7, 'Jul':7,
     'Augusti':8, 'Aug':8,
     'September':9, 'Sep':9,
     'Oktober':10, 'Okt':10,
     'November':11, 'Nov':11,
     'December':12, 'Dec':12},
    {'Måndag':0, 'Mån':0,
     'Tisdag':1, 'Tis':1,
     'Onsdag':2, 'Ons':2,
     'Torsdag':3, 'Tor':3,
     'Fredag':4, 'Fre':4,
     'Lördag':5, 'Lör':5,
     'Söndag':6, 'Sön':6},
    (('am','AM'),('pm','PM'))
    )
SWEDISH=LocaleAssembly(SWEDISH_Lang[0],SWEDISH_Lang[1],SWEDISH_Lang[2],SWEDISH_Lang[3])





class TimeObjError(Exception):
    """Generic TimeObj object exception"""
    def __init__(self, args=None):
        self.args=args

class StrptimeError(TimeObjError):
    """Generic StrpObj object exception"""
    def __init__(self,args=None):
        self.args=args



class TimeObj:
    """An object with basic time manipulation.

    VARIABLES:
        year -- Any integer.
        month -- [1,12]
        day -- [1,366]
        hour -- [0,23]
        minute -- [0,59]
        second -- [0,61]
        day_week -- [0,6] Day of the week.  Monday is 0.
        daylight -- [-1,1] Daylight savings.
        

    METHODS:
        __init__ (self, year=None, month=None, day=None, hour=None, minute=None,
                    second=None, day_week=None, julian_date=None, daylight=None)
                -- Sets up instance variables.
        __repr__(self) -> string -- Representation of instance.
        julianFirst(self) -> integer -- Calculates and returns the julian day for
                                January 1 of this year.  Requires that the year
                                be known.
        gregToJulian(self) -> integer -- Figures out the julian date using the
                                        year, month, day, and julianFirst()
                                        method.
        julianToGreg(self) -> tuple_of_ints -- Figures out the Gregorian date
                                        according to the year and julian date.
                                        Returns the tuple in the format of
                                        (year, month, day).
        dayWeek(self) -> integer -- Figures out the day of the week according to
                                    year, month, and day.
        FillInInfo(self) -- Figures out what info is missing and can be filled
                            in with the current knowledge and proceeds to do so
                            using gregToJulian(), julianToGreg(), and dayWeek().
        CheckIntegrity(self) -> integer -- Checks if the known information about
                                            the time is within allowed parameters.
                                            If a check fails, StrptimeError is raised.
        return_time(self) -> tuple -- Returns a tuple of the time information.
                                    All found instances of None are replaced
                                    replaced with 0.  The format of the tuple is
                                    (year, month, day, hour, minute, second, day
                                    of the week, julian date, daylight savings).

    """
    def __init__(self, year=None, month=None, day=None, hour=None, minute=None, second=None, day_week=None, julian_date=None, daylight=None):
        """Sets up instances variables.  All values can be set at initialization.
        Any left out info is automatically set to None."""
        self.year=year
        self.month=month
        self.day=day
        self.hour=hour
        self.minute=minute
        self.second=second
        self.day_week=day_week
        self.julian_date=julian_date
        self.daylight=daylight

    def __repr__(self):
        """Representation of the instance lists all info on the time"""
        return '<TimeObj instance year=%s month=%s day=%s hour=%s minute=%s second=%s day_of_the_week=%s julian_date=%s daylight_savings=%s>' % (self.year,self.month,self.day,self.hour,self.minute,self.second,self.day_week,self.julian_date,self.daylight)

    def julianFirst(self):
        """Calculates the julian day for the first of the current year. Uses
        self.year to figure out the year being used."""
        a=(14-1)/12
        y=(self.year+4800)-a
        m=1+12*a-3
        julian_first=1+((153*m+2)/5)+365*y+y/4-y/100+y/400-32045
        return julian_first

    def gregToJulian(self):
        """Converts the Gregorian date to the Julian date.
        Uses self.year, self.month, and self.day along with julianFirst().  If
        the Julian day needs to be calculated, just add the results of
        julianFirst() andgregToJulian()."""
        a=(14-self.month)/12
        y=self.year+4800-a
        m=self.month+12*a-3
        julian_day=self.day+((153*m+2)/5)+365*y+y/4-y/100+y/400-32045

        julian_first=self.julianFirst()

        julian_date=julian_day-julian_first
        julian_date=julian_date+1 #To make result be same as what strftime would give.
        return julian_date

    def julianToGreg(self):
        """Converts the Julian date to the Gregorian date.
        Uses julianFirst() (which uses self.year) and self.julian_date."""
        julian_first=self.julianFirst()
        julian_day=self.julian_date+julian_first
        julian_day=julian_day-1
        a=julian_day+32044
        b=(4*a+3)/146097
        c=a-((146097*b)/4)
        d=(4*c+3)/1461
        e=c-((1461*d)/4)
        m=(5*e+2)/153
        day=e-((153*m+2)/5)+1
        month=m+3-12*(m/10)
        year=100*b+d-4800+(m/10)
        return (year,month,day)

    def dayWeek(self):
        """Figures out the day of the week using self.year, self.month, and self.day.
        Monday is 0."""
        a=(14-self.month)/12
        y=self.year-a
        m=self.month+12*a-2
        day_week=(self.day+y+(y/4)-(y/100)+(y/400)+((31*m)/12))%7
        if day_week==0:
            day_week=6
        else:
            day_week=day_week-1
        return day_week

    def FillInInfo(self):
        """Based on the current time information, it figures out what other info can be filled in."""
        if self.julian_date==None and self.year and self.month and self.day:
            julian_date=self.gregToJulian()
            self.julian_date=julian_date
        if (self.month==None or self.day==None) and self.year and self.julian_date:
            gregorian=self.julianToGreg()
            self.month=gregorian[1] #Year tossed out since needed to do calculation in the first place.
            self.day=gregorian[2]
        if self.day_week==None and self.year and self.month and self.day:
            self.dayWeek()

    def CheckIntegrity(self):
        """Checks info integrity based on the range that a number can be.
        Checking whether numbers are integers or not is unneeded since regex
        would catch that. Year is not checked since it can be any positive 4-
        digit integer number.  Any invalid values raises a StrptimeError
        exception."""
        success=1
        if self.month!=None:
            if not (1<=self.month<=12):
                success=0
                raise StrptimeError,'Month incorrect'
        if self.day!=None:
            if not 1<=self.day<=31:
                success=0
                raise StrptimeError,'Day incorrect'
        if self.hour!=None:
            if not 0<=self.hour<=23:
                success=0
                raise StrptimeError,'Hour incorrect'
        if self.minute!=None:
            if not 0<=self.minute<=59:
                success=0
                raise StrptimeError,'Minute incorrect'
        if self.second!=None:
            if not 0<=self.second<=61: #61 covers leap seconds.
                success=0
                raise StrptimeError,'Second incorrect'
        if self.day_week!=None:
            if not 0<=self.day_week<=6:
                success=0
                raise StrptimeError,'Day of the Week incorrect'
        if self.julian_date!=None:
            if not 0<=self.julian_date<=366:
                success=0
                raise StrptimeError,'Julian Date incorrect'
        if self.daylight!=None:
            if not -1<=self.daylight<=1:
                success=0
                raise StrptimeError,'Daylight Savings incorrect'
        return success
            

    def return_time(self):
        """Returns a tuple in the format used by time.gmtime().
        All instances of None in the information are replaced with 0."""
        temp_time=[self.year, self.month, self.day, self.hour, self.minute, self.second, self.day_week, self.julian_date, self.daylight]
        for current in xrange(9):
            if temp_time[current]==None:
                temp_time[current]=0
        return tuple(temp_time)



class StrpObj(TimeObj):
    
    """Subclasses TimeObj to provide methods for functionality like time.strptime().

    METHODS:
        RECreation(self, format, DIRECTIVEDict) -> re object -- Creates the re
                    object used for extrapolating the info out of a string based
                    on the passed-in format string.
        convert(self, string, format, locale_setting) -- Takes the string and
                    extrapolates time info from it based on the format string
                    and chosen locale. 
    """
    
    def RECreation(self, format, DIRECTIVEDict):
        """Takes in a format string and the DIRECTIVEDict and creates a regex object for convert()."""
        Directive=0
        REString=''
        for char in format:
            if char=='%' and not Directive:
                Directive=1
            elif Directive:
                if not DIRECTIVEDict.has_key('%'+char):
                    raise GenericError
                else:
                    REString=REString+DIRECTIVEDict['%'+char]
                    Directive=0
            else:
                REString=REString+char
        return re.compile(REString, re.IGNORECASE)

    def convert(self, string, format, locale_setting):
        """Extrapolates the info from the passed in string based on the format
        and locale setting.  Uses DictAssembly() and RECreation()."""
        DIRECTIVEDict,MONTHDict,DAYDict,AM_PM=locale_setting
        REComp=self.RECreation(format, DIRECTIVEDict)
        reobj=REComp.match(string)
        for found in reobj.groupdict().keys():
            if found in ('y','Y'): #Year
                if found=='y': #Without century
                    self.year=CENTURY+int(reobj.group('y'))
                else: #With century
                    self.year=int(reobj.group('Y'))
            elif found in ('b','B','m'): #Month
                if found=='m':
                    self.month=int(reobj.group(found))
                else: #Int
                    try:
                        self.month=MONTHDict[reobj.group(found)]
                    except KeyError:
                        raise StrptimeError, 'Unrecognized month'
            elif found=='d': #Day of the Month
                self.day=int(reobj.group(found))
            elif found in ('H','I'): #Hour
                hour=int(reobj.group(found))
                if found=='H':
                    self.hour=hour
                else:
                    try:
                        if reobj.group('p') in AM_PM[0]:
                            AP=0
                        else:
                            AP=1
                    except KeyError:
                        raise StrptimeError, 'Lacking needed AM/PM information'
                    if AP:
                        if hour==12:
                            self.hour=12
                        else:
                            self.hour=12+hour
                    else:
                        if hour==12:
                            self.hour=0
                        else:
                            self.hour=hour
            elif found=='M': #Minute
                self.minute=int(reobj.group(found))
            elif found=='S': #Second
                self.second=int(reobj.group(found))
            elif found in ('a','A','w'): #Day of the week
                if found=='w':
                    day_value=int(reobj.group(found))
                    if day_value==0:
                        self.day_week=6
                    else:
                        self.day_week=day_value-1
                else:
                    try:
                        self.day_week=DAYDict[reobj.group(found)]
                    except KeyError:
                        raise StrptimeError, 'Unrecognized day'
            elif found=='j': #Julian date
                self.julian_date=int(reobj.group(found))
            elif found=='Z': #Daylight savings
                TZ=reobj.group(found)
                if len(TZ)==3:
                    if TZ[1] in ('D','d'):
                        self.daylight=1
                    else:
                        self.daylight=0
                elif TZ.find('Daylight')!=-1:
                    self.daylight=1
                else:
                    self.daylight=0



def strptime(string, format='%a %b %d %H:%M:%S %Y', option=AS_IS, locale_setting=ENGLISH):
    """Creates a StrpObj instance and uses its methods to find out the tuple representation
    (as based on time.gmtime()) of the string passed in based on the format
    string and the locale setting.  Also triggers the checking of the integrity
    of the extrapolated info and fills in missing gaps where possible
    based on the passed in option.  It then returns the tuple representation of
    the instance."""
    Obj=StrpObj()
    Obj.convert(string, format, locale_setting)
    if option in (FILL_IN,CHECK):
        Obj.CheckIntegrity()
    if option in (FILL_IN,):
        Obj.FillInInfo()
    return Obj.return_time()
