"""
Módulo de Clima Mejorado para Windows - J.A.R.V.I.S.
Con carga robusta de variables de entorno
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.core.exceptions import APIError

class WeatherModule:
   def __init__(self, api_key: Optional[str] = None):
    """Carga mejorada para Windows con manejo de permisos"""
    try:
        # 1. Intenta cargar desde parámetro
        if api_key and api_key != "TU_API_KEY":
            self.api_key = api_key.strip()
            return
            
        # 2. Carga desde .env con ruta absoluta
        env_path = r"C:\jarvis\.env"
        if os.path.exists(env_path):
            from dotenv import load_dotenv
            try:
                load_dotenv(dotenv_path=env_path, override=True, encoding='utf-8')
                self.api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
                if self.api_key:
                    return
            except PermissionError:
                print("⚠️ Error de permisos al leer .env")
                
        # 3. Fallback seguro
        raise ValueError(
            "No se pudo cargar OPENWEATHER_API_KEY\n"
            "Solución:\n"
            "1. Verifica que el archivo C:\jarvis\.env exista\n"
            "2. Asegúrate que contenga: OPENWEATHER_API_KEY=tu_clave\n"
            "3. Ejecuta como Admin: icacls \"C:\jarvis\.env\" /grant \"Todos:(R)\""
        )
        
    except Exception as e:
        print(f"🚨 Error crítico: {str(e)}")
        raise

    def _load_api_key(self, api_key: Optional[str]) -> str:
        """Carga la API key con validación para Windows"""
        # Intenta cargar desde parámetro
        if api_key and api_key != "TU_API_KEY":
            return api_key.strip('"\' ')
            
        # Intenta cargar desde .env (ruta absoluta para Windows)
        env_path = Path.cwd() / '.env'
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"📁 .env cargado desde: {env_path}")
            
        # Obtiene de variables de entorno
        key = os.getenv("OPENWEATHER_API_KEY")
        if not key:
            raise ValueError(
                "No se encontró OPENWEATHER_API_KEY\n"
                f"Ruta buscada: {env_path}\n"
                "Solución:\n"
                "1. Crea un archivo .env en C:\\jarvis\n"
                "2. Agrega: OPENWEATHER_API_KEY=tu_clave_sin_comillas\n"
                "3. Reinicia la terminal"
            )
        return key.strip('"\' ')

    def _mask_key(self, key: str) -> str:
        """Oculta parte de la clave para debug seguro"""
        return f"{key[:4]}...{key[-4:]}" if key else "None"

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