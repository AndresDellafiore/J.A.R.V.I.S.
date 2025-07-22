import sys
from pathlib import Path

# Añade la ruta del backend al sistema para imports
sys.path.append(str(Path(__file__).parent / "backend"))

from core.voice_engine import VoiceEngine
from modules.weather import WeatherModule

def main():
    print("Iniciando J.A.R.V.I.S...")
    voice = VoiceEngine()
    weather = WeatherModule()
    
    voice.speak("Sistema listo")
    
    while True:
        command = voice.listen().lower()
        if "clima" in command:
            response = weather.get_weather("Buenos Aires")  # Ejemplo
            voice.speak(response)

if __name__ == "__main__":
    main()
