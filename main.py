import sys
import os

# SOLUCIÓN DEFINITIVA - Configuración de paths para estructura con backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
MODULES_DIR = os.path.join(BACKEND_DIR, 'modules')

# Agregamos las rutas necesarias al path de Python
sys.path.extend([BASE_DIR, BACKEND_DIR, MODULES_DIR])

# Verificación de paths (opcional, puede eliminarse después)
print("\nRutas de búsqueda configuradas:")
for path in sys.path:
    print(f" - {path}")

# Importación robusta de módulos
try:
    from backend.modules.weather import WeatherModule
    from backend.modules.news import NewsModule
except ImportError as e:
    print(f"\nError en importación: {str(e)}")
    print("Fallando a importación alternativa...")
    try:
        from modules.weather import WeatherModule
        from modules.news import NewsModule
    except ImportError:
        print("¡No se pudo importar los módulos!")
        print("Por favor verifica que los archivos existan en:")
        print(f" - {os.path.join(MODULES_DIR, 'weather.py')}")
        print(f" - {os.path.join(MODULES_DIR, 'news.py')}")
        raise

# Resto de imports
import json
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
import random
import threading
from difflib import SequenceMatcher
from jarvis_gui import JARVISGUI

# Configuración inicial
CONFIG = {
    "nombre": "JARVIS",
    "hotword": "hola jarvis",
    "api_keys": {
        "openweather": "7246...ab1b",
        "deepseek": "tu_api_key_deepseek"
    },
    "umbral_similitud": 0.7,
    "tiempo_espera": 5,
    "modelo_ia": "deepseek-chat",
    "modo_silencioso": False,
    "usar_modulos": True
}

KNOWLEDGE_FILE = "knowledge_base.json"

class JARVIS:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)
        self.engine.setProperty('rate', 150)
        self.running = True
        self.learning_mode = False
        self.current_command = ""
        
        # Inicializar GUI
        self.gui = JARVISGUI(self)
        
        # Cargar conocimiento base
        self.knowledge_base = self.load_knowledge()
        
        # Inicializar módulos
        if CONFIG["usar_modulos"]:
            self.weather_module = WeatherModule()
            self.news_module = NewsModule()
        
        # Comandos básicos
        self.basic_commands = {
            "hola": self.respond_hello,
            "cómo estás": self.respond_status,
            "qué hora es": self.respond_time,
            "abre navegador": self.open_browser,
            "apágate": self.shutdown,
            "modo aprendizaje": self.toggle_learning,
            "busca en internet": self.search_web,
            "clima": self.weather_report,
            "noticias": self.news_report,
            "gracias": self.respond_thanks,
            "qué puedes hacer": self.list_capabilities,
            "reproduce": self.play_music,
            "dime un chiste": self.tell_joke,
            "abre la interfaz": self.show_gui,
            "minimiza la interfaz": self.hide_gui
        }
        
        self.gui.update_status("Sistema listo. Di 'hola JARVIS' para comenzar.")

    def load_knowledge(self):
        try:
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            base = {"comandos": {}, "respuestas": {}, "datos": {}}
            self.save_knowledge(base)
            return base
    
    def save_knowledge(self, data=None):
        with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data or self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def speak(self, text):
        self.gui.display_message("JARVIS", text, is_user=False)
        if not CONFIG["modo_silencioso"]:
            self.engine.say(text)
            self.engine.runAndWait()
            self.gui.animate_speech(False)
    
    def listen(self):
        with self.microphone as source:
            self.gui.update_status("Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=CONFIG["tiempo_espera"])
                command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                self.gui.display_message("Usuario", command, is_user=True)
                return command
            except sr.WaitTimeoutError:
                self.gui.update_status("Tiempo de espera agotado")
                return None
            except sr.UnknownValueError:
                self.gui.update_status("No se entendió el audio")
                return None
            except Exception as e:
                self.gui.update_status(f"Error: {str(e)}")
                return None
    
    def process_command(self, command):
        self.current_command = command
        
        if command.startswith(CONFIG["hotword"]):
            command = command.replace(CONFIG["hotword"], "").strip()
        
        if not command:
            return
        
        best_match, score = self.find_best_match(command, self.basic_commands.keys())
        
        if score > CONFIG["umbral_similitud"]:
            self.basic_commands[best_match]()
        elif command in self.knowledge_base["comandos"]:
            self.speak(self.knowledge_base["comandos"][command])
        elif self.learning_mode:
            self.learn_response(command)
        else:
            self.consult_ai(command)
    
    def find_best_match(self, command, options):
        best_match = ""
        best_score = 0.0
        
        for option in options:
            score = SequenceMatcher(None, command, option).ratio()
            if score > best_score:
                best_score = score
                best_match = option
        
        return best_match, best_score
    
    def learn_response(self, command):
        self.speak(f"No sé cómo responder a '{command}'. ¿Cómo debería responder?")
        response = self.listen()
        
        if response:
            self.knowledge_base["comandos"][command] = response
            self.save_knowledge()
            self.speak("Respuesta aprendida. Gracias por enseñarme.")
    
    def consult_ai(self, query):
        self.speak("Consultando con mi red de conocimiento...")
        
        try:
            headers = {
                "Authorization": f"Bearer {CONFIG['api_keys']['deepseek']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": CONFIG["modelo_ia"],
                "messages": [{"role": "user", "content": query}],
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                self.speak(ai_response)
                self.knowledge_base["respuestas"][query] = ai_response
                self.save_knowledge()
            else:
                self.speak("Lo siento, no pude conectar con mi red de conocimiento.")
        
        except Exception as e:
            self.speak("Estoy teniendo problemas técnicos. Por favor inténtalo más tarde.")

    def show_gui(self):
        """Muestra la interfaz gráfica"""
        self.gui.show_interface()
    
    def hide_gui(self):
        """Minimiza la interfaz gráfica"""
        self.gui.hide_interface()

    def run(self):
        """Ejecuta el bucle principal"""
        threading.Thread(target=self.gui.run, daemon=True).start()
        
        while self.running:
            command = self.listen()
            if command:
                self.process_command(command)

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.run()