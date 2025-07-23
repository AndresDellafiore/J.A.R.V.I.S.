import os
import json
import speech_recognition as sr
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.recognizer = sr.Recognizer()
        self.initialize_users_file()

    def initialize_users_file(self):
        """Inicializa el archivo de usuarios si no existe"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f)

    def load_users(self):
        """Carga los usuarios desde el archivo"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
            return {"users": []}

    def save_users(self, data):
        """Guarda los usuarios en el archivo"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error guardando usuarios: {e}")
            return False

    def register_user(self, name, voice_sample_path=None):
        """Registra un nuevo usuario con validación"""
        if not name or not isinstance(name, str):
            return False
            
        data = self.load_users()
        
        # Verificar si el usuario ya existe
        if any(user['name'].lower() == name.lower() for user in data['users']):
            self.set_current_user(name)
            return False
        
        new_user = {
            "name": name,
            "voice_sample": voice_sample_path,
            "register_date": str(datetime.now()),
            "preferences": {}
        }
        
        data['users'].append(new_user)
        if self.save_users(data):
            self.set_current_user(name)
            return True
        return False

    def identify_user(self, audio_source):
        """Intenta identificar al usuario por voz"""
        try:
            print("Por favor diga su nombre para identificarse...")
            audio = self.recognizer.listen(audio_source, timeout=5)
            name = self.recognizer.recognize_google(audio, language="es-ES")
            
            data = self.load_users()
            for user in data['users']:
                if user['name'].lower() in name.lower():
                    self.current_user = user
                    return True
            return False
            
        except sr.UnknownValueError:
            print("No se pudo entender el nombre")
            return False
        except sr.RequestError as e:
            print(f"Error en el servicio de reconocimiento: {e}")
            return False
        except Exception as e:
            print(f"Error en identificación: {e}")
            return False

    def get_current_user(self):
        """Devuelve el usuario actual"""
        return self.current_user

    def set_current_user(self, name):
        """Establece el usuario actual por nombre"""
        if not name:
            return False
            
        data = self.load_users()
        for user in data['users']:
            if user['name'].lower() == name.lower():
                self.current_user = user
                return True
        return False

    def delete_user(self, name):
        """Elimina un usuario registrado"""
        data = self.load_users()
        data['users'] = [user for user in data['users'] if user['name'].lower() != name.lower()]
        return self.save_users(data)