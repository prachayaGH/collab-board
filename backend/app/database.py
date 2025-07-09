import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

rds_password = os.getenv("RDS_PASSWORD")

if not rds_password:
    raise ValueError("RDS_PASSWORD environment variable is not set.")

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{rds_password}@collabboard.cu9iuk80kzai.us-east-1.rds.amazonaws.com:5432/CollabBoard"

engine = create_engine(SQLALCHEMY_DATABASE_URL) # สร้าง engine สำหรับเชื่อมต่อกับฐานข้อมูล
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # สร้าง session factory สำหรับทำงานกับฐานข้อมูล
Base = declarative_base() # สร้าง base class สำหรับ ORM models

try:
    with engine.connect() as connection:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Failed to connect to the database: {e}")



