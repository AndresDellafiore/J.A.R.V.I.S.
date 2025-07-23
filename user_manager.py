import os
import json
import speech_recognition as sr
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.recognizer = sr.Recognizer()
        
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f)

    def register_user(self, name, voice_sample_path=None):
        """Registra un nuevo usuario"""
        with open(self.users_file, 'r+') as f:
            data = json.load(f)
            
            if any(user['name'].lower() == name.lower() for user in data['users']):
                return False
            
            new_user = {
                "name": name,
                "voice_sample": voice_sample_path,
                "register_date": str(datetime.now()),
                "preferences": {}
            }
            
            data['users'].append(new_user)
            f.seek(0)
            json.dump(data, f, indent=4)
        return True

    def identify_user(self, audio_source):
        """Intenta identificar al usuario por voz"""
        try:
            print("Por favor diga su nombre para identificarse...")
            audio = self.recognizer.listen(audio_source, timeout=5)
            name = self.recognizer.recognize_google(audio, language="es-ES")
            
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                for user in data['users']:
                    if user['name'].lower() in name.lower():
                        self.current_user = user
                        return True
            return False
            
        except Exception as e:
            print(f"Error en identificación: {e}")
            return False

    def get_current_user(self):
        """Devuelve el usuario actual"""
        return self.current_user

    def set_current_user(self, name):
        """Establece el usuario actual por nombre"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            for user in data['users']:
                if user['name'].lower() == name.lower():
                    self.current_user = user
                    return True
        return False