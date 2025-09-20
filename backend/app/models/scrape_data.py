from pydantic import BaseModel, Field
from typing import Optional

class ScrapeData(BaseModel):
    data_id: int
    scrape_id: int
    value: Optional[float]
    datetime: str

    class Config:
        orm_mode = True
