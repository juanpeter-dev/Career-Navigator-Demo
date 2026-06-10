"""
Configuration management for Personal Career Navigator
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    # Model Configuration
    PRIMARY_MODEL: str = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet
    FALLBACK_MODEL: str = "gpt-4-turbo-preview"
    USE_ANTHROPIC: bool = True  # Primary choice
    
    # Application Settings
    MAX_ROADMAP_DAYS: int = 30
    MIN_HOURS_PER_DAY: int = 1
    MAX_HOURS_PER_DAY: int = 8
    DEFAULT_HOURS_PER_DAY: int = 2
    
    # Skill Taxonomy
    TECHNICAL_SKILL_CATEGORIES: list[str] = [
        "Programming Languages",
        "Frameworks & Libraries",
        "Databases",
        "Cloud & DevOps",
        "Tools & Technologies",
        "AI/ML",
        "Web Development",
        "Mobile Development",
        "System Design"
    ]
    
    SOFT_SKILL_CATEGORIES: list[str] = [
        "Communication",
        "Leadership",
        "Problem Solving",
        "Teamwork",
        "Time Management",
        "Adaptability",
        "Critical Thinking"
    ]
    
    # Resource Platforms
    LEARNING_PLATFORMS: list[str] = [
        "Coursera",
        "Udemy",
        "freeCodeCamp",
        "YouTube",
        "MDN Web Docs",
        "Official Documentation",
        "GitHub",
        "LeetCode",
        "HackerRank"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_api_key() -> tuple[str, str]:
    """
    Get the appropriate API key and model based on configuration
    Returns: (api_key, model_name)
    """
    if settings.USE_ANTHROPIC and settings.ANTHROPIC_API_KEY:
        return settings.ANTHROPIC_API_KEY, settings.PRIMARY_MODEL
    elif settings.OPENAI_API_KEY:
        return settings.OPENAI_API_KEY, settings.FALLBACK_MODEL
    else:
        raise ValueError(
            "No API key configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file"
        )
