from pydantic import BaseModel, Field

class Item(BaseModel):
    report_id: str
    candidate_id: str
    text_a: str
    text_b: str

class Candidate(BaseModel):
    report_id: str
    title: str
    description: str
    asset: str
