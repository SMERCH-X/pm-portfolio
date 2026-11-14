from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    policy: str
    reward_budget: float

class Asset(BaseModel):
    program_id: str
    target: str
    in_scope: bool = True
    notes: str = ""
