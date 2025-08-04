import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv()

supabase_password = os.getenv("SUPABASE_PASSWORD")

if not supabase_password:
    raise ValueError("SUPABASE_PASSWORD environment variable is not set.")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://postgres:{supabase_password}@db.tsuchnnvmfnljhxddpgs.supabase.co:5432/postgres"


engine = create_engine(SQLALCHEMY_DATABASE_URL) # สร้าง engine สำหรับเชื่อมต่อกับฐานข้อมูล
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # สร้าง session factory สำหรับทำงานกับฐานข้อมูล
Base = declarative_base() # สร้าง base class สำหรับ ORM models

try:
    with engine.connect() as connection:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Failed to connect to the database: {e}")



