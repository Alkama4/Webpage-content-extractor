class WebpageBase(BaseModel):
    url: HttpUrl = Field(..., description="The full URL that will be scraped")
    page_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Human-readable name for the page (optional)",
    )

class WebpageCreate(WebpageBase):
    pass

class WebpageInDB(WebpageBase):
    webpage_id: int

    class Config:
        orm_mode = True

class WebpagePatch(WebpageBase):
    url: Optional[HttpUrl] = None
    page_name: Optional[str] = None

    class Config:
        orm_mode = True

class WebpageOut(WebpageBase):
    updated: Optional[bool] = None
