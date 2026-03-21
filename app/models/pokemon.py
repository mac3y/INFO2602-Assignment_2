from sqlmodel import SQLModel, Field
from typing import Optional

class Pokemon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    weight: float
    height: float
    image_url: Optional[str] = None
