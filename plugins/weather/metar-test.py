import pymetar

weather = pymetar.MetarReport()
weather.fetchMetarReport('CYYZ')
print weather.getTime()
print weather.getWeather()
print weather.getTemperatureCelsius()
print weather.getPixmap() + '.png'
