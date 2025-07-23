import requests

class WeatherModule:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, location):
        """Obtiene el clima con manejo de errores"""
        if not self.api_key:
            return "Servicio no configurado"
            
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"{temp}°C y {description}"
            
        except requests.exceptions.RequestException as e:
            print(f"Error en weather API: {e}")
            return "No disponible"
        except Exception as e:
            print(f"Error procesando clima: {e}")
            return "Error"