import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyModule:
    def __init__(self):
        self.sp = None
        self.setup_client()
        
    def setup_client(self):
        """Configura el cliente de Spotify con manejo de errores"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                scope="user-modify-playback-state",
                redirect_uri="http://localhost:8888/callback"
            ))
        except Exception as e:
            print(f"Error configurando Spotify: {e}")
            self.sp = None

    def play(self):
        """Reproduce música en Spotify"""
        if not self.sp:
            return False
            
        try:
            self.sp.start_playback()
            return True
        except Exception as e:
            print(f"Error reproduciendo en Spotify: {e}")
            return False

    def stop(self):
        """Detiene la reproducción en Spotify"""
        if not self.sp:
            return False
            
        try:
            self.sp.pause_playback()
            return True
        except Exception as e:
            print(f"Error deteniendo Spotify: {e}")
            return False