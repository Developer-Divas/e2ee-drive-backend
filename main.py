from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from database import init_db, get_session
from auth import get_current_user, verify_google_token
from fastapi.responses import JSONResponse
import crud, schemas, os

app = FastAPI(title="E2EE Drive Backend")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@app.get("/folders")
def list_folders(parent_id: int | None = None, 
                 user_id: str = Depends(get_current_user), 
                 session: Session = Depends(get_session)):
    
    # 1. Get folders inside this folder
    folders = crud.list_folders(session, user_id, parent_id)

    # 2. Build breadcrumb path
    path = []
    if parent_id is not None:
        path = crud.get_parent_chain(session, parent_id)
        
    # Return files inside this folder
    files = []
    folder_path = "uploads"
    for fname in os.listdir(folder_path):
        files.append({"name": fname})

    return {
        "folders": folders,
        "files": files,
        "path": path
    }


@app.get("/folders/all", response_model=list[schemas.FolderRead])
def get_all_folders(user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    return crud.get_all_folders(session, user_id)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_id: str = Form(None),
    user = Depends(verify_google_token)   # <-- this verifies Google token
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"message": "OK", "file": file.filename, "folder_id": folder_id}