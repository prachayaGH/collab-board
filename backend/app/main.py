from fastapi import FastAPI
from .database import engine, Base
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import router as auth_router
import os
from dotenv import load_dotenv

load_dotenv()

# สร้าง table ถ้ายังไม่มี
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CollabBoard API",
    description="API for CollabBoard application",
    version="1.0.0"
)

# Add session middleware for OAuth flow
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://collab-board-sabv.onrender.com",
    ],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to CollabBoard backend 🎯"}

