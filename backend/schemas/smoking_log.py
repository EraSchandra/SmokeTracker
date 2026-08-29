from pydantic import BaseModel, Field
from datetime import datetime

class SmokingLogsCreate(BaseModel):
    cigarettes: int
    mood: str
    stress_level: int = Field(..., ge=1, le=10, description="Stress level must be between 1 and 10")
    location: str
    reason: str
    smoked_at: datetime

