from core.voice_engine import VoiceEngine
from core.brain import process_command

def main():
    engine = VoiceEngine()
    engine.speak("Sistema iniciado. ¿En qué puedo ayudarte?")
    
    while True:
        command = engine.listen()
        if "hola jarvis" in command:
            response = process_command(command)
            engine.speak(response)

if __name__ == "__main__":
    main()
