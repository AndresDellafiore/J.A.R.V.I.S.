import sys
from pathlib import Path
from backend.core.voice_engine import VoiceEngine
from backend.modules.weather import WeatherModule

def main():
    try:
        print("=== Iniciando J.A.R.V.I.S ===")
        voice = VoiceEngine()
        weather = WeatherModule(api_key="TU_API_KEY")  # Reemplaza con tu key
        
        voice.speak("Sistema listo. Di 'hola JARVIS' para comenzar.")
        
        while True:
            command = voice.listen()
            if not command:
                continue
                
            if "hola jarvis" in command:
                voice.speak("¿En qué puedo ayudarte?")
            elif "clima" in command:
                city = "Buenos Aires"  # Puedes extraer la ciudad del comando luego
                response = weather.get_weather(city)
                voice.speak(response)
                
    except KeyboardInterrupt:
        print("\n=== Sistema detenido ===")
    except Exception as e:
        print(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    main()