import pyttsx3
import speech_recognition as sr

class VoiceSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', 'english+f3')  # Ajusta la voz

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = r.listen(source, timeout=5)
            try:
                return r.recognize_google(audio, language="es-ES")
            except:
                return ""