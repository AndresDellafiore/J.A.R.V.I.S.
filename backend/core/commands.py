"""
Diccionario de comandos y respuestas para J.A.R.V.I.S
"""
COMMAND_RESPONSES = {
    "saludo": {
        "triggers": ["hola", "buenos días", "buenas tardes"],
        "responses": [
            "¡Hola! ¿Cómo puedo ayudarte?",
            "¡Buen día! Sistema listo",
            "¡Hola humano! ¿Qué necesitas?"
        ]
    },
    "clima": {
        "triggers": ["clima", "tiempo", "temperatura"],
        "responses": [
            "Consultando el clima...",
            "Analizando condiciones meteorológicas..."
        ]
    },
    "apertura": {
        "triggers": ["abre", "inicia", "lanza"],
        "apps": {
            "chrome": "Abriendo navegador Chrome",
            "explorer": "Iniciando Explorador de archivos"
        }
    }
}

def get_response(command: str) -> Optional[str]:
    """Busca la respuesta adecuada para un comando"""
    command = command.lower()
    for category, data in COMMAND_RESPONSES.items():
        if any(trigger in command for trigger in data["triggers"]):
            if category == "apertura":
                for app, response in data["apps"].items():
                    if app in command:
                        return response
            return random.choice(data["responses"])
    return None