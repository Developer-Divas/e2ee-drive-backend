import os
import shutil
from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlmodel import Session
from pydantic import BaseModel

from database import init_db, get_session
from auth import get_current_user, verify_google_token
import crud, schemas

import io
import zipfile
from fastapi.responses import StreamingResponse


# ---------- SUPABASE ----------
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET = "drive"

# ------------------------------
app = FastAPI(title="E2EE Drive Backend")
# ------------------------------

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


# =============================================================
#                    FOLDER CRUD (SQLite)
# =============================================================
@app.post("/folders", response_model=schemas.FolderRead)
def create_folder(
    payload: schemas.FolderCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        return crud.create_folder(session, payload.name, payload.parent_id, user_id)
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


@app.get("/folders")
def list_folders(
    parent_id: int | None = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. DB folders
    folders = crud.list_folders(session, user_id, parent_id)

    # 2. Breadcrumb
    path = crud.get_parent_chain(session, parent_id) if parent_id else []

    # 3. Supabase files
    folder_prefix = f"{user_id}/{parent_id or 'root'}"

    files_resp = supabase.storage.from_(BUCKET).list(folder_prefix)

    files = []
    for f in files_resp:
        if f["name"] == ".empty":
            continue
        metadata = f.get("metadata") or {}
        files.append({
            "name": f["name"],
            "size": metadata.get("size", 0)
        })

    return {
        "folders": folders,
        "files": files,
        "path": path
    }


@app.get("/folders/all", response_model=list[schemas.FolderRead])
def get_all_folders(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return crud.get_all_folders(session, user_id)



# =============================================================
#                       FILE UPLOAD
# =============================================================
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_id: str = Form(None),
    user=Depends(verify_google_token)
):
    user_id = user["user_id"]
    folder_key = folder_id or "root"

    storage_path = f"{user_id}/{folder_key}/{file.filename}"

    content = await file.read()

    # FIX: Remove invalid {"upsert": True}
    supabase.storage.from_(BUCKET).upload(
        storage_path,
        content
    )

    return {"message": "OK", "file": file.filename}



# =============================================================
#               FILE DOWNLOAD (SIGNED URL)
# =============================================================
@app.get("/download/{folder_id}/{filename}")
async def download_file(
    folder_id: str,
    filename: str,
    user=Depends(verify_google_token)
):
    user_id = user["user_id"]
    storage_path = f"{user_id}/{folder_id or 'root'}/{filename}"

    signed = supabase.storage.from_(BUCKET).create_signed_url(storage_path, 3600)

    return {"url": signed["signedURL"]}



# =============================================================
#                     DELETE FILE
# =============================================================
@app.delete("/delete/{folder_id}/{filename}")
async def delete_file(
    folder_id: str,
    filename: str,
    user=Depends(verify_google_token)
):
    user_id = user["user_id"]
    storage_path = f"{user_id}/{folder_id or 'root'}/{filename}"

    supabase.storage.from_(BUCKET).remove([storage_path])

    return {"message": "Deleted"}



# =============================================================
#                     RENAME FILE
# =============================================================
class RenameRequest(BaseModel):
    new_name: str


@app.post("/rename/{folder_id}/{filename}")
async def rename_file(
    folder_id: str,
    filename: str,
    body: RenameRequest,
    user=Depends(verify_google_token)
):
    user_id = user["user_id"]

    old_path = f"{user_id}/{folder_id or 'root'}/{filename}"
    new_path = f"{user_id}/{folder_id or 'root'}/{body.new_name}"

    # Download existing
    try:
        data = supabase.storage.from_(BUCKET).download(old_path)
    except Exception:
        return JSONResponse({"error": "File not found"}, status_code=404)

    # Upload new file
    supabase.storage.from_(BUCKET).upload(new_path, data)


    # Delete old
    supabase.storage.from_(BUCKET).remove([old_path])

    return {"message": "Renamed", "new_name": body.new_name}



# =============================================================
#                     FOLDER DELETE
# =============================================================
@app.delete("/folder/{folder_id}")
async def delete_folder(
    folder_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    crud.delete_folder(session, folder_id, user_id)

    prefix = f"{user_id}/{folder_id}"

    # List all objects inside folder
    items = supabase.storage.from_(BUCKET).list(prefix)

    if items:
        paths = [f"{prefix}/{i['name']}" for i in items]
        supabase.storage.from_(BUCKET).remove(paths)

    return {"message": "Folder deleted"}



# =============================================================
#                     FOLDER RENAME (DB ONLY)
# =============================================================
class RenameFolderRequest(BaseModel):
    new_name: str

@app.post("/folder/{folder_id}/rename")
async def rename_folder(
    folder_id: int,
    body: RenameFolderRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    folder.name = body.new_name
    session.add(folder)
    session.commit()
    session.refresh(folder)

    return {"message": "Renamed", "new_name": body.new_name}



# =============================================================
#            DOWNLOAD FOLDER AS ZIP (FUTURE FEATURE)
# =============================================================
@app.get("/folder/{folder_id}/download")
async def download_folder(
    folder_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    prefix = f"{user_id}/{folder_id}"

    files = supabase.storage.from_(BUCKET).list(prefix)
    if not files:
        return JSONResponse({"detail": "Folder is empty"}, status_code=400)

    import io, zipfile

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            if f["name"] == ".empty":
                continue

            file_path = f"{prefix}/{f['name']}"
            file_data = supabase.storage.from_(BUCKET).download(file_path)

            if file_data:
                zipf.writestr(f["name"], file_data)

    zip_buffer.seek(0)

    zip_filename = f"{folder.name}.zip"

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )
