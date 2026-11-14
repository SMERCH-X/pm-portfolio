from pydantic import BaseModel, Field

class Item(BaseModel):
    report_id: str
    severity: str
    asset_criticality: int
    exploitability: int

class RewardRule(BaseModel):
    severity: str
    amount: float = Field(ge=0)
