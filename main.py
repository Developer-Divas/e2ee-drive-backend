from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from database import init_db, get_session
from auth import get_current_user, verify_google_token
from fastapi.responses import JSONResponse
import crud, schemas, os, shutil

from pydantic import BaseModel
from fastapi.responses import FileResponse

app = FastAPI(title="E2EE Drive Backend")

UPLOAD_DIR = "uploads"

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
def create_folder(payload: schemas.FolderCreate, 
                  user_id: str = Depends(get_current_user), 
                  session: Session = Depends(get_session)):

    try:
        return crud.create_folder(session, payload.name, payload.parent_id, user_id)
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


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
    
    # 3. FIX: Safe folder path creation
    folder_key = str(parent_id) if parent_id is not None else "root"
    folder_path = os.path.join("uploads", folder_key)
    os.makedirs(folder_path, exist_ok=True)

    # 4. List files in this folder
    files = []
    for fname in os.listdir(folder_path):
        size = os.path.getsize(os.path.join(folder_path, fname))
        files.append({
            "name": fname,
            "size": size,
        })

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

    folder_path = os.path.join(UPLOAD_DIR, folder_id or "root")
    os.makedirs(folder_path, exist_ok=True)

    file_location = os.path.join(folder_path, file.filename)


    # Save file
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {"message": "OK", "file": file.filename, "folder_id": folder_id}


@app.get("/download/{folder_id}/{filename}")
async def download_file(folder_id: str, filename: str, user = Depends(verify_google_token)):
    file_path = os.path.join("uploads", folder_id or "root", filename)

    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )



@app.delete("/delete/{folder_id}/{filename}")
async def delete_file(folder_id: str, filename: str, user = Depends(verify_google_token)):
    file_path = os.path.join("uploads", folder_id or "root", filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "Deleted"}

    return JSONResponse({"error": "File not found"}, status_code=404)


class RenameRequest(BaseModel):
    new_name: str

@app.post("/rename/{folder_id}/{filename}")
async def rename_file(folder_id: str, filename: str, body: RenameRequest, user = Depends(verify_google_token)):
    old_path = os.path.join("uploads", folder_id or "root", filename)
    new_path = os.path.join("uploads", folder_id or "root", body.new_name)

    if not os.path.exists(old_path):
        return JSONResponse({"error": "Old file not found"}, status_code=404)

    os.rename(old_path, new_path)
    return {"message": "Renamed", "new_name": body.new_name}


@app.delete("/folder/{folder_id}")
async def delete_folder(folder_id: int,
                        user_id: str = Depends(get_current_user),
                        session: Session = Depends(get_session)):

    # 1. Check folder exists
    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    # 2. Delete folder record
    crud.delete_folder(session, folder_id, user_id)

    # 3. Delete folder directory
    folder_path = os.path.join("uploads", str(folder_id))
    if os.path.exists(folder_path):
        import shutil
        shutil.rmtree(folder_path)

    return {"message": "Folder deleted"}


class RenameFolderRequest(BaseModel):
    new_name: str

@app.post("/folder/{folder_id}/rename")
async def rename_folder(folder_id: int,
                        body: RenameFolderRequest,
                        user_id: str = Depends(get_current_user),
                        session: Session = Depends(get_session)):

    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    folder.name = body.new_name
    session.add(folder)
    session.commit()
    session.refresh(folder)

    return {"message": "Renamed", "new_name": body.new_name}


@app.get("/folder/{folder_id}/download")
async def download_folder(folder_id: int,
                          user_id: str = Depends(get_current_user),
                          session: Session = Depends(get_session)):

    folder = crud.get_folder(session, folder_id, user_id)
    if not folder:
        return JSONResponse({"detail": "Folder not found"}, status_code=404)

    folder_path = os.path.join("uploads", str(folder_id))
    if not os.path.exists(folder_path):
        return JSONResponse({"detail": "No files in this folder"}, status_code=404)

    zip_path = f"temp/{folder_id}.zip"
    os.makedirs("temp", exist_ok=True)

    shutil.make_archive(f"temp/{folder_id}", "zip", folder_path)

    return FileResponse(zip_path, filename=f"{folder.name}.zip")
