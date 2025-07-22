"""
Módulos de funcionalidades específicas

Actualmente incluye:
- WeatherModule: Obtención de datos meteorológicos
"""
from weather import WeatherModule

__all__ = ['WeatherModule']

# Configuración compartida para módulos
DEFAULT_CONFIG = {
    'timeout': 10,  # Tiempo máximo para operaciones
    'language': 'es'  # Idioma predeterminado
}