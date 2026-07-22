import shutil, uuid
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import client, init_db
from auth import router as auth_router
from yolo import detect
from ws_manager import manager
from risk import predict_risk

init_db()

# One-time migration: add columns for location + risk level if they don't exist yet.
# Safe to run on every startup — ALTER TABLE fails harmlessly if the column is already there.
for col in ["lat REAL", "lon REAL", "risk_level TEXT"]:
    try:
        client.execute(f"ALTER TABLE reports ADD COLUMN {col}")
    except Exception:
        pass

# Notifications: shared across all users. Read/unread state is tracked per
# user (by email) in a separate table, so everyone sees the same notification
# list but each person's read state is their own.
client.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
client.execute("""
CREATE TABLE IF NOT EXISTS notification_reads (
    notification_id INTEGER NOT NULL,
    user_email TEXT NOT NULL,
    PRIMARY KEY (notification_id, user_email)
)
""")

def add_notification(title: str, body: str):
    client.execute("INSERT INTO notifications (title, body) VALUES (?, ?)", [title, body])

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)

@app.post("/api/detect-animal")
async def detect_animal(file: UploadFile, reported_by: str, lat: float = None, lon: float = None):
    path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = detect(path)
    species, confidence = result if result else ("Unknown", 0.0)

    risk_level = None
    if lat is not None and lon is not None:
        try:
            risk_level = predict_risk(lat, lon, species)["risk_level"]
        except Exception:
            risk_level = None  # best-effort — a bad/missing risk lookup shouldn't fail the whole detection

    client.execute(
        "INSERT INTO reports (species, confidence, image_path, reported_by, lat, lon, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [species, confidence, path, reported_by, lat, lon, risk_level]
    )
    await manager.broadcast({
        "species": species, "confidence": confidence, "reported_by": reported_by,
        "lat": lat, "lon": lon, "risk_level": risk_level
    })
    add_notification(
        f"New detection: {species}",
        f"Reported by {reported_by} at {round(confidence * 100)}% confidence" + (f" — {risk_level} risk." if risk_level else ".")
    )
    return {"species": species, "confidence": confidence, "lat": lat, "lon": lon, "risk_level": risk_level}

@app.get("/api/reports")
def get_reports():
    result = client.execute(
        "SELECT species, confidence, reported_by, created_at, lat, lon, risk_level FROM reports ORDER BY created_at DESC"
    )
    return [
        {"species": r[0], "confidence": r[1], "reported_by": r[2], "created_at": r[3],
         "lat": r[4], "lon": r[5], "risk_level": r[6]}
        for r in result.rows
    ]

@app.websocket("/ws/alerts")
async def ws_alerts(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keeps connection alive
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.get("/api/predict-risk")
def risk(lat: float, lon: float, species: str = None):
    return predict_risk(lat, lon, species)

@app.post("/api/notifications")
def create_notification(title: str, body: str = ""):
    add_notification(title, body)
    return {"ok": True}

@app.get("/api/notifications")
def list_notifications(user_email: str, limit: int = 50):
    result = client.execute(
        """
        SELECT n.id, n.title, n.body, n.created_at,
               CASE WHEN r.user_email IS NULL THEN 0 ELSE 1 END AS is_read
        FROM notifications n
        LEFT JOIN notification_reads r
          ON r.notification_id = n.id AND r.user_email = ?
        ORDER BY n.created_at DESC
        LIMIT ?
        """,
        [user_email, limit]
    )
    return [
        {"id": row[0], "title": row[1], "body": row[2], "created_at": row[3], "read": bool(row[4])}
        for row in result.rows
    ]

@app.post("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user_email: str):
    client.execute(
        "INSERT OR IGNORE INTO notification_reads (notification_id, user_email) VALUES (?, ?)",
        [notification_id, user_email]
    )
    return {"ok": True}

@app.post("/api/notifications/read-all")
def mark_all_notifications_read(user_email: str):
    client.execute(
        "INSERT OR IGNORE INTO notification_reads (notification_id, user_email) SELECT id, ? FROM notifications",
        [user_email]
    )
    return {"ok": True}
