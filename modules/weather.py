import requests
from typing import Dict, Any

class WeatherModule:
    def __init__(self, api_key: str = "TU_API_KEY"):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str) -> str:
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es'
        }
        try:
            response = requests.get(self.base_url, params=params)
            data: Dict[str, Any] = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"El clima en {city} es {desc} con {temp}°C"
        except Exception as e:
            return f"Error al obtener el clima: {str(e)}"