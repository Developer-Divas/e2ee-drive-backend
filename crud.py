from sqlmodel import Session, select
from models import Folder
from schemas import FolderCreate, FolderRead
from typing import Optional, List


def create_folder(session: Session, name: str, parent_id: Optional[int], owner_id: str) -> FolderRead:
    folder = Folder(name=name, owner_id=owner_id, parent_id=parent_id)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return FolderRead.model_validate(folder, from_attributes=True)



def list_folders(session: Session, owner_id: str, parent_id: Optional[int] = None) -> List[FolderRead]:
    q = select(Folder).where(Folder.owner_id == owner_id)

    if parent_id is None:
        q = q.where(Folder.parent_id == None)
    else:
        q = q.where(Folder.parent_id == parent_id)

    rows = session.exec(q).all()
    return [FolderRead.model_validate(r, from_attributes=True) for r in rows]



def get_all_folders(session: Session, owner_id: str) -> List[FolderRead]:
    q = select(Folder).where(Folder.owner_id == owner_id)
    rows = session.exec(q).all()
    return [FolderRead.model_validate(r, from_attributes=True) for r in rows]

