"""
Núcleo del sistema J.A.R.V.I.S.

Contiene:
- VoiceEngine: Manejo de voz (reconocimiento y síntesis)
- Excepciones personalizadas
"""
from .voice_engine import VoiceEngine
from .exceptions import (
    JARVISError,
    VoiceRecognitionError,
    APIError
)

__all__ = [
    'VoiceEngine',
    'JARVISError',
    'VoiceRecognitionError',
    'APIError'
]