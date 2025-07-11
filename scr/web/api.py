from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="J.A.R.V.I.S. Web API")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Lógica de IA aquí (ej: OllamaManager.generate_response(data))
        await websocket.send_text(f"J.A.R.V.I.S. dice: {data}")

app.mount("/", StaticFiles(directory="static"), name="static")