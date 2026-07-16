import os, libsql_client
from dotenv import load_dotenv

load_dotenv()

client = libsql_client.create_client_sync(
    url=os.getenv("TURSO_DATABASE_URL").replace("libsql://", "https://"),
    auth_token=os.getenv("TURSO_AUTH_TOKEN")
)

def init_db():
    client.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, password_hash TEXT, initials TEXT)""")
    client.execute("""CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species TEXT, confidence REAL, image_path TEXT,
        reported_by TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")