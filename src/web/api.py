@"
from fastapi import FastAPI

app = FastAPI(title="J.A.R.V.I.S. API")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a J.A.R.V.I.S."}

@app.post("/ask")
async def ask_question(prompt: str):
    # Aquí integrarás con Ollama después
    return {"response": f"Recibí tu pregunta: {prompt}"}
"@ | Out-File -FilePath src\web\api.py -Encoding utf8