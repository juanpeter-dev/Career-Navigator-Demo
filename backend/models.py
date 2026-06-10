"""
Data models for Personal Career Navigator
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class SkillLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, Enum):
    """Skill categories"""
    PROGRAMMING_LANGUAGE = "Programming Languages"
    FRAMEWORK = "Frameworks & Libraries"
    DATABASE = "Databases"
    CLOUD_DEVOPS = "Cloud & DevOps"
    TOOLS = "Tools & Technologies"
    AI_ML = "AI/ML"
    WEB_DEV = "Web Development"
    MOBILE_DEV = "Mobile Development"
    SYSTEM_DESIGN = "System Design"
    SOFT_SKILL = "Soft Skills"


class Skill(BaseModel):
    """Individual skill with metadata"""
    name: str
    category: SkillCategory
    level: SkillLevel = SkillLevel.BEGINNER
    years_experience: Optional[float] = 0.0
    source: str = "extracted"  # extracted, inferred, or user_provided


class SkillSet(BaseModel):
    """Collection of skills organized by category"""
    technical_skills: List[Skill] = Field(default_factory=list)
    soft_skills: List[Skill] = Field(default_factory=list)
    total_count: int = 0
    
    def add_skill(self, skill: Skill):
        """Add a skill to the appropriate category"""
        if skill.category == SkillCategory.SOFT_SKILL:
            self.soft_skills.append(skill)
        else:
            self.technical_skills.append(skill)
        self.total_count += 1


class GitHubProfile(BaseModel):
    """GitHub profile data"""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    repositories: List[Dict[str, Any]] = Field(default_factory=list)
    languages: Dict[str, int] = Field(default_factory=dict)  # language: bytes of code
    top_technologies: List[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    """Parsed resume data"""
    raw_text: str
    education: List[Dict[str, str]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    skills_mentioned: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, str]] = Field(default_factory=list)


class LinkedInData(BaseModel):
    """LinkedIn profile data"""
    profile_url: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, str]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    endorsements: Dict[str, int] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """Complete user profile from all sources"""
    user_id: str = Field(default_factory=lambda: f"user_{datetime.now().timestamp()}")
    github: Optional[GitHubProfile] = None
    resume: Optional[ResumeData] = None
    linkedin: Optional[LinkedInData] = None
    extracted_skills: SkillSet = Field(default_factory=SkillSet)
    created_at: datetime = Field(default_factory=datetime.now)


class JobRole(BaseModel):
    """Target job role with requirements"""
    title: str
    description: str
    required_skills: List[Skill] = Field(default_factory=list)
    preferred_skills: List[Skill] = Field(default_factory=list)
    experience_years: Optional[int] = None
    industry: Optional[str] = None
    salary_range: Optional[str] = None


class SkillGap(BaseModel):
    """Identified skill gap with priority"""
    skill_name: str
    category: SkillCategory
    current_level: SkillLevel = SkillLevel.BEGINNER
    target_level: SkillLevel
    priority: int = Field(ge=1, le=10)  # 1-10, 10 being highest
    estimated_hours: int = 0
    reason: str = ""


class LearningResource(BaseModel):
    """Individual learning resource"""
    title: str
    type: str  # course, tutorial, documentation, project, video
    url: Optional[str] = None
    platform: str
    duration: Optional[str] = None
    difficulty: SkillLevel
    description: str
    skills_covered: List[str] = Field(default_factory=list)
    is_free: bool = True


class Checkpoint(BaseModel):
    """Progress checkpoint/milestone"""
    day: int
    title: str
    description: str
    deliverable: str
    skills_practiced: List[str] = Field(default_factory=list)


class WeekPlan(BaseModel):
    """Weekly learning plan"""
    week_number: int
    theme: str
    goals: List[str] = Field(default_factory=list)
    daily_tasks: Dict[int, str] = Field(default_factory=dict)  # day: task
    resources: List[LearningResource] = Field(default_factory=list)
    checkpoint: Optional[Checkpoint] = None


class LearningRoadmap(BaseModel):
    """Complete 30-day learning roadmap"""
    user_id: str
    target_role: str
    created_at: datetime = Field(default_factory=datetime.now)
    total_days: int = 30
    hours_per_day: int = 2
    
    # Roadmap structure
    overview: str = ""
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    weekly_plans: List[WeekPlan] = Field(default_factory=list)
    all_resources: List[LearningResource] = Field(default_factory=list)
    checkpoints: List[Checkpoint] = Field(default_factory=list)
    
    # Adaptive features
    progress_percentage: float = 0.0
    completed_checkpoints: List[int] = Field(default_factory=list)
    adaptation_notes: List[str] = Field(default_factory=list)


class AgentState(BaseModel):
    """State for LangGraph agent workflow"""
    # Input
    user_profile: Optional[UserProfile] = None
    target_role: Optional[JobRole] = None
    hours_per_day: int = 2
    
    # Intermediate states
    extracted_skills: Optional[SkillSet] = None
    job_requirements: Optional[JobRole] = None
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    
    # Output
    roadmap: Optional[LearningRoadmap] = None
    
    # Metadata
    current_step: str = "init"
    errors: List[str] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
