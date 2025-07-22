#!/usr/bin/env python3
"""
Punto de entrada principal para J.A.R.V.I.S.
Controla el flujo del asistente e integra todos los módulos.
"""
import sys
from pathlib import Path
import logging
from backend import VoiceEngine, WeatherModule
from backend.core.exceptions import APIError, VoiceRecognitionError

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configura rutas y variables de entorno."""
    sys.path.append(str(Path(__file__).parent))
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv no está instalado, usando variables de entorno del sistema")

def handle_command(command: str, voice: VoiceEngine, weather: WeatherModule) -> bool:
    """
    Procesa comandos y ejecuta acciones correspondientes.
    
    Args:
        command: Comando de voz reconocido
        voice: Instancia de VoiceEngine
        weather: Instancia de WeatherModule
        
    Returns:
        bool: True si se debe continuar ejecutando, False para salir
    """
    command = command.lower().strip()
    
    if not command:
        return True
        
    if "hola jarvis" in command:
        voice.speak("¿En qué puedo ayudarte?")
        return True
        
    elif "clima" in command:
        try:
            # Extracción básica de ciudad (mejorable con NLP)
            city = "Buenos Aires"  # Por defecto
            if " en " in command:
                city = command.split(" en ")[1].split(" ")[0]
            
            response = weather.get_weather(city)
            voice.speak(response)
        except APIError as e:
            voice.speak(f"No pude obtener el clima. Error: {str(e)}")
            logger.error(f"Weather API Error: {str(e)}")
        return True
        
    elif "salir" in command or "terminar" in command:
        voice.speak("Hasta luego, señor.")
        return False
        
    else:
        voice.speak("No entendí ese comando. Prueba con 'clima' o 'salir'")
        return True

def main():
    """Función principal de ejecución."""
    setup_environment()
    
    try:
        logger.info("=== Iniciando J.A.R.V.I.S ===")
        voice = VoiceEngine()
       weather = WeatherModule()  #  API key real en archivo .env
        
        voice.speak("Sistema inicializado. Di 'Hola JARVIS' para comenzar.")
        logger.info("Sistema listo, escuchando comandos...")
        
        running = True
        while running:
            try:
                command = voice.listen()
                running = handle_command(command, voice, weather)
                
            except VoiceRecognitionError as e:
                logger.warning(f"Error en reconocimiento: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Sistema detenido por el usuario")
        voice.speak("Apagando sistema.")
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        voice.speak("Se produjo un error grave. Revisa los logs.")
    finally:
        logger.info("=== Sistema finalizado ===")

if __name__ == "__main__":
    main()