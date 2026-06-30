from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = ""
    skills_required: Optional[str] = ""
    experience_required: Optional[str] = ""
    location: Optional[str] = ""

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    recruiter_id: int
    created_at: datetime
    company: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    job_id: int

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: int
    applicant_id: int
    status: str
    match_score: int

    class Config:
        from_attributes = True
