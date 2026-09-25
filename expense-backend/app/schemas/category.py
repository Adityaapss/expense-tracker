from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Shape of the JSON body for POST /api/categories."""

    name: str = Field(min_length=1, max_length=50)
    icon: str | None = Field(default=None, max_length=50)


class CategoryOut(BaseModel):
    """A category as returned to the client. user_id is left out on
    purpose - the client only needs to know a category's name/icon and
    whether it belongs to them (that's implied by it showing up at all).
    """

    id: int
    name: str
    icon: str | None

    class Config:
        from_attributes = True
