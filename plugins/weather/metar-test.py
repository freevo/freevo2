import pymetar

weather = pymetar.MetarReport()
weather.fetchMetarReport('CYYZ')
print weather.getTime()
print weather.getWeather()

