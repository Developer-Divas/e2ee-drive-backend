from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./e2ee_drive.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

def init_db():
    # IMPORTANT: import models so tables are registered
    from models import Folder, File
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
