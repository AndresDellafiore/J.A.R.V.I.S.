import speech_recognition as sr
import pyttsx3
import threading
import time
import json
import os
import random
from modules.weather import WeatherModule
from modules.news import NewsModule
from modules.system import SystemModule
from modules.spotify import SpotifyModule
from jarvis_gui import JARVISGUI
from config import load_config
from user_manager import UserManager

class JARVISResponses:
    @staticmethod
    def greeting():
        greetings = [
            "Buenos días señor, ¿en qué puedo ayudarle hoy?",
            "Buenos días señor Stark, sistemas operativos al 100%",
            "Señor, todos los sistemas están listos",
            "Buenos días, señor. ¿Cómo puedo asistirle?"
        ]
        return random.choice(greetings)
    
    @staticmethod
    def acknowledgment():
        acknowledgments = [
            "Sí, señor. Dígame",
            "A sus órdenes, señor",
            "Escuchándole, señor",
            "Procediendo, señor"
        ]
        return random.choice(acknowledgments)
    
    @staticmethod
    def confirmation():
        confirmations = [
            "Señor, ya estoy en eso",
            "De inmediato, señor",
            "Procesando su solicitud, señor",
            "Ejecutando ahora, señor"
        ]
        return random.choice(confirmations)
    
    @staticmethod
    def gratitude_response():
        responses = [
            "Gracias, señor",
            "Es un placer servirle, señor",
            "A su servicio, señor",
            "Siempre a sus órdenes, señor"
        ]
        return random.choice(responses)
    
    @staticmethod
    def task_completed():
        responses = [
            "Tarea completada, señor",
            "Operación finalizada, señor",
            "Hecho, señor",
            "Solicitud cumplida, señor"
        ]
        return random.choice(responses)

#class JARVIS:
#    def __init__(self):
#        self.config = load_config()
#        self.running = True
#        self.microphone = sr.Microphone()
#        self.recognizer = sr.Recognizer()
#        self.engine = pyttsx3.init()
#        self.engine.setProperty('rate', 150)
#        self.engine.setProperty('voice', 'spanish-latin-am')
#        
#        # Inicialización de módulos
#        self.weather_module = WeatherModule(self.config['weather_api_key'])
#        self.news_module = NewsModule(self.config['news_api_key'])
#        self.system_module = SystemModule()
#        self.spotify_module = SpotifyModule()
#        
#        # Inicialización de GUI
#        self.gui = JARVISGUI(self)
#        
#        # Hilo de escucha
#        self.listener_thread = threading.Thread(target=self.listen, daemon=True)
#        self.listener_thread.start()
#        
#        # Saludo inicial
#        self.speak(JARVISResponses.greeting())
#
#    def speak(self, text):
#        """Sintetiza voz y actualiza la GUI"""
#        self.gui.update_display(f"JARVIS: {text}")
#        self.engine.say(text)
#        self.engine.runAndWait()
#
#    def listen(self):
#        """Escucha continuamente comandos de voz"""
#        while self.running:
#            try:
#                with self.microphone as source:
#                    self.recognizer.adjust_for_ambient_noise(source)
#                    self.gui.update_status("Escuchando...")
#                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
#                
#                try:
#                    text = self.recognizer.recognize_google(audio, language="es-ES").lower()
#                    self.gui.update_display(f"Usuario: {text}")
#                    self.process_command(text)
#                except sr.UnknownValueError:
#                    self.gui.update_status("No te entendí, señor")
#                except sr.RequestError as e:
#                    self.gui.update_status(f"Error en servicio de voz: {e}")
#                    
#            except Exception as e:
#                self.gui.update_status(f"Error: {str(e)}")
#                time.sleep(1)
#
#    def process_command(self, command):
#        """Procesa los comandos de voz con estilo J.A.R.V.I.S."""
#        if any(word in command for word in ["hola", "buenos días", "buenas tardes"]):
#            self.speak(JARVISResponses.greeting())
#        
#        elif any(word in command for word in ["jarvis", "oye", "escucha"]):
#            self.speak(JARVISResponses.acknowledgment())
#        
#        elif "clima" in command or "tiempo" in command:
#            self.speak(JARVISResponses.confirmation())
#            weather_info = self.weather_module.get_weather("Buenos Aires")
#            self.speak(f"El clima en Buenos Aires es {weather_info}")
#            self.speak(JARVISResponses.task_completed())
#        
#        elif "noticias" in command:
#            self.speak(JARVISResponses.confirmation())
#            news = self.news_module.get_news()
#            self.speak(f"Estas son las noticias más recientes: {news[0]['title']}")
#            self.speak(JARVISResponses.task_completed())
#        
#        elif any(word in command for word in ["reproducir", "pon", "música"]):
#            self.speak(JARVISResponses.confirmation())
#            self.spotify_module.play()
#            self.speak("Reproduciendo música en Spotify")
#        
#        elif any(word in command for word in ["detener", "para", "detén"]):
#            self.speak(JARVISResponses.confirmation())
#            self.spotify_module.stop()
#            self.speak("Música detenida")
#        
#        elif any(word in command for word in ["gracias", "agradezco"]):
#            self.speak(JARVISResponses.gratitude_response())
#        
#        elif "apagar" in command or "salir" in command:
#            self.speak("Hasta luego, señor. Sistemas en modo de espera")
#            self.shutdown()
#        
#        else:
#            self.speak("No he entendido esa orden, señor. ¿Podría repetirla?")
#
#    def shutdown(self):
#        """Apaga el sistema de manera controlada"""
#        self.running = False
#        self.gui.root.quit()
#        if self.listener_thread.is_alive():
#            self.listener_thread.join(timeout=1)
#        os._exit(0)
# Modifica la clase JARVIS
class JARVIS:
    def __init__(self):
        # ... (código existente)
        self.user_manager = UserManager()
        self.setup_user()
        
    def setup_user(self):
        """Configura el usuario actual"""
        if not self.user_manager.identify_user(self.microphone):
            self.speak("No he podido identificarlo, señor. ¿Podría decirme su nombre?")
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5)
                    name = self.recognizer.recognize_google(audio, language="es-ES")
                    if self.user_manager.register_user(name):
                        self.speak(f"Mucho gusto, {name}. Quedaré registrado para la próxima.")
                        self.user_manager.set_current_user(name)
            except Exception as e:
                print(f"Error registrando usuario: {e}")
                self.speak("Continuaré como modo invitado, señor.")

    # Modifica las respuestas para usar el nombre
    def greeting(self):
        user = self.user_manager.get_current_user()
        name = user['name'] if user else "señor"
        
        greetings = [
            f"Buenos días {name}, ¿en qué puedo ayudarle hoy?",
            f"Buenos días {name}, sistemas operativos al 100%",
            f"{name}, todos los sistemas están listos",
            f"Buenos días, {name}. ¿Cómo puedo asistirle?"
        ]
        return random.choice(greetings)
if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.gui.root.mainloop()