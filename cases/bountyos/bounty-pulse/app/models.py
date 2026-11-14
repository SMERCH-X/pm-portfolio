from pydantic import BaseModel, Field

class Item(BaseModel):
    report_id: str
    event_type: str
    program_id: str
