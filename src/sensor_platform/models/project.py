from pydantic import BaseModel, Field


class Project(BaseModel):
    """A monitoring project / campaign that groups devices, e.g. 'BRUGGE-01'."""

    project_id: str = Field(..., min_length=1, max_length=64)
    name: str
    region: str
