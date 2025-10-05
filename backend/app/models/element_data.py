from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ElementData(BaseModel):
    data_id: int
    element_id: int
    value: Optional[float]
    created_at: datetime = Field(..., alias="created_at")

    class Config:
        orm_mode = True
