import os
from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from database import init_db, get_session
from auth import verify_google_token
import crud, schemas

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL").rstrip("/") + "/"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET = "drive"

app = FastAPI(title="E2EE Drive Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://e2ee-drive.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()


# ---------- FOLDERS ----------
@app.post("/folders", response_model=schemas.FolderRead)
def create_folder(payload: schemas.FolderCreate, user=Depends(verify_google_token), session: Session = Depends(get_session)):
    return crud.create_folder(session, payload.name, payload.parent_id, user["user_id"])


@app.get("/folders")
def list_folders(parent_id: int | None = None, user=Depends(verify_google_token), session: Session = Depends(get_session)):
    folders = crud.list_folders(session, user["user_id"], parent_id)
    path = crud.get_parent_chain(session, parent_id) if parent_id else []
    files = crud.list_files(session, user["user_id"], parent_id)

    return {
        "folders": folders,
        "files": [{"name": f.name, "meta": f.meta} for f in files],
        "path": path
    }


# ---------- FILE UPLOAD ----------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_id: str = Form(None),
    meta: str = Form(...),
    user=Depends(verify_google_token),
    session: Session = Depends(get_session)
):
    user_id = user["user_id"]
    db_folder = None if folder_id in (None, "root") else int(folder_id)
    storage_folder = folder_id or "root"

    path = f"{user_id}/{storage_folder}/{file.filename}"

    content = await file.read()
    try:
        supabase.storage.from_(BUCKET).remove([path])
    except Exception:
        pass

    supabase.storage.from_(BUCKET).upload(path, content)
    crud.create_or_replace_file(session, user_id, db_folder, file.filename, meta)

    return {"message": "OK"}


# ---------- FILE DOWNLOAD ----------
@app.get("/download/{folder_id}/{filename}")
def download_file(folder_id: str, filename: str, user=Depends(verify_google_token)):
    path = f"{user['user_id']}/{folder_id or 'root'}/{filename}"
    signed = supabase.storage.from_(BUCKET).create_signed_url(path, 3600)
    return {"url": signed["signedURL"]}


# ---------- FILE DELETE ----------
@app.delete("/delete/{folder_id}/{filename}")
def delete_file(folder_id: str, filename: str, user=Depends(verify_google_token), session: Session = Depends(get_session)):
    db_folder = None if folder_id == "root" else int(folder_id)
    path = f"{user['user_id']}/{folder_id}/{filename}"

    supabase.storage.from_(BUCKET).remove([path])
    crud.delete_file(session, user["user_id"], db_folder, filename)
    return {"message": "Deleted"}


# ---------- FILE RENAME ----------
@app.post("/rename/{folder_id}/{filename}")
def rename_file(folder_id: str, filename: str, body: dict, user=Depends(verify_google_token), session: Session = Depends(get_session)):
    new = body["new_name"]
    db_folder = None if folder_id == "root" else int(folder_id)

    old_path = f"{user['user_id']}/{folder_id}/{filename}"
    new_path = f"{user['user_id']}/{folder_id}/{new}"

    data = supabase.storage.from_(BUCKET).download(old_path)
    supabase.storage.from_(BUCKET).upload(new_path, data)
    supabase.storage.from_(BUCKET).remove([old_path])

    crud.rename_file(session, user["user_id"], db_folder, filename, new)
    return {"message": "Renamed"}


# ---------- FOLDER DELETE ----------
@app.delete("/folder/{folder_id}")
def delete_folder(folder_id: int, user=Depends(verify_google_token), session: Session = Depends(get_session)):
    crud.delete_folder(session, folder_id, user["user_id"])
    prefix = f"{user['user_id']}/{folder_id}"

    items = supabase.storage.from_(BUCKET).list(prefix)
    if items:
        supabase.storage.from_(BUCKET).remove([f"{prefix}/{i['name']}" for i in items])

    return {"message": "Folder deleted"}


# ---------- FOLDER RENAME ----------
@app.post("/folder/{folder_id}/rename")
def rename_folder(
    folder_id: int,
    body: dict,
    user=Depends(verify_google_token),
    session: Session = Depends(get_session)
):
    folder = crud.get_folder(session, folder_id, user["user_id"])
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    folder.name = body["new_name"]
    session.add(folder)
    session.commit()
    session.refresh(folder)

    return {"message": "Renamed", "new_name": body["new_name"]}
