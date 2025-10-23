from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator
from datetime import datetime, timedelta, time

class WebpageBase(BaseModel):
    url: HttpUrl = Field(..., description="The full URL that will be scraped")
    page_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Human‑readable name for the page (optional)",
    )
    run_time: time = Field(
        default_factory=lambda: time(hour=4, minute=0),
        description="Time of day to run the scrape",
    )
    is_active: bool = Field(True)

    @field_validator('run_time', mode='before')
    def _to_time(cls, v):
        """Accept a timedelta (MySQL TIME) and return datetime.time."""
        if isinstance(v, timedelta):
            return (datetime.min + v).time()
        return v

class WebpageCreate(WebpageBase):
    pass

class WebpageInDB(WebpageBase):
    webpage_id: int

    class Config:
        orm_mode = True

class WebpagePatch(WebpageBase):
    url: Optional[HttpUrl] = None
    page_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Human-readable name for the page (optional)",
    )
    run_time: Optional[time] = Field(
        None,
        description="Time of day to run the scrape",
    )
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True

class WebpageOut(WebpageInDB):
    """
    Response model for PATCH and PUT operations.
    Inherits id, url, page_name from WebpageInDB and adds an
    `updated` flag indicating whether any column was actually changed.
    """
    updated: bool = Field(
        default=False,
        description="True if the UPDATE modified at least one column"
    )
