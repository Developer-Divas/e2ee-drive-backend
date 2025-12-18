from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Folder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_id: str
    parent_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# 🔐 REQUIRED FOR E2EE
class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: str
    folder_id: Optional[int] = None   # NULL = root
    name: str                          # encrypted filename (.enc)
    meta: str                          # encryption metadata JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
