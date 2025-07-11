import ollama

class OllamaManager:
    def __init__(self, model="llama3"):
        self.model = model

    def generate_response(self, prompt):
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"