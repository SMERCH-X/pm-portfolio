from pydantic import BaseModel, Field
from typing import Literal

class Item(BaseModel):
    program_id: str
    asset: str
    title: str
    description: str
    severity: str

class StatusChange(BaseModel):
    status: Literal["new", "triaged", "accepted", "rejected", "resolved"]
    assignee: str = ""
