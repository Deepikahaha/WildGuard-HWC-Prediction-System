import os, bcrypt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import jwt
from database import client

router = APIRouter()
SECRET = os.getenv("JWT_SECRET")

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def make_initials(name: str) -> str:
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()

def make_token(email: str) -> str:
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, SECRET, algorithm="HS256")

@router.post("/api/register")
def register(name: str, email: str, password: str):
    if client.execute("SELECT id FROM users WHERE email = ?", [email]).rows:
        raise HTTPException(400, "Email already registered")
    initials = make_initials(name)
    client.execute(
        "INSERT INTO users (name, email, password_hash, initials) VALUES (?, ?, ?, ?)",
        [name, email, hash_pw(password), initials]
    )
    return {"token": make_token(email), "name": name, "initials": initials}

@router.post("/api/login")
def login(email: str, password: str):
    result = client.execute("SELECT name, password_hash, initials FROM users WHERE email = ?", [email])
    if not result.rows or not verify_pw(password, result.rows[0][1]):
        raise HTTPException(401, "Invalid credentials")
    name, _, initials = result.rows[0]
    return {"token": make_token(email), "name": name, "initials": initials}

@router.get("/api/profile")
def profile(email: str):
    result = client.execute("SELECT name, email, initials FROM users WHERE email = ?", [email])
    if not result.rows:
        raise HTTPException(404, "Not found")
    name, email, initials = result.rows[0]
    return {"name": name, "email": email, "initials": initials}