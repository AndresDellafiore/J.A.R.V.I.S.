class JARVISError(Exception):
    """Base para errores personalizados"""
    pass

class VoiceRecognitionError(JARVISError):
    """Falló el reconocimiento de voz"""
    pass

class APIError(JARVISError):
    """Error en APIs externas"""
    pass