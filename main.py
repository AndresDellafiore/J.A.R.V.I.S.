import speech_recognition as sr
import pyttsx3
import threading
import time
import json
import os
import random
from JARVIS.modules.weather import WeatherModule
from JARVIS.modules.news import NewsModule
from JARVIS.modules.system import SystemModule
from JARVIS.modules.spotify import SpotifyModule
from jarvis_gui import JARVISGUI
from config import load_config
from user_manager import UserManager


class JARVISResponses:
    @staticmethod
    def greeting(user_name="señor"):
        greetings = [
            f"Buenos días {user_name}, ¿en qué puedo ayudarle hoy?",
            f"Buenos días {user_name}, sistemas operativos al 100%",
            f"{user_name}, todos los sistemas están listos",
            f"Buenos días, {user_name}. ¿Cómo puedo asistirle?"
        ]
        return random.choice(greetings)
    
    @staticmethod
    def acknowledgment(user_name="señor"):
        acknowledgments = [
            f"Sí, {user_name}. Dígame",
            f"A sus órdenes, {user_name}",
            f"Escuchándole, {user_name}",
            f"Procediendo, {user_name}"
        ]
        return random.choice(acknowledgments)
    
    @staticmethod
    def confirmation(user_name="señor"):
        confirmations = [
            f"{user_name}, ya estoy en eso",
            f"De inmediato, {user_name}",
            f"Procesando su solicitud, {user_name}",
            f"Ejecutando ahora, {user_name}"
        ]
        return random.choice(confirmations)
    
    @staticmethod
    def gratitude_response(user_name="señor"):
        responses = [
            f"Gracias, {user_name}",
            f"Es un placer servirle, {user_name}",
            f"A su servicio, {user_name}",
            f"Siempre a sus órdenes, {user_name}"
        ]
        return random.choice(responses)

class JARVIS:
    def __init__(self):
        self.config = load_config()
        self.running = True
        self.microphone = sr.Microphone()
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', 'spanish-latin-am')
        self.user_manager = UserManager()
        
        # Inicialización de módulos con manejo de errores
        try:
            self.weather_module = WeatherModule(self.config.get('weather_api_key', ''))
            self.news_module = NewsModule(self.config.get('news_api_key', ''))
            self.system_module = SystemModule()
            self.spotify_module = SpotifyModule()
        except Exception as e:
            print(f"Error inicializando módulos: {e}")
            self.speak("Algunos módulos no funcionarán correctamente")

        self.gui = JARVISGUI(self)
        self.setup_user()
        self.start_listener()

    def setup_user(self):
        """Configura el usuario actual con manejo de errores"""
        try:
            if not self.user_manager.identify_user(self.microphone):
                self.speak("No he podido identificarlo. ¿Podría decirme su nombre?")
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5)
                    name = self.recognizer.recognize_google(audio, language="es-ES")
                    if self.user_manager.register_user(name):
                        self.speak(f"Mucho gusto, {name}. Quedaré registrado para la próxima.")
        except Exception as e:
            print(f"Error en setup_user: {e}")
            self.speak("Continuaré en modo invitado")

    def start_listener(self):
        """Inicia el hilo de escucha de manera segura"""
        self.listener_thread = threading.Thread(target=self.listen, daemon=True)
        self.listener_thread.start()
        self.speak(JARVISResponses.greeting(self.get_user_name()))

    def get_user_name(self):
        """Obtiene el nombre del usuario actual"""
        user = self.user_manager.get_current_user()
        return user['name'] if user else "señor"

    def speak(self, text):
        """Sintetiza voz con manejo de errores"""
        try:
            self.gui.update_display(f"JARVIS: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error en speak: {e}")

    def listen(self):
        """Escucha continua con manejo robusto de errores"""
        while self.running:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.gui.update_status("Escuchando...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                self.process_audio(audio)
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Error en listen: {e}")
                time.sleep(1)

    def process_audio(self, audio):
        """Procesa el audio capturado"""
        try:
            text = self.recognizer.recognize_google(audio, language="es-ES").lower()
            self.gui.update_display(f"Usuario: {text}")
            self.process_command(text)
        except sr.UnknownValueError:
            self.gui.update_status("No te entendí")
        except sr.RequestError as e:
            self.gui.update_status(f"Error en servicio de voz: {e}")

    def process_command(self, command):
        """Procesa comandos con respuestas personalizadas"""
        user_name = self.get_user_name()
        
        if any(word in command for word in ["hola", "buenos días", "buenas tardes"]):
            self.speak(JARVISResponses.greeting(user_name))
        
        elif any(word in command for word in ["jarvis", "oye", "escucha"]):
            self.speak(JARVISResponses.acknowledgment(user_name))
        
        elif "clima" in command or "tiempo" in command:
            self.process_weather_command(user_name)
        
        elif "noticias" in command:
            self.process_news_command(user_name)
        
        elif any(word in command for word in ["reproducir", "pon", "música"]):
            self.process_spotify_command("play", user_name)
        
        elif any(word in command for word in ["detener", "para", "detén"]):
            self.process_spotify_command("stop", user_name)
        
        elif any(word in command for word in ["gracias", "agradezco"]):
            self.speak(JARVISResponses.gratitude_response(user_name))
        
        elif "apagar" in command or "salir" in command:
            self.shutdown()
        
        else:
            self.speak(f"No he entendido esa orden, {user_name}. ¿Podría repetirla?")

    def process_weather_command(self, user_name):
        """Procesa comando del clima"""
        self.speak(JARVISResponses.confirmation(user_name))
        try:
            weather_info = self.weather_module.get_weather("Buenos Aires")
            self.speak(f"El clima en Buenos Aires es {weather_info}")
        except Exception as e:
            print(f"Error en weather: {e}")
            self.speak("No pude obtener información del clima")

    def process_news_command(self, user_name):
        """Procesa comando de noticias"""
        self.speak(JARVISResponses.confirmation(user_name))
        try:
            news = self.news_module.get_news()
            self.speak(f"Estas son las noticias más recientes: {news[0]['title']}")
        except Exception as e:
            print(f"Error en news: {e}")
            self.speak("No pude obtener las noticias")

    def process_spotify_command(self, action, user_name):
        """Procesa comandos de Spotify"""
        self.speak(JARVISResponses.confirmation(user_name))
        try:
            if action == "play":
                self.spotify_module.play()
                self.speak("Reproduciendo música en Spotify")
            else:
                self.spotify_module.stop()
                self.speak("Música detenida")
        except Exception as e:
            print(f"Error en spotify: {e}")
            self.speak("No pude controlar Spotify")

    def shutdown(self):
        """Apaga el sistema de manera controlada"""
        user_name = self.get_user_name()
        self.speak(f"Hasta luego, {user_name}. Sistemas en modo de espera")
        self.running = False
        self.gui.root.quit()
        if hasattr(self, 'listener_thread') and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)
        os._exit(0)

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.gui.root.mainloop()