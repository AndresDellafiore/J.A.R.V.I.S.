import requests

class NewsModule:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"
        
    def get_news(self, country='ar', page_size=3):
        """Obtiene noticias con manejo de errores"""
        if not self.api_key:
            return [{'title': 'Servicio de noticias no configurado', 'url': '#'}]
            
        try:
            params = {
                'country': country,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return [{
                'title': article['title'],
                'url': article['url']
            } for article in data.get('articles', [])]
            
        except requests.exceptions.RequestException as e:
            print(f"Error en news API: {e}")
            return [{'title': 'No se pudieron cargar las noticias', 'url': '#'}]
        except Exception as e:
            print(f"Error procesando noticias: {e}")
            return [{'title': 'Error al obtener noticias', 'url': '#'}]