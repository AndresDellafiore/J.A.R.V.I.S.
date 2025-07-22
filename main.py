import sys
import random
from pathlib import Path
from backend.core.voice_engine import VoiceEngine
from backend.modules.weather import WeatherModule

def main():
    try:
        print("=== Iniciando J.A.R.V.I.S ===")
        voice = VoiceEngine()
        weather = WeatherModule()
        
        voice.speak("Sistema listo. Di 'hola JARVIS' para comenzar.")
        
        while True:
            command = voice.listen()
            if not command:
                continue
                
            # Sistema de comandos mejorado
            if any(palabra in command for palabra in ["hola", "buenos días", "buenas tardes"]):
                responses = [
                    "¡Hola humano! ¿En qué puedo ayudarte?",
                    "¡Buenas! Dime tus órdenes",
                    "Sistema operativo listo"
                ]
                voice.speak(random.choice(responses))
                
            elif "clima" in command or "tiempo" in command:
                city = "Buenos Aires"  # Puedes extraer la ciudad del comando
                response = weather.get_weather(city)
                voice.speak(response)
                
            elif any(palabra in command for palabra in ["quién eres", "presentate"]):
                voice.speak("Soy JARVIS, tu asistente virtual. Versión 2.0")
                
            elif "abre" in command or "inicia" in command:
                if "chrome" in command:
                    os.startfile("chrome.exe")
                    voice.speak("Abriendo navegador Chrome")
                # Añade más apps aquí
                
            else:
                unknown_responses = [
                    "No entendí ese comando",
                    "Mis capacidades son limitadas, prueba con 'clima' o 'abrir navegador'",
                    "Reconfigura mi matriz de comandos, no entendí eso"
                ]
                voice.speak(random.choice(unknown_responses))
                
    except KeyboardInterrupt:
        print("\n=== Sistema detenido ===")
    except Exception as e:
        print(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    main()