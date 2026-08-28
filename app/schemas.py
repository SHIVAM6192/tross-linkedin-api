from typing import List, Optional
from pydantic import BaseModel, Field

class DateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class MediaItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    media_type: str  # e.g., "Document", "Link"
    thumbnail_url: Optional[str] = None

class ExperienceItem(DateRange):
    title: str
    company_name: str
    location: Optional[str] = None
    description: Optional[str] = None

class EducationItem(DateRange):
    school_name: str
    degree_name: Optional[str] = None
    field_of_study: Optional[str] = None
    grade: Optional[str] = None

class CertificationItem(DateRange):
    name: str
    authority: Optional[str] = None
    url: Optional[str] = None
    license_number: Optional[str] = None

class ProjectItem(DateRange):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None

class ProfileResponse(BaseModel):
    public_identifier: str
    profile_urn: Optional[str] = None
    industry: Optional[str] = None
    full_name: str
    headline: Optional[str] = None
    about: Optional[str] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None
    background_picture_url: Optional[str] = None
    featured_media: List[MediaItem] = Field(default_factory=list)
    experiences: List[ExperienceItem] = Field(default_factory=list)
    educations: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)