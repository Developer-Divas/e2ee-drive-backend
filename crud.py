from sqlmodel import Session, select
from typing import List
from models import Folder, File
from schemas import FolderRead


# ---------- FOLDERS ----------
def create_folder(session: Session, name: str, parent_id: int | None, user_id: str):
    existing = session.exec(
        select(Folder).where(
            Folder.owner_id == user_id,
            Folder.parent_id == parent_id,
            Folder.name == name
        )
    ).first()

    if existing:
        raise ValueError("Folder with this name already exists.")

    folder = Folder(name=name, parent_id=parent_id, owner_id=user_id)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


def list_folders(session, user_id: str, parent_id: int | None):
    q = select(Folder).where(Folder.owner_id == user_id)
    q = q.where(Folder.parent_id == parent_id) if parent_id else q.where(Folder.parent_id.is_(None))
    rows = session.exec(q).all()

    result = []
    for f in rows:
        count = session.exec(
            select(Folder).where(Folder.parent_id == f.id)
        ).all()
        result.append({
            "id": f.id,
            "name": f.name,
            "owner_id": f.owner_id,
            "parent_id": f.parent_id,
            "item_count": len(count)
        })
    return result


def get_all_folders(session: Session, owner_id: str) -> List[FolderRead]:
    rows = session.exec(select(Folder).where(Folder.owner_id == owner_id)).all()
    return [FolderRead.model_validate(r, from_attributes=True) for r in rows]


def get_parent_chain(session, folder_id):
    chain = []
    current = session.get(Folder, folder_id)
    while current:
        chain.insert(0, {"id": current.id, "name": current.name})
        current = session.get(Folder, current.parent_id) if current.parent_id else None
    return chain


def get_folder(session, folder_id, user_id):
    return session.exec(
        select(Folder).where(Folder.id == folder_id, Folder.owner_id == user_id)
    ).first()


def delete_folder(session, folder_id, user_id):
    folder = get_folder(session, folder_id, user_id)
    if folder:
        session.delete(folder)
        session.commit()


# ---------- FILES ----------
def create_or_replace_file(session, owner_id, folder_id, name, meta):
    existing = session.exec(
        select(File).where(
            File.owner_id == owner_id,
            File.folder_id == folder_id,
            File.name == name
        )
    ).first()

    if existing:
        session.delete(existing)
        session.commit()

    file = File(owner_id=owner_id, folder_id=folder_id, name=name, meta=meta)
    session.add(file)
    session.commit()


def list_files(session, owner_id, folder_id):
    q = select(File).where(File.owner_id == owner_id)
    q = q.where(File.folder_id == folder_id) if folder_id else q.where(File.folder_id.is_(None))
    return session.exec(q).all()


def delete_file(session, owner_id, folder_id, name):
    file = session.exec(
        select(File).where(
            File.owner_id == owner_id,
            File.folder_id == folder_id,
            File.name == name
        )
    ).first()
    if file:
        session.delete(file)
        session.commit()


def rename_file(session, owner_id, folder_id, old, new):
    file = session.exec(
        select(File).where(
            File.owner_id == owner_id,
            File.folder_id == folder_id,
            File.name == old
        )
    ).first()
    if file:
        file.name = new
        session.add(file)
        session.commit()
