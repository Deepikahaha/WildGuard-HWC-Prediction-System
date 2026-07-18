import shutil, uuid
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import client, init_db
from auth import router as auth_router
from yolo import detect
from ws_manager import manager
from risk import predict_risk

init_db()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)

@app.post("/api/detect-animal")
async def detect_animal(file: UploadFile, reported_by: str):
    path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = detect(path)
    species, confidence = result if result else ("Unknown", 0.0)

    client.execute(
        "INSERT INTO reports (species, confidence, image_path, reported_by) VALUES (?, ?, ?, ?)",
        [species, confidence, path, reported_by]
    )
    await manager.broadcast({"species": species, "confidence": confidence, "reported_by": reported_by})
    return {"species": species, "confidence": confidence}

@app.get("/api/reports")
def get_reports():
    result = client.execute("SELECT species, confidence, reported_by, created_at FROM reports ORDER BY created_at DESC")
    return [{"species": r[0], "confidence": r[1], "reported_by": r[2], "created_at": r[3]} for r in result.rows]

@app.websocket("/ws/alerts")
async def ws_alerts(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keeps connection alive
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.get("/api/predict-risk")
def risk(lat: float, lon: float):
    return predict_risk(lat, lon)

@app.get("/api/predict-risk")
def risk(lat: float, lon: float, species: str = None):
    return predict_risk(lat, lon, species)