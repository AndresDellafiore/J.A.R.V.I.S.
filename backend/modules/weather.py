"""
Módulo mejorado para obtener datos meteorológicos de OpenWeatherMap
Con manejo robusto de API keys y sistema de caché
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.core.exceptions import APIError
from dotenv import load_dotenv

class WeatherModule:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el módulo con carga segura de API key.
        
        Args:
            api_key: Opcional. Si no se provee, carga desde:
                    - Variable de entorno OPENWEATHER_API_KEY
                    - Archivo .env en la raíz del proyecto
        """
        # Configuración de rutas
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)
        
        # Carga la API key con validación estricta
        self.api_key = self._load_api_key(api_key)
        print(f"\n🔑 CLAVE CARGADA: {self.api_key[:4]}...{self.api_key[-4:]}\n")  # Debug seguro

    def _load_api_key(self, api_key: Optional[str]) -> str:
        """Carga y valida la API key desde múltiples fuentes."""
        # 1. Intenta cargar desde parámetro
        if api_key and api_key != "TU_API_KEY":
            return api_key.strip()
            
        # 2. Intenta cargar desde .env
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"📁 .env encontrado en: {env_path}")
        
        # 3. Obtiene de variables de entorno
        key_from_env = os.getenv("OPENWEATHER_API_KEY")
        if key_from_env:
            return key_from_env.strip()
            
        # 4. Fallback seguro
        raise ValueError(
            "🚨 API key no configurada\n"
            "Solución:\n"
            "1. Crea un archivo .env en la raíz del proyecto\n"
            "2. Agrega: OPENWEATHER_API_KEY=tu_clave_de_32_caracteres\n"
            f"3. Ruta esperada: {env_path}\n"
            "4. No uses comillas o espacios"
        )

    def _validate_api_key(self):
        """Valida el formato de la API key."""
        if not self.api_key or len(self.api_key.strip()) != 32:
            raise ValueError(
                f"Formato de API key inválido (longitud: {len(self.api_key)})\n"
                "Las claves de OpenWeather deben tener exactamente 32 caracteres."
            )

    def get_weather(self, city: str) -> str:
        """
        Obtiene el clima actual con manejo de errores robusto.
        
        Args:
            city: Nombre de la ciudad (ej: 'Buenos Aires')
            
        Returns:
            str: Descripción formateada del clima
            
        Raises:
            APIError: Para errores de conexión/API
        """
        # 1. Verifica caché primero
        if cached := self._get_cached_weather(city):
            return self._format_response(cached, from_cache=True)

        # 2. Parámetros de la solicitud
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es'
        }
        
        try:
            # 3. Solicitud a la API
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                headers={'User-Agent': 'JARVIS-Assistant/2.0'}
            )
            
            # 4. Manejo de errores HTTP
            if response.status_code != 200:
                error_data = response.json()
                raise APIError(f"Error {response.status_code}: {error_data.get('message', 'Sin detalles')}")
                
            # 5. Procesamiento de datos
            data = response.json()
            self._validate_weather_data(data)
            self._update_cache(city, data)
            
            return self._format_response(data)
            
        except requests.exceptions.Timeout:
            raise APIError("⌛ Tiempo de espera agotado con OpenWeather")
        except requests.exceptions.RequestException as e:
            raise APIError(f"🔌 Error de conexión: {str(e)}")
        except (KeyError, ValueError) as e:
            raise APIError(f"📉 Datos inválidos: {str(e)}")

    def _get_cached_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos del caché si están vigentes."""
        cached = self.cache.get(city.lower())
        return cached['data'] if cached and datetime.now() < cached['expires_at'] else None

    def _validate_weather_data(self, data: Dict[str, Any]):
        """Valida la estructura de los datos meteorológicos."""
        if not all(key in data for key in ('main', 'weather', 'name')):
            raise ValueError("Estructura de datos incompleta")

    def _update_cache(self, city: str, data: Dict[str, Any]):
        """Actualiza el caché con nuevos datos."""
        self.cache[city.lower()] = {
            'data': data,
            'expires_at': datetime.now() + self.cache_duration
        }

    def _format_response(self, data: Dict[str, Any], from_cache: bool = False) -> str:
        """Formatea la respuesta para el usuario."""
        cache_note = " (datos en caché)" if from_cache else ""
        return (
            f"🌤️ Clima en {data['name']}: "
            f"{data['weather'][0]['description'].capitalize()}, "
            f"{data['main']['temp']}°C, "
            f"humedad {data['main']['humidity']}%"
            f"{cache_note}"
        )