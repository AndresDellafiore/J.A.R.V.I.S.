import requests
from typing import Dict, Any
from backend.core.exceptions import APIError

class WeatherModule:
    def __init__(self, api_key: str = "TU_API_KEY"):
        if api_key == "TU_API_KEY":
            raise ValueError("Debes proporcionar una API key válida de OpenWeather")
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str) -> str:
        """Obtiene el clima actual para una ciudad específica.
        
        Args:
            city: Nombre de la ciudad (ej: 'Buenos Aires')
            
        Returns:
            str: Descripción del clima en formato legible
            
        Raises:
            APIError: Si hay problemas con la API
            ValueError: Si la ciudad no existe
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # Verificar si la respuesta fue exitosa
            if response.status_code != 200:
                error_data = response.json()
                raise APIError(f"Error {response.status_code}: {error_data.get('message', 'Error desconocido')}")
                
            data: Dict[str, Any] = response.json()
            
            # Extraer datos con validación
            if 'main' not in data or 'weather' not in data:
                raise APIError("Datos de clima incompletos en la respuesta")
                
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            
            return (f"El clima en {city}: {desc.capitalize()}, "
                    f"{temp}°C, humedad {humidity}%")
                    
        except requests.exceptions.Timeout:
            raise APIError("Tiempo de espera agotado al conectar con OpenWeather")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error de conexión: {str(e)}")
        except (KeyError, IndexError) as e:
            raise APIError(f"Datos de clima en formato incorrecto: {str(e)}")