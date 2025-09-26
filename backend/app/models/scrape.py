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

class ScrapePatch(ScrapeBase):
    locator: Optional[str] = None
    metric_name: Optional[str] = None

    class Config:
        orm_mode = True


class ScrapeOut(ScrapeInDB):
    """
    Response model for PATCH and PUT operations.
    Inherits id, locator, metric_name, webpage_id from ScrapeInDB
    and adds an `updated` flag indicating whether any column was actually changed.
    """
    updated: Optional[bool] = None
    updated: bool = Field(
        default=False,
        description="True if the UPDATE modified at least one column"
    )
    