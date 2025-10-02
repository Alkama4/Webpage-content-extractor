from typing import Optional
from pydantic import BaseModel, Field

class ElementBase(BaseModel):
    locator: str = Field(..., max_length=512,
                         description="CSS selector or XPath")
    metric_name: Optional[str] = Field(
        None,
        max_length=128,
        description="Optional friendly name for the metric",
    )

class ElementCreate(ElementBase):
    pass

class ElementInDB(ElementBase):
    element_id: int
    webpage_id: int

    class Config:
        orm_mode = True

class ElementPatch(ElementBase):
    locator: Optional[str] = None
    metric_name: Optional[str] = None

    class Config:
        orm_mode = True


class ElementOut(ElementInDB):
    """
    Response model for PATCH and PUT operations.
    Inherits id, locator, metric_name, webpage_id from ElementInDB
    and adds an `updated` flag indicating whether any column was actually changed.
    """
    updated: Optional[bool] = None
    updated: bool = Field(
        default=False,
        description="True if the UPDATE modified at least one column"
    )
    