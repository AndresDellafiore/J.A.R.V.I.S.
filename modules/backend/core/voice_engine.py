import speech_recognition as sr
import pyttsx3
from typing import Optional

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidad del habla

    def listen(self) -> Optional[str]:
        """Escucha y transcribe comandos de voz."""
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio, language='es-ES')
                print(f"Comando detectado: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("No se entendió el audio")
                return None
            except sr.RequestError:
                print("Error en el servicio de voz")
                return None

    def speak(self, text: str) -> None:
        """Reproduce un texto como voz."""
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()