from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size")
