import sys
import os
import importlib.util
import json
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
import random
import threading
import queue
from difflib import SequenceMatcher

# Configuración de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
MODULES_DIR = os.path.join(BACKEND_DIR, 'modules')
sys.path.extend([BASE_DIR, BACKEND_DIR, MODULES_DIR])

def dynamic_import(module_name, file_path):
    """Importación dinámica robusta"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"No se pudo encontrar el módulo en {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Carga de módulos con manejo de errores mejorado
try:
    weather_module = dynamic_import('weather', os.path.join(MODULES_DIR, 'weather.py'))
    WeatherModule = getattr(weather_module, 'WeatherModule')
    
    try:
        from backend.modules.news import NewsModule
    except ImportError:
        class NewsModule:
            def get_news(self):
                return "Módulo de noticias no disponible temporalmente"
        print("[⚠️] Usando NewsModule de respaldo")

except Exception as e:
    print(f"\nERROR: No se pudo cargar los módulos: {str(e)}")
    print("Solución:")
    print("1. Verifica que los archivos existan en backend/modules/")
    print("2. Asegúrate que las clases tengan los nombres correctos")
    print("3. Revisa que no haya errores de sintaxis en los módulos")
    input("\nPresiona Enter para salir...")
    sys.exit(1)

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
        self.gui_queue = queue.Queue()
        
        # Inicializar GUI
        self.init_gui()
        
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
        
        self.safe_gui_update("update_status", "Sistema listo. Di 'hola JARVIS' para comenzar.")

    def init_gui(self):
        """Inicializa la GUI de manera segura"""
        try:
            from jarvis_gui import JARVISGUI
            self.gui = JARVISGUI(self, self.gui_queue)
        except Exception as e:
            print(f"Error al inicializar GUI: {e}")
            class DummyGUI:
                def __init__(self, *args, **kwargs): pass
                def update_status(self, text): print(f"GUI: {text}")
                def display_message(self, sender, text, is_user=False): print(f"{sender}: {text}")
                def animate_speech(self, speaking): pass
                def show_interface(self): pass
                def hide_interface(self): pass
                def exit_program(self): pass
            self.gui = DummyGUI()

    def safe_gui_update(self, method, *args, **kwargs):
        """Actualización segura de la GUI a través de cola"""
        self.gui_queue.put((method, args, kwargs))

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
        self.safe_gui_update("display_message", "JARVIS", text, False)
        if not CONFIG["modo_silencioso"]:
            self.engine.say(text)
            self.engine.runAndWait()
            self.safe_gui_update("animate_speech", False)
    
    def listen(self):
        self.safe_gui_update("update_status", "Escuchando...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=CONFIG["tiempo_espera"])
                command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                self.safe_gui_update("display_message", "Usuario", command, True)
                return command
            except sr.WaitTimeoutError:
                self.safe_gui_update("update_status", "Tiempo de espera agotado")
                return None
            except sr.UnknownValueError:
                self.safe_gui_update("update_status", "No se entendió el audio")
                return None
            except Exception as e:
                self.safe_gui_update("update_status", f"Error: {str(e)}")
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

    # Métodos de comandos
    def respond_hello(self):
        responses = ["Hola, ¿en qué puedo ayudarte?", "¡Hola! ¿Cómo estás?", "Hola humano, soy JARVIS"]
        self.speak(random.choice(responses))

    def respond_status(self):
        statuses = ["Funcionando al 100%", "Todo en orden", "Listo para ayudarte"]
        self.speak(random.choice(statuses))

    def respond_time(self):
        now = datetime.datetime.now()
        self.speak(f"Son las {now.hour} horas con {now.minute} minutos")

    def open_browser(self):
        self.speak("Abriendo navegador web")
        webbrowser.open("https://www.google.com")

    def shutdown(self):
        self.speak("Apagando sistema. Hasta luego")
        self.running = False
        self.safe_gui_update("exit_program")

    def toggle_learning(self):
        self.learning_mode = not self.learning_mode
        status = "activado" if self.learning_mode else "desactivado"
        self.speak(f"Modo aprendizaje {status}")

    def search_web(self):
        query = self.current_command.replace("busca en internet", "").strip()
        if not query:
            self.speak("¿Qué te gustaría buscar?")
            query = self.listen()
        if query:
            self.speak(f"Buscando {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")

    def weather_report(self):
        if hasattr(self, 'weather_module'):
            self.speak(self.weather_module.get_weather("tu_ciudad"))
        else:
            self.speak("Módulo de clima no disponible")

    def news_report(self):
        if hasattr(self, 'news_module'):
            self.speak(self.news_module.get_news())
        else:
            self.speak("Módulo de noticias no disponible")

    def respond_thanks(self):
        self.speak("De nada, estoy aquí para ayudar")

    def list_capabilities(self):
        capabilities = ["Responder preguntas", "Buscar en internet", "Decir la hora"]
        self.speak("Puedo: " + ", ".join(capabilities))

    def play_music(self):
        song = self.current_command.replace("reproduce", "").strip()
        if not song:
            self.speak("¿Qué canción te gustaría escuchar?")
            song = self.listen()
        if song:
            self.speak(f"Reproduciendo {song}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

    def tell_joke(self):
        jokes = ["¿Qué le dice un semáforo a otro? No me mires, me estoy cambiando."]
        self.speak(random.choice(jokes))

    def show_gui(self):
        self.safe_gui_update("show_interface")
    
    def hide_gui(self):
        self.safe_gui_update("hide_interface")

    def run(self):
        """Ejecuta el bucle principal"""
        while self.running:
            command = self.listen()
            if command:
                self.process_command(command)

if __name__ == "__main__":
    jarvis = JARVIS()
    
    # Iniciar en un hilo separado para evitar problemas con Tkinter
    main_thread = threading.Thread(target=jarvis.run, daemon=True)
    main_thread.start()
    
    # Procesar la cola de la GUI en el hilo principal
    if hasattr(jarvis, 'gui') and hasattr(jarvis.gui, 'process_updates'):
        while getattr(jarvis, 'running', True):
            try:
                jarvis.gui.process_updates()
                jarvis.gui.root.update_idletasks()
                jarvis.gui.root.update()
            except (AttributeError, RuntimeError):
                break