import requests
import json
from abc import ABC
from dataclasses import dataclass
import datetime
from io import BytesIO
import os
from typing import Union



class OneCallData:
    '''Class storing all OneCall weather info'''
    
    def __init__(self, lat, lon, timezone, timezone_offset, current, minutely, hourly, daily, alerts):
        self.lat = lat
        self.lon = lon
        self.timezone = timezone
        self.timezone_offset = timezone_offset

        self.current = current
        self.minutely = minutely
        self.hourly = hourly
        self.daily = daily
        self.alerts = alerts

    # Instantiate a class by the dict
    @classmethod
    def from_dict(cls, the_dict):
        '''Creates OneCallData object based on the given dict'''

        return cls(
            lat=the_dict.get('lat', None),
            lon=the_dict.get('lon', None),
            timezone=the_dict.get('timezone', None),
            timezone_offset=the_dict.get('timezone_offset', None),
            current=CurrentWeatherData.from_dict(the_dict.get('current', {})),
            minutely=[MinutelyWeatherData.from_dict(item) for item in the_dict.get('minutely', {})],
            hourly=[HourlyWeatherData.from_dict(item) for item in the_dict.get('hourly', {})],
            daily=[DailyWeatherData.from_dict(item) for item in the_dict.get('daily', {})],
            alerts=[AlertsWeatherData.from_dict(item) for item in the_dict.get('alerts', {})],
            #alerts=AlertsWeatherData.from_dict(the_dict.get('alerts', {})),
        )


class OpenWeather:
    '''
    Weather manager class
    In objects of this class there are configured basic parameters as location, API key, units or language
    '''

    def __init__(self, api_key: str, units: str, language: str, lat:Union[str, float]=None, lon:Union[str, float]=None):
        self.api_key = api_key
        self.units = units
        self.lang = language
        self.lat = str(lat)
        self.lon = str(lon)


    # Get one-call weather data from API (current, 48h forecast)
    def get_weather(self, latitude:Union[str, float]=None, longitude:Union[str, float]=None) -> OneCallData:
        '''Returns OneCallData object with all weather info'''

        if (latitude is None or longitude is None) and (self.lat is None or self.lon is None):
            raise AttributeError("No lat/lon passed as an argument nor defined in properties.")
        latitude = latitude or self.lat
        longitude = longitude or self.lon
        if latitude is not None: latitude = str(latitude)
        if longitude is not None: longitude = str(longitude)

        req = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&appid={self.api_key}&units={self.units}")
        return OneCallData.from_dict(json.loads(req.content))
    

@dataclass
class WeatherData(ABC):
    '''WeatherData Abstract Base Class for all kind of weather data from OpenWeather API'''

    @classmethod
    def from_dict(cls, the_dict):

        # Searches the_dict for values for every class field
        fields = {}
        for field in cls.__dict__['__dataclass_fields__']:
            if field == "weather":
                fields[field] = Weather.from_dict(the_dict.get(field, [{}])[0])
            else:
                fields[field] = the_dict.get(field, None)

        return cls(**fields)

    @staticmethod
    def _timestamp_to_dt(timestamp:int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp)
    
    
@dataclass
class Weather(WeatherData):
    '''Weather class stores weather description from OpenWeather API'''

    id:str
    main:str
    description:str
    icon:str

    @property
    def icon_url(self) -> str:
        '''Returns URL for the icon'''

        #return f'https://openweathermap.org/img/w/{self.icon}.png'   # old icons, worse resolution
        return f'https://openweathermap.org/img/wn/{self.icon}@2x.png' # new icons, better resolution, simpler design
    
    def get_icon_image(self, save=False) -> BytesIO:
        '''Returns icon image'''

        # Check if local file exists
        local_path = f'./images/new/{self.icon}.png'
        if os.path.exists(local_path):
            return open(local_path, 'rb')
        else:
        # Get from web
            req = requests.get(self.icon_url)
            if save:
                with open(local_path, 'wb') as new_file:
                    new_file.write(req.content)
            return BytesIO(req.content)


@dataclass
class HourlyWeatherData(WeatherData):
    '''HourlyWeatherData class stores hourly weather forecast'''

    dt: int
    temp: Union[int, float, dict]
    feels_like: Union[str, dict]
    pressure: Union[int, float]
    humidity: Union[int, float]
    dew_point: Union[int, float]
    uvi: Union[int, float]
    clouds: Union[int, float]
    visibility: Union[int, float]
    wind_speed: Union[int, float]
    wind_deg: Union[int, float]
    wind_gust: float
    weather: Weather
    rain: float
    snow: float
    pop: Union[int, float]

    @property
    def dt_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.dt)
    
    @property
    def datetime_str(self, template:str="%d-%m-%Y %H:%M") -> str:
        return self.dt_dt.strftime(template)


@dataclass
class CurrentWeatherData(HourlyWeatherData):
    '''CurrentWeatherData class stores current weather data'''

    sunrise: int
    sunset: int

    @property
    def sunrise_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.sunrise)
    
    @property
    def sunset_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.sunset)


@dataclass
class DailyWeatherData(CurrentWeatherData):
    '''CurrentWeatherData class stores daily weather forecast data'''

    moonrise: int
    moonset: int
    moonphase: float
    pop: Union[int, float]

    @property
    def moonrise_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.moonrise)
    
    @property
    def moonset_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.moonset)


@dataclass
class MinutelyWeatherData(WeatherData):
    dt: int
    precipitation: Union[int, float]

    @property
    def dt_dt(self) -> datetime.datetime:
        return self._timestamp_to_dt(self.dt)


@dataclass
class AlertsWeatherData(WeatherData):
    '''AlertsWeatherData class stores weather alerts'''

    sender_name: str
    event: str
    start: int
    end: int
    description: str
    tags: list

