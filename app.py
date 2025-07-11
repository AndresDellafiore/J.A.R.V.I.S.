from flask import Flask, render_template, request, jsonify
import subprocess
from tools.memory import load_memory, save_memory
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
memory = load_memory()

def chat_with_phi(prompt, memory):
    context = "\n".join(memory[-5:])
    full_prompt = f"{context}\nUsuario: {prompt}\nAI:"
    result = subprocess.run(
        ["ollama", "run", "phi"],
        input=full_prompt.encode(),
        stdout=subprocess.PIPE
    )
    response = result.stdout.decode(errors="ignore")
    return response.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    memory.append(f"Usuario: {user_input}")
    response = chat_with_phi(user_input, memory)
    memory.append(f"AI: {response}")
    save_memory(memory)
    return jsonify({"response": response})

if __name__ == "__main__":
    #app.run(debug=True) 
    app.run(host="127.0.0.1", port=5050, debug=True)
