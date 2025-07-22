import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.core.exceptions import APIError

class WeatherModule:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)
        self.api_key = self._load_api_key(api_key)
        print(f"[🌦️] WeatherModule iniciado | Key: {self._mask_key(self.api_key)}")

    def _load_api_key(self, api_key: Optional[str]) -> str:
        """Carga robusta de API key"""
        # 1. Intenta desde parámetro
        if api_key and api_key != "TU_API_KEY":
            return api_key.strip()
            
        # 2. Intenta desde .env
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path, override=True)
            if key := os.getenv("OPENWEATHER_API_KEY"):
                return key.strip()
                
        # 3. Intenta desde variables del sistema
        if key := os.environ.get("OPENWEATHER_API_KEY"):
            return key.strip()
            
        raise ValueError("No se pudo cargar la API key de OpenWeather")

    def _mask_key(self, key: str) -> str:
        """Oculta parte de la clave para logs"""
        return f"{key[:4]}...{key[-4:]}" if key else "[NO KEY]"

    def get_weather(self, city: str) -> str:
        """Obtiene clima con manejo de errores mejorado"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return (
                f"Clima en {data['name']}: "
                f"{data['weather'][0]['description'].capitalize()}, "
                f"{data['main']['temp']}°C, "
                f"humedad {data['main']['humidity']}%"
            )
            
        except requests.exceptions.RequestException as e:
            return f"No pude obtener el clima. Error: {str(e)}"