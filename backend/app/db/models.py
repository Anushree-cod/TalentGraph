from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_recruiter = Column(Boolean, default=False)
    
    # Relationships
    jobs = relationship("Job", back_populates="recruiter")
    applications = relationship("JobApplication", back_populates="applicant")
    profile = relationship("CandidateProfile", back_populates="user", uselist=False)

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text)
    parsed_skills = Column(Text)  # Store JSON as string for simplicity
    github_analysis = Column(Text) # Store JSON as string for simplicity
    
    user = relationship("User", back_populates="profile")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(Text)
    skills_required = Column(Text, nullable=True)
    experience_required = Column(String, nullable=True)
    location = Column(String, nullable=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")

class JobApplication(Base):
    __tablename__ = "job_applications"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="applied")
    match_score = Column(Integer, default=0)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    years_experience = Column(Integer, nullable=True)
    expected_salary = Column(String, nullable=True)
    cover_letter = Column(Text, nullable=True)
    analysis_json = Column(Text, nullable=True)
    
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
