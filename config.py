import os
import json

def load_config():
    """Carga la configuración con manejo robusto de errores"""
    config_file = "config.json"
    default_config = {
        "weather_api_key": "",
        "news_api_key": "",
        "spotify_client_id": "",
        "spotify_client_secret": ""
    }
    
    try:
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            
            # Validar estructura básica
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
                    
            return config
            
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return default_config

def save_config(new_config):
    """Guarda la configuración con validación"""
    try:
        with open("config.json", 'w') as f:
            json.dump(new_config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False