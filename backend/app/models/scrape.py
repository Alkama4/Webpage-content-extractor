from typing import Optional
from pydantic import BaseModel, Field

class ScrapeBase(BaseModel):
    locator: str = Field(..., max_length=512,
                         description="CSS selector or XPath")
    metric_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Optional friendly name for the metric",
    )

class ScrapeCreate(ScrapeBase):
    pass

class ScrapeInDB(ScrapeBase):
    scrape_id: int
    webpage_id: int

    class Config:
        orm_mode = True
