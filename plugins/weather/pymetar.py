# Copyright (C) 2002  Tobias Klausmann
# Modified by Jerome Alet
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.        See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# By reading this code you agree not to ridicule the author =)

import string
import re
import urllib
import types
import math, fpformat

__author__ = "klausman-usenet@tuts.net"

__version__ = "0.4"

__doc__ = """Pymetar v%s (c) 2002 Tobias Klausman

Pymetar is a python module and command line tool designed to fetch Metar
reports from the NOAA (http://www.noaa.gov) and allow access to the included
weather information.

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307, USA.

Please e-mail bugs to: %s""" % (__version__, __author__)


#
# What a boring list to type !
#
# It seems the NOAA doesn't want to return plain text, but considering the
# format of their response, this is not to save bandwidth :-)
#
_WeatherConditions = {
                      "DZ" : ("Drizzle", "rain", {
                               "" :   "Moderate drizzle",
                               "-" :  "Light drizzle",
                               "+" :  "Heavy drizzle",
                               "VC" : "Drizzle in the vicinity",
                               "MI" : "Shallow drizzle",
                               "BC" : "Patches of drizzle",
                               "PR" : "Partial drizzle",
                               "TS" : ("Thunderstorm", "storm"),
                               "BL" : "Windy drizzle",
                               "SH" : "Showers",
                               "DR" : "Drifting drizzle",
                               "FZ" : "Freezing drizzle",
                             }),
                      "RA" : ("Rain", "rain", {
                               "" :   "Moderate rain",
                               "-" :  "Light rain",
                               "+" :  "Heavy rain",
                               "VC" : "Rain in the vicinity",
                               "MI" : "Shallow rain",
                               "BC" : "Patches of rain",
                               "PR" : "Partial rainfall",
                               "TS" : ("Thunderstorm", "storm"),
                               "BL" : "Blowing rainfall",
                               "SH" : "Rain showers",
                               "DR" : "Drifting rain",
                               "FZ" : "Freezing rain",
                             }),
                      "SN" : ("Snow", "snow", {
                               "" :   "Moderate snow",
                               "-" :  "Light snow",
                               "+" :  "Heavy snow",
                               "VC" : "Snow in the vicinity",
                               "MI" : "Shallow snow",
                               "BC" : "Patches of snow",
                               "PR" : "Partial snowfall",
                               "TS" : ("Snowstorm", "storm"),
                               "BL" : "Blowing snowfall",
                               "SH" : "Snowfall showers",
                               "DR" : "Drifting snow",
                               "FZ" : "Freezing snow",
                             }),
                      "SG" : ("Snow grains", "snow", {
                               "" :   "Moderate snow grains",
                               "-" :  "Light snow grains",
                               "+" :  "Heavy snow grains",
                               "VC" : "Snow grains in the vicinity",
                               "MI" : "Shallow snow grains",
                               "BC" : "Patches of snow grains",
                               "PR" : "Partial snow grains",
                               "TS" : ("Snowstorm", "storm"),
                               "BL" : "Blowing snow grains",
                               "SH" : "Snow grain showers",
                               "DR" : "Drifting snow grains",
                               "FZ" : "Freezing snow grains",
                             }),
                      "IC" : ("Ice crystals", "snow", {
                               "" :   "Moderate ice crystals",
                               "-" :  "Few ice crystals",
                               "+" :  "Heavy ice crystals",
                               "VC" : "Ice crystals in the vicinity",
                               "BC" : "Patches of ice crystals",
                               "PR" : "Partial ice crystals",
                               "TS" : ("Ice crystal storm", "storm"),
                               "BL" : "Blowing ice crystals",
                               "SH" : "Showers of ice crystals",
                               "DR" : "Drifting ice crystals",
                               "FZ" : "Freezing ice crystals",
                             }),
                      "PE" : ("Ice pellets", "snow", {
                               "" :   "Moderate ice pellets",
                               "-" :  "Few ice pellets",
                               "+" :  "Heavy ice pellets",
                               "VC" : "Ice pellets in the vicinity",
                               "MI" : "Shallow ice pellets",
                               "BC" : "Patches of ice pellets",
                               "PR" : "Partial ice pellets",
                               "TS" : ("Ice pellets storm", "storm"),
                               "BL" : "Blowing ice pellets",
                               "SH" : "Showers of ice pellets",
                               "DR" : "Drifting ice pellets",
                               "FZ" : "Freezing ice pellets",
                             }),
                      "GR" : ("Hail", "rain", {
                               "" :   "Moderate hail",
                               "-" :  "Light hail",
                               "+" :  "Heavy hail",
                               "VC" : "Hail in the vicinity",
                               "MI" : "Shallow hail",
                               "BC" : "Patches of hail",
                               "PR" : "Partial hail",
                               "TS" : ("Hailstorm", "storm"),
                               "BL" : "Blowing hail",
                               "SH" : "Hail showers",
                               "DR" : "Drifting hail",
                               "FZ" : "Freezing hail",
                             }),
                      "GS" : ("Small hail", "rain", {
                               "" :   "Moderate small hail",
                               "-" :  "Light small hail",
                               "+" :  "Heavy small hail",
                               "VC" : "Small hail in the vicinity",
                               "MI" : "Shallow small hail",
                               "BC" : "Patches of small hail",
                               "PR" : "Partial small hail",
                               "TS" : ("Small hailstorm", "storm"),
                               "BL" : "Blowing small hail",
                               "SH" : "Showers of small hail",
                               "DR" : "Drifting small hail",
                               "FZ" : "Freezing small hail",
                             }),
                      "UP" : ("Precipitation", "rain", {
                               "" :   "Moderate precipitation",
                               "-" :  "Light precipitation",
                               "+" :  "Heavy precipitation",
                               "VC" : "Precipitation in the vicinity",
                               "MI" : "Shallow precipitation",
                               "BC" : "Patches of precipitation",
                               "PR" : "Partial precipitation",
                               "TS" : ("Unknown thunderstorm", "storm"),
                               "BL" : "Blowing precipitation",
                               "SH" : "Showers, type unknown",
                               "DR" : "Drifting precipitation",
                               "FZ" : "Freezing precipitation",
                             }),
                      "BR" : ("Mist", "fog", {
                               "" :   "Moderate mist",
                               "-" :  "Light mist",
                               "+" :  "Thick mist",
                               "VC" : "Mist in the vicinity",
                               "MI" : "Shallow mist",
                               "BC" : "Patches of mist",
                               "PR" : "Partial mist",
                               "BL" : "Mist with wind",
                               "DR" : "Drifting mist",
                               "FZ" : "Freezing mist",
                             }),
                      "FG" : ("Fog", "fog", {
                               "" :   "Moderate fog",
                               "-" :  "Light fog",
                               "+" :  "Thick fog",
                               "VC" : "Fog in the vicinity",
                               "MI" : "Shallow fog",
                               "BC" : "Patches of fog",
                               "PR" : "Partial fog",
                               "BL" : "Fog with wind",
                               "DR" : "Drifting fog",
                               "FZ" : "Freezing fog",
                             }),
                      "FU" : ("Smoke", "fog", {
                               "" :   "Moderate smoke",
                               "-" :  "Thin smoke",
                               "+" :  "Thick smoke",
                               "VC" : "Smoke in the vicinity",
                               "MI" : "Shallow smoke",
                               "BC" : "Patches of smoke",
                               "PR" : "Partial smoke",
                               "TS" : ("Smoke w/ thunders", "storm"),
                               "BL" : "Smoke with wind",
                               "DR" : "Drifting smoke",
                             }),
                      "VA" : ("Volcanic ash", "fog", {
                               "" :   "Moderate volcanic ash",
                               "+" :  "Thick volcanic ash",
                               "VC" : "Volcanic ash in the vicinity",
                               "MI" : "Shallow volcanic ash",
                               "BC" : "Patches of volcanic ash",
                               "PR" : "Partial volcanic ash",
                               "TS" : ("Volcanic ash w/ thunders", "storm"),
                               "BL" : "Blowing volcanic ash",
                               "SH" : "Showers of volcanic ash",
                               "DR" : "Drifting volcanic ash",
                               "FZ" : "Freezing volcanic ash",
                             }),
                      "SA" : ("Sand", "fog", {
                               "" :   "Moderate sand",
                               "-" :  "Light sand",
                               "+" :  "Heavy sand",
                               "VC" : "Sand in the vicinity",
                               "BC" : "Patches of sand",
                               "PR" : "Partial sand",
                               "BL" : "Blowing sand",
                               "DR" : "Drifting sand",
                             }),
                      "HZ" : ("Haze", "fog", {
                               "" :   "Moderate haze",
                               "-" :  "Light haze",
                               "+" :  "Thick haze",
                               "VC" : "Haze in the vicinity",
                               "MI" : "Shallow haze",
                               "BC" : "Patches of haze",
                               "PR" : "Partial haze",
                               "BL" : "Haze with wind",
                               "DR" : "Drifting haze",
                               "FZ" : "Freezing haze",
                             }),
                      "PY" : ("Sprays", "fog", {
                               "" :   "Moderate sprays",
                               "-" :  "Light sprays",
                               "+" :  "Heavy sprays",
                               "VC" : "Sprays in the vicinity",
                               "MI" : "Shallow sprays",
                               "BC" : "Patches of sprays",
                               "PR" : "Partial sprays",
                               "BL" : "Blowing sprays",
                               "DR" : "Drifting sprays",
                               "FZ" : "Freezing sprays",
                             }),
                      "DU" : ("Dust", "fog", {
                               "" :   "Moderate dust",
                               "-" :  "Light dust",
                               "+" :  "Heavy dust",
                               "VC" : "Dust in the vicinity",
                               "BC" : "Patches of dust",
                               "PR" : "Partial dust",
                               "BL" : "Blowing dust",
                               "DR" : "Drifting dust",
                             }),
                      "SQ" : ("Squall", "storm", {
                               "" :   "Moderate squall",
                               "-" :  "Light squall",
                               "+" :  "Heavy squall",
                               "VC" : "Squall in the vicinity",
                               "PR" : "Partial squall",
                               "TS" : "Thunderous squall",
                               "BL" : "Blowing squall",
                               "DR" : "Drifting squall",
                               "FZ" : "Freezing squall",
                             }),
                      "SS" : ("Sandstorm", "fog", {
                               "" :   "Moderate sandstorm",
                               "-" :  "Light sandstorm",
                               "+" :  "Heavy sandstorm",
                               "VC" : "Sandstorm in the vicinity",
                               "MI" : "Shallow sandstorm",
                               "PR" : "Partial sandstorm",
                               "TS" : ("Thunderous sandstorm", "storm"),
                               "BL" : "Blowing sandstorm",
                               "DR" : "Drifting sandstorm",
                               "FZ" : "Freezing sandstorm",
                             }),
                      "DS" : ("Duststorm", "fog", {
                               "" :   "Moderate duststorm",
                               "-" :  "Light duststorm",
                               "+" :  "Heavy duststorm",
                               "VC" : "Duststorm in the vicinity",
                               "MI" : "Shallow duststorm",
                               "PR" : "Partial duststorm",
                               "TS" : ("Thunderous duststorm", "storm"),
                               "BL" : "Blowing duststorm",
                               "DR" : "Drifting duststorm",
                               "FZ" : "Freezing duststorm",
                             }),
                      "PO" : ("Dustwhirls", "fog", {
                               "" :   "Moderate dustwhirls",
                               "-" :  "Light dustwhirls",
                               "+" :  "Heavy dustwhirls",
                               "VC" : "Dustwhirls in the vicinity",
                               "MI" : "Shallow dustwhirls",
                               "BC" : "Patches of dustwhirls",
                               "PR" : "Partial dustwhirls",
                               "BL" : "Blowing dustwhirls",
                               "DR" : "Drifting dustwhirls",
                             }),
                      "+FC" : ("Tornado", "storm", {
                               "" :   "Moderate tornado",
                               "+" :  "Raging tornado",
                               "VC" : "Tornado in the vicinity",
                               "PR" : "Partial tornado",
                               "TS" : "Thunderous tornado",
                               "BL" : "Tornado",
                               "DR" : "Drifting tornado",
                               "FZ" : "Freezing tornado",
                              }),
                      "FC" : ("Funnel cloud", "fog", {
                               "" :   "Moderate funnel cloud",
                               "-" :  "Light funnel cloud",
                               "+" :  "Thick funnel cloud",
                               "VC" : "Funnel cloud in the vicinity",
                               "MI" : "Shallow funnel cloud",
                               "BC" : "Patches of funnel cloud",
                               "PR" : "Partial funnel cloud",
                               "BL" : "Funnel cloud w/ wind",
                               "DR" : "Drifting funnel cloud",
                             }),
                    }

