"""
CV Extraction Schema using Pydantic

This module defines the data models for extracting structured information
from curriculum vitae (CV) documents.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ContactInformation(BaseModel):
    """Contact details of the candidate."""

    full_name: str = Field(..., description="Full name of the candidate")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State/Country")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    portfolio: Optional[HttpUrl] = Field(None, description="Portfolio or personal website URL")


class WorkExperience(BaseModel):
    """Individual work experience entry."""

    job_title: str = Field(..., description="Job title or position")
    company: str = Field(..., description="Company or organization name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[date] = Field(None, description="Start date of employment")
    end_date: Optional[date] = Field(None, description="End date of employment (null if current)")
    is_current: bool = Field(False, description="Whether this is the current position")
    description: Optional[str] = Field(None, description="Job description and responsibilities")
    achievements: List[str] = Field(default_factory=list, description="Key achievements and accomplishments")


class Education(BaseModel):
    """Educational qualification entry."""

    degree: str = Field(..., description="Degree or certification name")
    institution: str = Field(..., description="Educational institution name")
    location: Optional[str] = Field(None, description="Institution location")
    field_of_study: Optional[str] = Field(None, description="Major or field of study")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="Graduation date")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA if applicable")
    honors: Optional[str] = Field(None, description="Honors, awards, or distinctions")


class Certification(BaseModel):
    """Professional certification entry."""

    name: str = Field(..., description="Certification name")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: Optional[date] = Field(None, description="Date certification was issued")
    expiration_date: Optional[date] = Field(None, description="Expiration date if applicable")
    credential_id: Optional[str] = Field(None, description="Certification credential ID")
    credential_url: Optional[HttpUrl] = Field(None, description="URL to verify certification")


class Project(BaseModel):
    """Project entry."""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    role: Optional[str] = Field(None, description="Role in the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    url: Optional[HttpUrl] = Field(None, description="Project URL or repository")
    highlights: List[str] = Field(default_factory=list, description="Key achievements or highlights")


class Language(BaseModel):
    """Language proficiency entry."""

    language: str = Field(..., description="Language name")
    proficiency: str = Field(
        ...,
        description="Proficiency level (e.g., Native, Fluent, Professional, Intermediate, Basic)"
    )


class Skill(BaseModel):
    """Skill entry with optional proficiency level."""

    name: str = Field(..., description="Skill name")
    category: Optional[str] = Field(None, description="Skill category (e.g., Programming, Soft Skills)")
    proficiency: Optional[str] = Field(None, description="Proficiency level")


class CVSchema(BaseModel):
    """
    Complete CV schema for extracting structured information from resumes.

    This is the main model that encompasses all sections of a CV.
    """

    contact_info: ContactInformation = Field(..., description="Personal contact information")

    summary: Optional[str] = Field(
        None,
        description="Professional summary or objective statement"
    )

    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="List of work experiences, ordered by most recent first"
    )

    education: List[Education] = Field(
        default_factory=list,
        description="List of educational qualifications, ordered by most recent first"
    )

    skills: List[Skill] = Field(
        default_factory=list,
        description="List of skills and competencies"
    )

    certifications: List[Certification] = Field(
        default_factory=list,
        description="List of professional certifications"
    )

    projects: List[Project] = Field(
        default_factory=list,
        description="List of notable projects"
    )

    languages: List[Language] = Field(
        default_factory=list,
        description="List of languages spoken"
    )


    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "contact_info": {
                    "full_name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1-555-0123",
                    "location": "San Francisco, CA",
                    "linkedin": "https://linkedin.com/in/johndoe",
                    "github": "https://github.com/johndoe"
                },
                "summary": "Experienced software engineer with 5+ years building scalable web applications",
                "work_experience": [
                    {
                        "job_title": "Senior Software Engineer",
                        "company": "Tech Corp",
                        "location": "San Francisco, CA",
                        "start_date": "2021-01-15",
                        "end_date": None,
                        "is_current": True,
                        "description": "Lead backend development for cloud infrastructure",
                        "achievements": [
                            "Reduced API response time by 40%",
                            "Mentored 3 junior engineers"
                        ]
                    }
                ],
                "skills": [
                    {"name": "Python", "category": "Programming", "proficiency": "Expert"},
                    {"name": "AWS", "category": "Cloud", "proficiency": "Advanced"}
                ]
            }
        }
