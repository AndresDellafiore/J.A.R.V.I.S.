import speech_recognition as sr
import pyttsx3
import random
from typing import Optional

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        # Configuración para Windows
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)  # Cambia el índice para otra voz

    def listen(self, timeout=3, phrase_time_limit=5) -> Optional[str]:
        """Escucha con configuración mejorada para Windows"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("\n[🦻] Escuchando...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                text = self.recognizer.recognize_google(audio, language='es-ES').lower()
                print(f"[📝] Comando: {text}")
                return text
            except sr.WaitTimeoutError:
                print("[⏱️] Tiempo de espera agotado")
                return None
            except sr.UnknownValueError:
                print("[🔇] No se entendió el audio")
                return None
            except Exception as e:
                print(f"[❌] Error en reconocimiento: {str(e)}")
                return None

    def speak(self, text: str) -> None:
        """Síntesis de voz mejorada"""
        print(f"[🗣️] JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()