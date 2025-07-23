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
    
    # ... (otros métodos actualizados para usar user_name)