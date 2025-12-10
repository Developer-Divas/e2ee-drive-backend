from sqlmodel import Session, select
from models import Folder
from schemas import FolderCreate, FolderRead
from typing import Optional, List

def create_folder(session: Session, name: str, parent_id: int | None, user_id: str):

    # CHECK: Duplicate folder name in the same parent
    existing = session.exec(
        select(Folder).where(
            Folder.owner_id == user_id,        # FIXED
            Folder.parent_id == parent_id,
            Folder.name == name
        )
    ).first()

    if existing:
        raise ValueError("Folder with this name already exists in this location.")

    # Create new folder
    folder = Folder(name=name, parent_id=parent_id, owner_id=user_id)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


# crud.py (add/replace list_folders)
from sqlmodel import select
from models import Folder

def list_folders(session, user_id: str, parent_id: int | None):
    q = select(Folder).where(Folder.owner_id == user_id)
    if parent_id is None:
        q = q.where(Folder.parent_id.is_(None))
    else:
        q = q.where(Folder.parent_id == parent_id)

    rows = session.exec(q).all()

    # build result with item_count (number of child folders)
    result = []
    for f in rows:
        # count child folders (simple approach)
        child_q = select(Folder).where(Folder.parent_id == f.id)
        children = session.exec(child_q).all()
        item_count = len(children)

        result.append({
            "id": f.id,
            "name": f.name,
            "owner_id": f.owner_id,
            "parent_id": f.parent_id,
            "item_count": item_count
        })

    return result


def get_all_folders(session: Session, owner_id: str) -> List[FolderRead]:
    q = select(Folder).where(Folder.owner_id == owner_id)
    rows = session.exec(q).all()
    return [FolderRead.model_validate(r, from_attributes=True) for r in rows]

def get_parent_chain(session, folder_id):
    chain = []
    current = session.get(Folder, folder_id)

    while current:
        chain.insert(0, { "id": current.id, "name": current.name })
        current = session.get(Folder, current.parent_id) if current.parent_id else None

    return chain


def get_folder(session: Session, folder_id: int, user_id: str):
    return session.exec(
        select(Folder).where(Folder.id == folder_id, Folder.owner_id == user_id)
    ).first()


def delete_folder(session: Session, folder_id: int, user_id: str):
    folder = get_folder(session, folder_id, user_id)
    if folder:
        session.delete(folder)
        session.commit()
