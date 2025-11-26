from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from database import init_db, get_session
from auth import get_current_user
import crud, schemas

app = FastAPI(title="E2EE Drive Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/folders", response_model=schemas.FolderRead)
def create_folder(payload: schemas.FolderCreate, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    return crud.create_folder(session, payload.name, payload.parent_id, user_id)

@app.get("/folders", response_model=list[schemas.FolderRead])
def list_folders(parent_id: int | None = None, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    return crud.list_folders(session, user_id, parent_id)

@app.get("/folders/all", response_model=list[schemas.FolderRead])
def get_all_folders(user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    return crud.get_all_folders(session, user_id)
