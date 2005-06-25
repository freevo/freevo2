# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# msnbc.py - Grabber for weather data.
# -----------------------------------------------------------------------------
# $Id$
#
# 
# The grabber will accept any location that is recognized by the msnbc website.
# To find a location code for you, goto:
#  - http://www.msnbc.com/news/WEA_Front.asp?cp1=1
# or search for you city/country in the data/location_codes.txt file. A file
# with weather codes is also shipped in data/weathertypes.dat.
#
# Based on Freevo Weather 0.8 by James A. Laska <jlaska@nc.rr.com>
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
#
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
# -----------------------------------------------------------------------------

# python modules
import re
import time
import logging

# webinfo modules
from pywebinfo.grabberitem import GrabberItem
from pywebinfo.grabber     import Grabber


log = logging.getLogger('pywebinfo')

class WeatherItem(GrabberItem):
    # geo data
    country = None
    city = None
    region = None
    state = None
    last_update = None

    # weather data
    icon = None
    description = None
    temp = None
    temp_felt = None
    wind_strength = None
    wind_direction = None
    barometer = None
    humidity = None
    uv = None
    visibility = None
    forecast = None

    # map img url
    map_url = None

    # id
    acid = None

    def __init__(self, metric=False):
        self.metric = metric

    def set(self, var, value):
        if var == 'swCity':
            self.city = value

        elif var == 'swSubDiv':
            self.state = value

        elif var == 'swCountry':
            self.country = value

        elif var == 'swRegion':
            self.region = value

        elif var == 'swTemp':
            if self.metric:
                value = toCelcius(value)
            self.temp = value

        elif var == 'swWindS':
            if self.metric:
                value = toKilometers(value)
            self.wind_strength = value

        elif var == 'swWindD':
            self.wind_direction = value

        elif var == 'swBaro':
            if self.metric:
                value = toBarometer(value)
            self.barometer = value

        elif var == 'swHumid':            
            self.humidity = value 

        elif var == 'swReal':
            if self.metric:
                value = toCelcius(value)
            self.temp_felt = value 

        elif var == 'swUV':
            self.uv = value

        elif var == 'swVis':
            if self.metric and value != 999.0:
                value = toKilometers(value)
            self.visibility = value

        elif var == 'swConText':
            self.description = value

        elif var == 'swAcid':
            self.acid = value 

        elif var == 'swCIcon':
            self.icon = WeatherType().get_icon(value)

        elif var == 'swFore':
            self.forecast = parseForecast(value, self.metric)

        elif var == 'swLastUp':
            # last update data='03/18/2005 16:50:00'
            tstruct          = time.strptime(value, '%m/%d/%Y %H:%M:%S')
            self.last_update = time.mktime(tstruct)



class WeatherForecastItem(GrabberItem):
    """
    Item holding forecast information
    """
    date = None
    temp_high = None
    temp_low  = None
    weather_type = None
    weather_icon = None



class WeatherGrabber(Grabber):
    data_url = 'http://www.msnbc.com/m/chnk/d/weather_d_src.asp?acid=%s'
    map_url  = 'http://www.weather.com/weather/map/%s?from=LAPmaps'
    map_url2 = 'http://www.weather.com/%s'

    # regular expressions
    lmatch = re.compile('^[ \t]+this\.(\w+) = "([^"]+)";*').match
    mmatch = re.compile('^[ \t]+if \(isMinNS4\) var mapNURL = "([^"]+)*').match
    imatch = re.compile('^<IMG NAME="mapImg" SRC="([^"]+)"').match


    def __init__(self, cb_progress=None, cb_error=None,
                 cb_result=None, language='en-US'):

        Grabber.__init__(self, cb_progress, cb_error, cb_result, language)
        self.item = None

    def handle_line(self, url, line):
        """
        Handle one line
        """
        if url.startswith('http://www.msnbc'):
            # parse data
            m = self.lmatch(line)
            if m:
                self.item.set(m.group(1), m.group(2))

        elif url.startswith('http://www.weather.com/weather/map/'):
            if not self.item.map_url:
                m = self.mmatch(line)
                if m:
                    self.maplink = m.group(1)
                    self.get_url(self.map_url2 % self.maplink)

        elif url == (self.map_url2 % self.maplink):
            # ok, parse the image location
            if self.item and not self.item.map_url:
                m = self.imatch(line)
                if m:
                    self.item.map_url = m.group(1)
                    # finished parsing
                    # deliver the results
                    self.deliver_result(self.item)
                    self.item = None
 

    def handle_finished(self, url):
        """
        Handle finished url
        """
        if url.startswith('http://www.msnbc'):
            if self.maplink and self.item.acid:
                # we are also parsing the maplink
                self.get_url(self.map_url % self.item.acid)
            else:
                # deliver the result right away
                self.deliver_result(self.item)


    def search(self, location, metric=False, maplink=True):
        """
        Get the weatherdata from the given location.
        @metric:  return represent units in metric system.
        @maplink: set true if it should parse sat-picture.
                  (requires another page download)
        """
        self.location = location
        self.metric   = metric
        self.item     = WeatherItem(metric)
        self.maplink  = maplink
        self.get_url(self.data_url % location)

        return self.return_result()
        

