from pydantic import BaseModel
from typing import Optional

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class FolderRead(BaseModel):
    id: int
    name: str
    owner_id: str
    parent_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
