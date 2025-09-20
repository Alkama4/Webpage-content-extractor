from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class WebpageBase(BaseModel):
    url: HttpUrl = Field(..., description="The full URL that will be scraped")
    page_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Human‑readable name for the page (optional)",
    )

class WebpageCreate(WebpageBase):
    pass

class WebpageInDB(WebpageBase):
    webpage_id: int

    class Config:
        orm_mode = True