def parseForecast(data, metric):
    """
    Parse the forecast items
    """
    params = data.split("|")

    # FIXME what does this mean?
    #dayNum       = int( params[0] )
    #curDay       = int( time.strftime("%u") ) + 1

    #if dayNum != curDay:
    #    pastTime = 1

    forecast = []

    for i in range(0, 4):
        wf = WeatherForecastItem()

        # date
        wf.date = time.mktime(time.strptime( params[i+6], '%m/%d/%Y'))

        # icon
        wf.weather_icon = params[i+10]

        # weather type
        wf.weather_type = params[i+15]

        # temperatures
        if metric:
            params[i+20] = toCelcius(params[i+20])
            params[i+40] = toCelcius(params[i+40])

        wf.temp_high = params[i+20]
        wf.temp_low  = params[i+40]

        forecast.append(wf)
    
    return forecast

   	
def toCelcius(fTemp):
    """
    Convert from farenheit to celcius
    """
    return '%d' % ((5.0/9.0)*( float(fTemp) - 32.0))


def toKilometers(miles):
    """
    Convert from miles to kilometers
    """
    return '%d' % int(float(miles) * 1.6)

def toBarometer(baro):
    return '%.1f' % (float(baro) * 3.386)

############# WEATHER DATA #############
class WeatherType(object):
    _types = {
    '1'   : 'Cloudy,cloudy.png',
    '3'   : 'Mostly Cloudy,mcloudy.png',
    '4'   : 'Partly Cloudy,pcloudy.png',
    '13'  : 'Light Rain,lshowers.png',
    '14'  : 'Showers,showers.png',
    '16'  : 'Snow,snowshow.png',
    '18'  : 'Rain,showers.png',
    '19'  : 'AM Showers,showers.png',
    '20'  : 'Fog,fog.png',
    '21'  : 'Few Showers,lshowers.png',
    '22'  : 'Mostly Sunny,sunny.png',
    '24'  : 'Sunny,sunny.png',
    '25'  : 'Scattered Flurries,flurries.png',
    '26'  : 'AM Clouds/PM Sun,pcloudy.png',
    '27'  : 'Isolated T-Storms,thunshowers.png',
    '28'  : 'Scattered Thunderstorms,thunshowers.png',
    '29'  : 'PM Showers,showers.png',
    '30'  : 'PM Showers/Wind,showers.png',
    '31'  : 'Rain/Snow Showers,rainsnow.png',
    '32'  : 'Few Snow Showers,flurries.png',
    '33'  : 'Cloudy/Wind,cloudy.png',
    '34'  : 'Flurries/Wind,flurries.png',
    '35'  : 'Mostly Cloudy/Windy,mcloudy.png',
    '36'  : 'Rain/Thunder,thunshowers.png',
    '37'  : 'Partly Cloudy/Windy,pcloudy.png',
    '38'  : 'AM Rain/Snow Showers,rainsnow.png',
    '40'  : 'Light Rain/Wind,lshowers.png',
    '41'  : 'Showers/Wind,showers.png',
    '42'  : 'Heavy Snow,snowshow.png',
    '44'  : 'Mostly Sunny/Wind,sunny.png',
    '45'  : 'Flurries,flurries.png',
    '47'  : 'Rain/Wind,showers.png',
    '49'  : 'Sct Flurries/Wind,flurries.png',
    '50'  : 'Sct Strong Storms,thunshowers.png',
    '51'  : 'PM T-Storms,thunshowers.png',
    '53'  : 'Thunderstorms,thunshowers.png',
    '55'  : 'Sunny/Windy,sunny.png',
    '56'  : 'AM Thunderstorms,thunshowers.png',
    '62'  : 'AM Rain,showers.png',
    '64'  : 'Iso T-Storms/Wind,thunshowers.png',
    '65'  : 'Rain/Snow,rainsnow.png',
    '66'  : 'Sct T-Storms/Wind,showers.png',
    '67'  : 'AM Showers/Wind,showers.png',
    '70'  : 'Sct Snow Showers,snowshow.png',
    '71'  : 'Snow to Ice/Wind,snowshow.png',
    '76'  : 'AM Ice,rainsnow.png',
    '77'  : 'Snow to Rain,rainsnow.png',
    '80'  : 'AM Light Rain,lshowers.png',
    '81'  : 'PM Light Rain,lshowers.png',
    '82'  : 'PM Rain,showers.png',
    '84'  : 'Snow Showers,snowshow.png',
    '85'  : 'Rain to Snow,rainsnow.png',
    '86'  : 'PM Rain/Snow,snowshow.png',
    '88'  : 'Few Showers/Wind,showers.png',
    '90'  : 'Snow/Wind,snowshow.png',
    '91'  : 'PM Rain/Snow Showers,rainsnow.png',
    '92'  : 'PM Rain/Snow/Wind,rainsnow.png',
    '93'  : 'Rain/Snow Showers/Wind,rainsnow.png',
    '94'  : 'Rain/Snow/Wind,rainsnow.png',
    '98'  : 'Light Snow,flurries.png',
    '100' : 'PM Snow,snowshow.png',
    '101' : 'Few Snow Showers/Wind,snowshow.png',
    '103' : 'Light Snow/Wind,flurries.png',
    '104' : 'Wintry Mix,flurries.png',
    '105' : 'AM Wintry Mix,rainsnow.png',
    '106' : 'Hvy Rain/Freezing Rain,rainsnow.png',
    '108' : 'AM Light Snow,flurries.png',
    '109' : 'PM Rain/Snow/Wind,rainsnow.png',
    '114' : 'Rain/Freezing Rain,showers.png',
    '118' : 'T-Storms/Wind,thunshowers.png',
    '123' : 'Sprinkles,lshowers.png',
    '125' : 'AM Snow Showers,snowshow.png',
    '126' : 'AM Clouds/PM Sun/Wind,pcloudy.png',
    '128' : 'AM Rain/Snow/Wind,rainsnow.png',
    '130' : 'Rain to Snow/Wind,rainsnow.png',
    '132' : 'Snow to Wintry Mix,snowshow.png',
    '133' : 'PM Snow Showers/Wind,snowshow.png',
    '135' : 'Snow and Ice to Rain,rainsnow.png',
    '137' : 'Heavy Rain,showers.png',
    '138' : 'AM Rain/Ice,showers.png',
    '145' : 'AM Snow Showers/Wind,snowshow.png',
    '146' : 'AM Light Snow/Wind,flurries.png',
    '150' : 'PM Light Rain/Wind,lshowers.png',
    '152' : 'AM Light Wintry Mix,rainsnow.png',
    '153' : 'PM Light Snow/Wind,flurries.png',
    '154' : 'Heavy Rain/Wind,showers.png',
    '155' : 'PM Snow Shower,snowshow.png',
    '158' : 'Snow to Rain/Wind,rainsnow.png',
    '164' : 'PM Light Rain/Ice,showers.png',
    '167' : 'AM Snow,snowshow.png',
    '171' : 'Snow to Ice,snowshow.png',
    '172' : 'Wintry Mix/Wind,rainsnow.png',
    '175' : 'PM Light Snow,flurries.png',
    '178' : 'AM Drizzle,lshowers.png',
    '189' : 'Strong Storms/Wind,thunshowers.png',
    '193' : 'PM Drizzle,lshowers.png',
    '194' : 'Drizzle,lshowers.png',
    '201' : 'AM Light Rain/Wind,lshowers.png',
    '204' : 'AM Rain/Wind,showers.png',
    '223' : 'Wintry Mix to Snow,rainsnow.png',
    '231' : 'Rain,showers.png',
    '240' : 'AM Light Rain/Ice,rainsnow.png',
    '259' : 'Hvy Rain/Freezing Rain,showers.png',
    '271' : 'Snow Showers/Windy,snowshow.png',
    '988' : 'Partly Cloudy/Windy,pcloudy.png',
    '989' : 'Light Rain Shower,lshowers.png',
    '990' : 'Light Rain with Thunder,thunshowers.png',
    '991' : 'Light Drizzle,lshowers.png',
    '992' : 'Mist,fog.png',
    '993' : 'Smoke,fog.png',
    '994' : 'Haze,fog.png',
    '995' : 'Light Snow Shower,flurries.png',
    '996' : 'Light Snow Shower/ Windy,flurries.png',
    '997' : 'Clear,fair.png',
    '998' : 'A Few Clouds,pcloudy.png',
    '999' : 'Fair,fair.png' }

    def get_icon(self, id):
        """
        Get icon according to id
        """
        if self._types.has_key(id):
            id = self._types[id].split(',')[1]

        return id
        
    	