#
# RegExps to extract the different parts from the Metar encoded report
TIME_RE_STR = r"^([0-9]{6})Z$"
WIND_RE_STR = r"^(([0-9]{3})|VRB)([0-9]?[0-9]{2})(G[0-9]?[0-9]{2})?KT$"
VIS_RE_STR  = r"^(([0-9]?[0-9])|(M?1/[0-9]?[0-9]))SM$"
CLOUD_RE_STR= r"^(CLR|SKC|BKN|SCT|FEW|OVC)([0-9]{3})?$"
TEMP_RE_STR = r"^(M?[0-9][0-9])/(M?[0-9][0-9])$"
PRES_RE_STR = r"^(A|Q)([0-9]{4})$"
COND_RE_STR = r"^(-|\\+)?(VC|MI|BC|PR|TS|BL|SH|DR|FZ)?(DZ|RA|SN|SG|IC|PE|GR|GS|UP|BR|FG|FU|VA|SA|HZ|PY|DU|SQ|SS|DS|PO|\\+?FC)$"

class MetarReport:

    """
    This class provides a means to download and parse the decoded METAR reports
    from http://weather.noaa.gov/

    In order to find the report relevant for you, find the closest station at
    http://www.nws.noaa.gov/oso/siteloc.shtml and feed its 4-letter station
    code to fetchMetarReport(), case does not matter.

    All methods return metric values, no matter what the station provides. The
    conversion factors were taken from the excellent "units" program.

    If None is returned that means the information wasn't available or could
    not be parsed. If you have the suspicion that failure to parse an
    information was this libs fault, please save the report generating the
    error send it to me with a few lines detailing the problem. Thanks!
    """

    def match_WeatherPart(self, regexp) :
        """
        Returns the matching part of the encoded Metar report.  
        regexp: the regexp needed to extract this part.  
        Returns the first matching string or None.  
        WARNING: Some Metar reports may contain several matching strings, only
        the first one is taken into account, e.g. FEW020 SCT075 BKN053 
        """
        if self.code is not None :
            rg = re.compile(regexp)
            for wpart in self.getRawMetarCode().split() :
                match = rg.match(wpart)
                if match :
                    return match.string[match.start(0) : match.end(0)]

    def extractSkyConditions(self) :
        """
        Extracts sky condition information from the encoded report.  Returns a
        tuple containing the description of the sky conditions as a string and
        a suggested pixmap name for an icon representing said sky condition.
        """
        wcond = self.match_WeatherPart(COND_RE_STR)
        if wcond is not None :
            if (len(wcond) > 3) and (wcond.startswith('+') or wcond.startswith('-')) :
                wcond = wcond[1:]
            if wcond.startswith('+') or wcond.startswith('-') :
                pphen = 1
            elif len(wcond) < 4 :
                pphen = 0
            else :
                pphen = 2
            squal = wcond[:pphen]
            sphen = wcond[pphen : pphen + 4]
            phenomenon = _WeatherConditions.get(sphen, None)
            if phenomenon is not None :
                (name, pixmap, phenomenon) = phenomenon
                pheninfo = phenomenon.get(squal, name)
                if type(pheninfo) != types.TupleType :
                    return (pheninfo, pixmap)
                else :
                    # contains pixmap info
                    return pheninfo

    def parseLatLong(self, latlong):
        """
        Parse Lat or Long in METAR notation into float values. N and E are +, S
        and W are -. Expects one positional string and returns one float value.
        """
        # I know, I could invert this if and put
        # the rest of the function into its block,
        # but I find this to be more readable
        if latlong is None: return None

        s = string.strip(string.upper(latlong))
        elms = string.split(s,'-')
        ud = elms[-1][-1]
        elms[-1] = elms[-1][:-1]
        elms = map(string.atoi, elms)
        coords = 0.0
        elen = len(elms)
        if elen > 2:
            coords = coords + float(elms[2])/3600.0

        if elen > 1:
            coords = coords + float(elms[1])/60.0

        coords=coords + float(elms[0])

        if ud in ('W','S'):
            coords=-1.0*coords

        f,i=math.modf(coords)

        if elen > 2:
            f=float(fpformat.sci(f,4))
        elif elen > 1:
            f=float(fpformat.sci(f,2))
        else:
            f=0.0

        return f+i

    def extractCloudInformation(self) :
        """
        Extracts cloud information.  returns None or a tuple (sky type as a
        string of text and suggested pixmap name)
        """   
        wcloud = self.match_WeatherPart(CLOUD_RE_STR)
        if wcloud is not None :
            stype = wcloud[:3]
            if (stype == "CLR") or (stype == "SKC") :
                return ("Clear sky", "sun")
            elif stype == "BKN" :
                return ("Broken clouds", "suncloud")
            elif stype == "SCT" :
                return ("Scattered clouds", "suncloud")
            elif stype == "FEW" :
                return ("Few clouds", "suncloud")
            elif stype == "OVC" :
                return ("Overcast", "cloud")

    def getFullReport(self):
        """
        Return the complete weather report.
        """
        return self.fullreport

    def getTemperatureCelsius(self):
        """
        Return the temperature in degrees Celsius.
        """
        return self.temp

    def getTemperatureFahrenheit(self):
        """
        Return the temperature in degrees Fahrenheit.
        """
        return (self.temp * (9.0/5.0)) + 32.0

    def getDewPointCelsius(self):
        """
        Return dewpoint in degrees Celsius.
        """
        return self.dewp

    def getDewPointFahrenheit(self):
        """
        Return dewpoint in degrees Fahrenheit.
        """
        return (self.dewp * (9.0/5.0)) + 32.0

    def getWindSpeed(self):
        """
        Return the wind speed in meters per second.
        """
        return self.windspeed

    def getWindDirection(self):
        """
        Return wind direction in degrees.
        """
        return self.winddir

    def getWindCompass(self):
        """
        Return wind direction as compass direction
        (e.g. NE or SSE)
        """
        return self.windcomp

    def getVisibilityKilometers(self):
        """
        Return visibility in km.
        """
        return self.vis

    def getVisibilityMiles(self):
        """
        Return visibility in miles.
        """
        return self.vis / 1.609344

    def getHumidity(self):
        """
        Return relative humidity in percent.
        """
        return self.humid

    def getPressure(self):
        """
        Return pressure in hPa.
        """
        return self.press

    def getRawMetarCode(self):
        """
        Return the encoded weather report.
        """
        return self.code

    def getWeather(self):
        """
        Return short weather conditions
        """
        return self.weather

    def getSkyConditions(self):
        """
        Return sky conditions
        """
        return self.sky

    def getStationName(self):
        """
        Return full station name
        """
        return self.fulln

    def getStationCity(self):
        """
        Return city-part of station name
        """
        return self.stat_city

    def getStationCountry(self):
        """
        Return country-part of station name
        """
        return self.stat_country

    def getCycle(self):
        """
        Return cycle value.
        The cycle value is not the frequency or delay between observations but
        the "time slot" in which the observation was made. There are 24 cycle
        slots every day which usually last from N:45 to N+1:45. The cycle from
        23:45 to 0:45 is cycle 0.
        """
        return self.cycle

    def getStationPosition(self):
        """
        Return latitude, longitude and altitude above sea level of station as a
        tuple. Some stations don't deliver altitude, for those, None is
        returned as altitude.  The lat/longs are expressed as follows:
        xx-yyd
        where xx is degrees, yy minutes and d the direction.
        Thus 51-14N means 51 degrees, 14 minutes north.  d may take the values
        N, S for latitues and W, E for longitudes. Latitude and Longitude may
        include seconds.  Altitude is always given as meters above sea level,
        including a trailing M.
        Schipohl Int. Airport Amsterdam has, for example:
        ('52-18N', '004-46E', '-2M')
        Moenchengladbach (where I live):
        ('51-14N', '063-03E', None)
        If you need lat and long as float values, look at 
        getStationPositionFloat() instead
        """
        return (self.latitude, self.longitude, self.altitude)

    def getStationPositionFloat(self):
        """
        Return latitude and longitude as float values in a tuple (lat,long,alt)
        """
        return (self.latf,self.longf,self.altitude)

    def getStationLatitude(self) :
        """
        Return the station's latitude in dd-mm[-ss]D format :
        dd : degrees
        mm : minutes
        ss : seconds
        D : direction (N, S, E, W)
        """
        return self.latitude

    def getStationLatitudeFloat(self):
        """
        Return latitude as a float
        """
        return self.latf

    def getStationLongitude(self) :
        """
        Return the station's longitude in dd-mm[-ss]D format :
        dd : degrees
        mm : minutes
        ss : seconds
        D : direction (N, S, E, W)
        """
        return self.longitude

    def getStationLongitudeFloat(self):
        """
        Return Longitude as a float
        """
        return (self.longf)

    def getStationAltitude(self) :
        """
        Return the station's altitude above the sea in meters.
        """
        return self.altitude

    def getReportURL(self):
        """
        Return the URL from which the report was fetched.
        """
        return self.reporturl

    def getTime(self):
        """
        Return the time when the observation was made.  Note that this is *not*
        the time when the report was fetched by us
        Format:  YYYY.MM.DD HHMM UTC
        Example: 2002.04.01 1020 UTC
        """
        return self.rtime

    def getISOTime(self):
        """
        Return the time when the observation was made in ISO 8601 format
        (e.g. 2002-07-25 15:12:00Z)
        """
        return(self.metar_to_iso8601(self.rtime))

    def getPixmap(self):
        """
        Return a suggested pixmap name, without extension, depending on current
        weather.
        """
        return self.pixmap

    def metar_to_iso8601(self, metardate) :
        """
        Converts a metar date to an ISO8601 date.
        """
        if metardate is not None:
            (date, hour, tz) = metardate.split()
            (year, month, day) = date.split('.')
            # assuming tz is always 'UTC', aka 'Z'
            return "%s-%s-%s %s:%s:00Z" % (year, month, day, hour[:2], hour[2:4])

    def strreverse(self, str):
        """
        Reverses a string
        """
        listr=list(str)
        listr.reverse()
        return (string.join(listr,""))

    def __init__(self, MetarStationCode = None):
        """
        Get initial report if a station code is passed as a parameter,
        otherwise initialize fields.
        """
        if MetarStationCode is not None :
            self.fetchMetarReport(MetarStationCode)
        else :
            self._ClearAllFields()

    def _ClearAllFields(self):
        """
        Clears all fields values.
        """
        # until finished, report is invalid
        self.valid = 0
        # Clear all
        self.fullreport=None
        self.temp=None
        self.windspeed=None
        self.winddir=None
        self.vis=None
        self.dewp=None
        self.humid=None
        self.press=None
        self.code=None
        self.weather=None
        self.sky=None
        self.fulln=None
        self.cycle=None
        self.windcomp=None
        self.rtime=None
        self.pixmap=None
        self.latitude=None
        self.longitude=None
        self.altitude=None
        self.stat_city=None
        self.stat_country=None
        self.reportutl=None
        self.latf=None
        self.longf=None

    def fetchMetarReport(self, station, baseurl="http://weather.noaa.gov/pub/data/observations/metar/decoded/"):
        """
        Retrieve the decoded METAR report from the given base URL and parse it.
        Fill the data properties in the class instance with the values found in
        the report, converting them to metric values where necessary.
        """
        self._ClearAllFields()
        station=string.upper(station)
        self.reporturl="%s%s.TXT" % (baseurl, station)
        fn=urllib.urlopen(self.reporturl)
        # Dump entire report in a variable
        self.fullreport=fn.read()

        # if fn.info().status is 0, everything seems to be in order
        if not fn.info().status:

            lines=string.split(self.fullreport,"\n")

            for line in lines:
                # Most lines start with a Header and a colon
                try:
                    header,data=string.split(line,":",1)
                except ValueError:
                    header=data=line

                header=string.strip(header)
                data=string.strip(data)

                # The station identifier and location
                if (string.find(header,"("+station+")")!=-1):
                    try:
                        loc,p=string.split(data,"(",1)
                        loc=string.strip(loc)
                        rloc=self.strreverse(loc)
                        rcoun,rcity=string.split(rloc,",",1)
                    except ValueError:
                        city=""
                        coun=""
                        p=data
                    try:
                        id,lat,long,ht=string.split(p," ")
                        ht = int(ht[:-1]) # skip the 'M' for meters
                    except ValueError:
                        id,lat,long=string.split(p," ")
                        ht=None
                    self.stat_city=string.strip(self.strreverse(rcity))
                    self.stat_country=string.strip(self.strreverse(rcoun))
                    self.fulln=loc
                    self.latitude = lat
                    self.longitude = long
                    self.latf=self.parseLatLong(lat)
                    self.longf=self.parseLatLong(long)
                    self.altitude = ht

                # The line containing the date/time of the report
                elif (string.find(data,"UTC")!=-1):
                    local,rt=string.split(data,"/")
                    self.rtime=string.strip(rt)

                # temperature
                elif (header=="Temperature"):
                    t,i=string.split(data," ",1)
                    self.temp=(float(t)-32)*(5.0/9.0)

                # wind direction and speed
                elif (header == "Wind"):
                    if (string.find(data,"Calm")!=-1):
                        self.windspeed=0.0
                        self.winddir=None
                        self.windcomp=None
                    elif (string.find(data,"Variable")!=-1):
                        v,a,speed,r=string.split(data," ",3)
                        self.windspeed=(float(speed)*0.44704)
                        self.winddir=None
                        self.windcomp=None
                    else:
                        f,t,comp,deg,r,d,speed,r=string.split(data," ",7)
                        self.winddir=int(deg[1:])
                        self.windcomp=string.strip(comp)
                        self.windspeed=(float(speed)*0.44704)

                # visibility
                elif (header=="Visibility"):
                    for d in data.split() :
                        try :
                            self.vis = float(d)*1.609344
                            break
                        except ValueError :
                            pass

                # dew point
                elif (header=="Dew Point"):
                    dp,i=string.split(data," ",1)
                    self.dewp=(float(dp)-32)*(5.0/9.0)

                # humidity
                elif (header=="Relative Humidity"):
                    h,i=string.split(data,"%",1)
                    self.humid=int(h)

                # pressure
                elif (header=="Pressure (altimeter)"):
                    p,r=string.split(data," ",1)
                    self.press=(float(p)*33.863886)

                # short weather description ("rain", "mist", ...)
                elif (header=="Weather"):
                    self.weather=data

                # short description of sky cond.
                elif (header=="Sky conditions"):
                    self.sky=data

                # the encoded weather report
                elif (header=="ob"):
                    self.code=string.strip(data)

                # the cycle value describes the cycle in
                # which the observations were made
                elif (header=="cycle"):
                    self.cycle=int(data)

            # decode cloud and sky conditions informations from
            # the raw report, this will suggest us a pixmap to use
            # to graphically represent the weather.
            cloudinfo = self.extractCloudInformation()
            if cloudinfo is not None :
                (cloudinfo, cloudpixmap) = cloudinfo
            else :
                (cloudinfo, cloudpixmap) = (None, None)
            conditions = self.extractSkyConditions()
            if conditions is not None :
                (conditions, condpixmap) = conditions
            else :
                (conditions, condpixmap) = (None, None)

            # fill the weather information
            self.weather = self.weather or conditions or cloudinfo

            # Pixmap guessed from general conditions has priority
            # over pixmap guessed from clouds
            self.pixmap = condpixmap or cloudpixmap

            # report is complete
            self.valid = 1

        # Even if the report is bad, toss the fd
        del fn
