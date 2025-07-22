"""
Paquete principal del backend de J.A.R.V.I.S.

Exporta:
- core: Funcionalidades centrales (motor de voz, excepciones)
- modules: Módulos de comandos (clima, noticias, etc.)
"""
from .core import VoiceEngine, JARVISError, VoiceRecognitionError, APIError
from .modules import WeatherModule

__all__ = [
    'VoiceEngine',
    'JARVISError',
    'VoiceRecognitionError',
    'APIError',
    'WeatherModule'
]

__version__ = '2.0.0'