import openai
import os
import json
import subprocess
import speech_recognition as sr
import pyttsx3
from tools.memory import load_memory, save_memory
from tools.reader import load_text_from_folder
from dotenv import load_dotenv
from googletrans import Translator

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_") or ""

# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

# Inicializar traductor
translator = Translator()

def decir(texto):
    engine.say(texto)
    engine.runAndWait()

def escuchar():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Escuchando...")
        audio = recognizer.listen(source)
    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        print(f"Tú (voz): {texto}")
        return texto
    except sr.UnknownValueError:
        print("❓ No entendí lo que dijiste.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Error con el reconocimiento de voz: {e}")
        return ""

def traducir_a_ingles(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        return texto

def traducir_a_espanol(texto):
    try:
        return translator.translate(texto, src='en', dest='es').text
    except Exception as e:
        return texto

def buscar_con_chatgpt(pregunta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": pregunta}],
            temperature=0.7,
            max_tokens=500
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error al buscar en ChatGPT: {e}"

def chat_with_phi(prompt, memory):
    context = "\n".join(memory[-5:])
    full_prompt = f"{context}\nUsuario: {prompt}\nAI:"

    try:
        result = subprocess.run(
            ["ollama", "run", "phi"],
            input=full_prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        response = result.stdout.decode(errors="ignore").strip()
        if not response:
            raise RuntimeError("Respuesta vacía de Ollama.")
        return response
    except subprocess.TimeoutExpired:
        return "⏰ Tiempo de espera agotado al consultar a Phi."
    except Exception as e:
        return f"❌ Error al ejecutar Phi: {str(e)}"

if __name__ == "__main__":
    print("🤖 AI-Phi iniciado. Escribe 'salir' para terminar.")
    memory = load_memory()

    try:
        while True:
            modo = input("📢 ¿Usar voz? (s/n): ").strip().lower()
            if modo == "s":
                user_input = escuchar()
            else:
                user_input = input("Tú: ").strip()

            if user_input.lower() in ['salir', 'exit']:
                print("👋 Saliendo de AI-Phi...")
                break

            if user_input.lower() == "documentos":
                documentos = load_text_from_folder()
                user_input = f"Aquí hay documentos:\n{documentos[:3000]}"

            elif user_input.lower().startswith("buscar "):
                query = user_input[7:].strip()
                resultado = buscar_con_chatgpt(query)
                user_input = f"Resultado de búsqueda con ChatGPT para '{query}':\n{resultado}"

            memory.append(f"Usuario: {user_input}")

            input_english = traducir_a_ingles(user_input)
            response_english = chat_with_phi(input_english, memory)
            response = traducir_a_espanol(response_english)

            memory.append(f"AI: {response}")
            print(f"AI: {response}\n")
            decir(response)
            save_memory(memory)

    except KeyboardInterrupt:
        print("\n🛑 Interrupción por teclado. Finalizando AI-Phi...")