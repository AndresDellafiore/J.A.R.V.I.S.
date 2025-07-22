import os
import json
import speech_recognition as sr
import pyttsx3
import openai
import datetime
import webbrowser
import requests
import random
from time import sleep
from threading import Thread
from difflib import SequenceMatcher
from modules.weather import WeatherModule
from modules.news import NewsModule

# Configuración inicial
CONFIG = {
    "nombre": "JARVIS",
    "hotword": "hola jarvis",
    "api_keys": {
        "openweather": "7246...ab1b",  # Mantén tu API key actual
        "deepseek": "tu_api_key_deepseek"  # Reemplaza con tu API key
    },
    "umbral_similitud": 0.7,
    "tiempo_espera": 5,
    "modelo_ia": "deepseek-chat",
    "modo_silencioso": False,
    "usar_modulos": True
}

# Base de conocimiento local
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
            "dime un chiste": self.tell_joke
        }
        
        print("=== Iniciando J.A.R.V.I.S ===")
        print(f"[🌦️] WeatherModule iniciado | Key: {CONFIG['api_keys']['openweather'][:4]}...{CONFIG['api_keys']['openweather'][-4:]}")
        self.speak("Sistema listo. Di 'hola JARVIS' para comenzar.")

    def load_knowledge(self):
        """Carga el conocimiento base desde archivo"""
        try:
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            base = {
                "comandos": {},
                "respuestas": {},
                "datos": {}
            }
            self.save_knowledge(base)
            return base
    
    def save_knowledge(self, data=None):
        """Guarda el conocimiento base en archivo"""
        with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data or self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def speak(self, text):
        """Habla el texto proporcionado"""
        print(f"[🗣️] {CONFIG['nombre']}: {text}")
        if not CONFIG["modo_silencioso"]:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def listen(self):
        """Escucha y reconoce comandos de voz"""
        with self.microphone as source:
            print("[🦻] Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=CONFIG["tiempo_espera"])
                command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"[📝] Comando: {command}")
                return command
            except sr.WaitTimeoutError:
                print("[⏱️] Tiempo de espera agotado")
                return None
            except sr.UnknownValueError:
                print("[🔇] No se entendió el audio")
                return None
            except Exception as e:
                print(f"[❌] Error: {str(e)}")
                return None
    
    def process_command(self, command):
        """Procesa el comando recibido"""
        self.current_command = command
        
        # Verificar si es la hotword
        if command.startswith(CONFIG["hotword"]):
            command = command.replace(CONFIG["hotword"], "").strip()
        
        if not command:
            return
        
        # Buscar comando más similar
        best_match, score = self.find_best_match(command, self.basic_commands.keys())
        
        if score > CONFIG["umbral_similitud"]:
            self.basic_commands[best_match]()
        elif command in self.knowledge_base["comandos"]:
            response = self.knowledge_base["comandos"][command]
            self.speak(response)
        elif self.learning_mode:
            self.learn_response(command)
        else:
            self.consult_ai(command)
    
    def find_best_match(self, command, options):
        """Encuentra la mejor coincidencia para el comando"""
        best_match = ""
        best_score = 0.0
        
        for option in options:
            score = SequenceMatcher(None, command, option).ratio()
            if score > best_score:
                best_score = score
                best_match = option
        
        return best_match, best_score
    
    def learn_response(self, command):
        """Aprende una nueva respuesta para un comando"""
        self.speak(f"No sé cómo responder a '{command}'. ¿Cómo debería responder?")
        response = self.listen()
        
        if response:
            self.knowledge_base["comandos"][command] = response
            self.save_knowledge()
            self.speak("Respuesta aprendida. Gracias por enseñarme.")
    
    def consult_ai(self, query):
        """Consulta a una IA externa (DeepSeek)"""
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
                
                # Almacenar localmente
                self.knowledge_base["respuestas"][query] = ai_response
                self.save_knowledge()
            else:
                self.speak("Lo siento, no pude conectar con mi red de conocimiento. Inténtalo más tarde.")
        
        except Exception as e:
            print(f"[❌] Error al conectar con IA: {str(e)}")
            self.speak("Estoy teniendo problemas técnicos. Por favor inténtalo más tarde.")
    
    def respond_hello(self):
        """Responde al saludo"""
        responses = [
            "Hola, ¿en qué puedo ayudarte?",
            "¡Hola! Listo para servirte.",
            "Hola, soy JARVIS. ¿Cómo puedo asistirte hoy?"
        ]
        self.speak(random.choice(responses))
    
    def respond_status(self):
        """Responde sobre su estado"""
        self.speak("Funcionando al 100% de mi capacidad. ¿En qué puedo ayudarte?")
    
    def respond_time(self):
        """Da la hora actual"""
        now = datetime.datetime.now()
        self.speak(f"Son las {now.hour} horas y {now.minute} minutos")
    
    def open_browser(self):
        """Abre el navegador web"""
        self.speak("Abriendo navegador")
        webbrowser.open("https://www.google.com")
    
    def shutdown(self):
        """Apaga el sistema"""
        self.speak("Apagando sistema. Hasta luego.")
        self.running = False
    
    def toggle_learning(self):
        """Activa/desactiva el modo aprendizaje"""
        self.learning_mode = not self.learning_mode
        status = "activado" if self.learning_mode else "desactivado"
        self.speak(f"Modo aprendizaje {status}")
    
    def search_web(self):
        """Busca en internet"""
        if "busca en internet" in self.current_command:
            query = self.current_command.replace("busca en internet", "").strip()
        else:
            self.speak("¿Qué deseas que busque en internet?")
            query = self.listen()
        
        if query:
            self.speak(f"Buscando {query} en internet")
            webbrowser.open(f"https://www.google.com/search?q={query}")
    
    def weather_report(self):
        """Proporciona el reporte del clima"""
        if CONFIG["usar_modulos"]:
            self.speak(self.weather_module.get_weather())
        else:
            self.speak("El módulo de clima no está disponible en este momento")
    
    def news_report(self):
        """Proporciona las noticias"""
        if CONFIG["usar_modulos"]:
            self.speak(self.news_module.get_news())
        else:
            self.speak("El módulo de noticias no está disponible en este momento")
    
    def respond_thanks(self):
        """Responde a agradecimientos"""
        self.speak("De nada. Siempre estoy aquí para ayudar.")
    
    def list_capabilities(self):
        """Enumera las capacidades del sistema"""
        capabilities = [
            "Puedo responder preguntas",
            "Buscar información en internet",
            "Decirte la hora y fecha",
            "Darte el reporte del clima",
            "Contarte las últimas noticias",
            "Aprender nuevas cosas que me enseñes",
            "Contar chistes",
            "Reproducir música en YouTube",
            "Y mucho más. Pregúntame lo que necesites!"
        ]
        self.speak("Mis capacidades incluyen: " + ". ".join(capabilities))
    
    def play_music(self):
        """Reproduce música en YouTube"""
        if "reproduce" in self.current_command:
            song = self.current_command.replace("reproduce", "").strip()
        else:
            self.speak("¿Qué canción te gustaría escuchar?")
            song = self.listen()
        
        if song:
            self.speak(f"Reproduciendo {song} en YouTube")
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
    
    def tell_joke(self):
        """Cuenta un chiste"""
        jokes = [
            "¿Qué le dice un gusano a otro gusano? Voy a dar una vuelta a la manzana.",
            "¿Cómo se despiden los químicos? Ácido un placer.",
            "¿Qué le dice una iguana a su hermana gemela? Somos iguanitas.",
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter."
        ]
        self.speak(random.choice(jokes))
    
    def run(self):
        """Ejecuta el bucle principal del asistente"""
        while self.running:
            command = self.listen()
            if command:
                self.process_command(command)

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.run()