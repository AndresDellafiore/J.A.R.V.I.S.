"""
Módulo para obtener datos meteorológicos de OpenWeatherMap
Incluye manejo seguro de API keys y caché básico
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from backend.core.exceptions import APIError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class WeatherModule:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el módulo de clima.
        
        Args:
            api_key: Opcional. Si no se provee, se intentará obtener de:
                    1. Variable de entorno OPENWEATHER_API_KEY
                    2. Archivo .env
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        print(f"DEBUG - Clave cargada: {self.api_key}")  # Para verificación
        self._validate_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)  # Cache de 30 minutos

    def _validate_api_key(self):
        """Valida que la API key sea correcta."""
        if not self.api_key:
            raise ValueError(
                "OpenWeather API key no configurada. "
                "Agrega OPENWEATHER_API_KEY en .env o pásala directamente."
            )
        if len(self.api_key) != 32:  # Las keys de OpenWeather tienen 32 chars
            raise ValueError("Formato de API key inválido")

    def _get_cached_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos del caché si son recientes."""
        cached_data = self.cache.get(city.lower())
        if cached_data and datetime.now() < cached_data['expires_at']:
            return cached_data['data']
        return None

    def get_weather(self, city: str) -> str:
        """
        Obtiene el clima actual para una ciudad específica.
        
        Args:
            city: Nombre de la ciudad (ej: 'Buenos Aires')
            
        Returns:
            str: Descripción del clima en formato legible
            
        Raises:
            APIError: Si hay problemas con la API
            ValueError: Si la ciudad no existe
        """
        # Verificar caché primero
        cached = self._get_cached_weather(city)
        if cached:
            return self._format_response(cached, from_cache=True)

        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es'
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                headers={'User-Agent': 'JARVIS-Assistant/1.0'}
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise APIError(f"Error {response.status_code}: {error_data.get('message', 'Error desconocido')}")
                
            data: Dict[str, Any] = response.json()
            
            # Validar estructura de respuesta
            if not all(key in data for key in ('main', 'weather')):
                raise APIError("Datos de clima incompletos en la respuesta")
            
            # Actualizar caché
            self.cache[city.lower()] = {
                'data': data,
                'expires_at': datetime.now() + self.cache_duration
            }
            
            return self._format_response(data)
            
        except requests.exceptions.Timeout:
            raise APIError("Tiempo de espera agotado al conectar con OpenWeather")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error de conexión: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise APIError(f"Datos de clima en formato incorrecto: {str(e)}")

    def _format_response(self, data: Dict[str, Any], from_cache: bool = False) -> str:
        """Formatea la respuesta de la API para el usuario."""
        temp = data['main']['temp']
        desc = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data.get('wind', {}).get('speed', 'N/A')
        
        base_msg = (
            f"El clima en {data['name']}: {desc}, "
            f"{temp}°C, humedad {humidity}%, "
            f"viento a {wind_speed} km/h"
        )
        
        if from_cache:
            return base_msg + " (datos en caché)"
        return base_msg
