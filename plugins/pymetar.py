# Copyright (C) 2002  Tobias Klausmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# By reading this code you agree not to ridicule the author =)

import string,urllib

class Report:

    """
    This class provides a means to download and parse 
    the decoded METAR reports from http://weather.noaa.gov
    
    In order to find the report relevant for you, find
    the closest station at 
    http://www.nws.noaa.gov/oso/siteloc.shtml and feed
    its 4-letter station code to fetch()

    All methods return metric values, no matter what the
    station provides. The conversion factors were taken 
    from the excellent "units" program.
    """

    def getreport(self):
        """
        Return the complete weather report.
        """
        return self.fullreport

    def gettemp(self):
        """
        Return the temperature in degrees Celsius.
        """
        return self.temp

    def getwindspeed(self):
        """
        Return the wind speed in meters per second.
        """
        return self.windspeed

    def getwinddir(self):
        """
        Return wind direction in degrees.
        """
        return self.winddir

    def getvis(self):
        """
        Return visibility in km. Return values of 12
        correspond to "greater than 11 km".
        """
        return self.vis

    def getdewpoint(self):
        """
        Return dewpoint in degrees Celsius.
        """
        return self.dewp

    def gethumid(self):
        """
        Return relative humidity in percent.
        """
        return self.humid
    
    def getpress(self):
        """
        Return pressure in hPa.
        """
        return self.press

    def getcode(self):
        """
        Return the encoded weather report.
        """
        return (self.code)

    def getweather(self):
        """
        Return short weather conditions
        """
        return self.weather

    def getskycond(self):
        """
        Return sky conditions
        """
        return self.sky

    def getfullname(self):
        """
        Return full station name
        """
        return self.fulln

    def getcycle(self):
        """
        Return cycle value.
        The cycle value is not the frequency or delay
        between observations but the "time slot" in
        which the observation was made. There are 24 
        cycle slots every day which usually last from
        N:45 to N+1:45. The cycle from 23:45 to 0:45
        is cycle 0.
        """
        return self.cycle

    def getwindcomp(self):
        """
        Return wind direction as compass direction
        (e.g. NE or SSE)
        """
        return self.windcomp

    def getlocpos(self):
        """
        Return latitude, longitude and height above sea level of station
        as a tuple. Some stations don't deliver height, for those,
        -1 is returned as height.
        The lat/longs are expressed as follows:
        xx-yyd
        where xx is degrees, yy minutes and d the direction.
        Thus 51-14N means 51 degrees, 14 minutes north.
        d may take the values N, S for latitues and W, E for
        longitudes.
        Height is always given as meters above sea level,
        including a trailing M.
        Schipohl Int. Airport Amsterdam has, for example:
        ('52-18N', '004-46E', '-2M')
        Moenchengladbach (where I live):
        ('51-14N', '063-03E', -1)
        """
        return self.locpos
    
    def gettime(self):
        """
        Return the time when the observation was made.
        Note that this is *not* the time when the report
        was fetched by us
        Format:  YYYY.MM.DD HHMM UTC
        Example: 2002.04.01 1020 UTC
        """
        return self.rtime

    def __init__(self):
        self.fullreport=""
        self.temp=0.0
        self.windspeed=0.0
        self.winddir=0
        self.vis=0
        self.dewp=0
        self.humid=0
        self.press=0
        self.code=""
        self.weather=""
        self.sky=""
        self.fulln=""
        self.cycle=0
        self.windcomp=""
        self.rtime="1970.01.01 0000 UTC"
        
    def fetch(self, station, baseurl="http://weather.noaa.gov/pub/data/observations/metar/decoded/"):
        """
        Retrieve the decoded METAR report from the given
        base URL and parse it.
        Fill the data properties in the class instance with
        the values found in the report, converting them to 
        metric values where necessary.
        """
        reporturl=baseurl+string.upper(station)+".TXT"
        fn=urllib.urlopen(reporturl)

        # Dump entire report in a variable and toss
        # the file descriptor.
        self.fullreport=fn.read()
        del fn

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
                    city,r=string.split(data,",",1)
                    coun,p=string.split(r,"(",1)
                except ValueError:
                    city=""
                    coun=""
                    p=data
                try:
                    id,lat,long,ht=string.split(p," ")
                except ValueError:
                    id,lat,long=string.split(p," ")
                    ht=-1
                self.fulln=city+" "+coun
                
                self.locpos=(lat,long,ht)

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
                    self.winddir=0
                    self.windcomp=""
                else:
                    f,t,comp,deg,r,d,speed,r=string.split(data," ",7)
                    self.winddir=int(deg[1:])
                    self.windcomp=string.strip(comp)
                    self.windspeed=(float(speed)*0.44704)

            # visibility
            elif (header=="Visibility"):
                if (string.find(data,"greater")!=-1):
                    self.vis=12
                else:
                    vis,c=string.split(data," ",1)
                    self.vis=float(vis)*1.609344

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


        

    
