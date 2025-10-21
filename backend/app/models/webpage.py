from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class WebpageBase(BaseModel):
    url: HttpUrl = Field(..., description="The full URL that will be scraped")
    page_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Human-readable name for the page (optional)",
    )
    run_minute: int = Field(0, ge=0, le=59)
    run_hour: int = Field(10, ge=0, le=23)
    is_active: bool = Field(True)

class WebpageCreate(WebpageBase):
    pass

class WebpageInDB(WebpageBase):
    webpage_id: int

    class Config:
        orm_mode = True

class WebpagePatch(WebpageBase):
    url: Optional[HttpUrl] = None
    page_name: Optional[str] = None
    run_minute: Optional[int] = Field(None, ge=0, le=59)
    run_hour: Optional[int] = Field(None, ge=0, le=23)
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
