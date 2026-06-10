"""
Utility functions for Personal Career Navigator
"""
import os
import re
from typing import Optional, List, Dict, Any
from github import Github, GithubException
import requests
from config import settings


class GitHubClient:
    """GitHub API client wrapper"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional token"""
        self.token = token or settings.GITHUB_TOKEN
        self.client = Github(self.token) if self.token else Github()
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch comprehensive GitHub profile data
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary containing profile data
        """
        try:
            user = self.client.get_user(username)
            
            # Get repositories
            repos = []
            languages = {}
            
            for repo in user.get_repos():
                if not repo.fork:  # Skip forked repos
                    repo_data = {
                        'name': repo.name,
                        'description': repo.description,
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'forks': repo.forks_count,
                        'topics': repo.get_topics(),
                        'created_at': repo.created_at.isoformat() if repo.created_at else None,
                        'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    }
                    repos.append(repo_data)
                    
                    # Aggregate languages
                    if repo.language:
                        repo_languages = repo.get_languages()
                        for lang, bytes_count in repo_languages.items():
                            languages[lang] = languages.get(lang, 0) + bytes_count
            
            # Sort languages by usage
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            
            profile_data = {
                'username': user.login,
                'name': user.name,
                'bio': user.bio,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following,
                'repositories': repos,
                'languages': dict(languages),
                'top_technologies': [lang for lang, _ in top_languages[:10]],
            }
            
            return profile_data
            
        except GithubException as e:
            raise ValueError(f"Failed to fetch GitHub profile: {str(e)}")
    
    def analyze_repository_complexity(self, repo_data: Dict[str, Any]) -> str:
        """Analyze repository complexity based on metadata"""
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        topics = repo_data.get('topics', [])
        
        if stars > 50 or forks > 20 or len(topics) > 5:
            return "advanced"
        elif stars > 10 or forks > 5 or len(topics) > 2:
            return "intermediate"
        else:
            return "beginner"


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from text using pattern matching
    This is a basic implementation - the AI agent will do more sophisticated extraction
    
    Args:
        text: Input text (resume, bio, etc.)
        
    Returns:
        List of extracted skill keywords
    """
    # Common skill keywords (this would be much more comprehensive in production)
    skill_patterns = [
        # Programming Languages
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin|Scala)\b',
        # Frameworks
        r'\b(React|Angular|Vue|Django|Flask|FastAPI|Spring|Express|Next\.js|Node\.js)\b',
        # Databases
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|DynamoDB|Firebase)\b',
        # Cloud & DevOps
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|CI/CD|Jenkins|GitHub Actions|Terraform)\b',
        # AI/ML
        r'\b(Machine Learning|Deep Learning|TensorFlow|PyTorch|Scikit-learn|NLP|Computer Vision)\b',
        # Tools
        r'\b(Git|Linux|Bash|REST API|GraphQL|Microservices|Agile|Scrum)\b',
    ]
    
    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)


def normalize_skill_name(skill: str) -> str:
    """Normalize skill names for consistency"""
    # Convert to title case and handle common variations
    skill = skill.strip().title()
    
    # Handle common variations
    replacements = {
        'Javascript': 'JavaScript',
        'Typescript': 'TypeScript',
        'Nodejs': 'Node.js',
        'Nextjs': 'Next.js',
        'Mongodb': 'MongoDB',
        'Postgresql': 'PostgreSQL',
        'Mysql': 'MySQL',
        'Graphql': 'GraphQL',
        'Tensorflow': 'TensorFlow',
        'Pytorch': 'PyTorch',
    }
    
    return replacements.get(skill, skill)


def calculate_learning_hours(current_level: str, target_level: str, skill_complexity: str = "medium") -> int:
    """
    Estimate hours needed to progress from current to target skill level
    
    Args:
        current_level: Current proficiency (beginner, intermediate, advanced, expert)
        target_level: Target proficiency
        skill_complexity: Skill complexity (low, medium, high)
        
    Returns:
        Estimated hours needed
    """
    level_map = {
        'beginner': 0,
        'intermediate': 1,
        'advanced': 2,
        'expert': 3
    }
    
    complexity_multiplier = {
        'low': 1.0,
        'medium': 1.5,
        'high': 2.0
    }
    
    current = level_map.get(current_level.lower(), 0)
    target = level_map.get(target_level.lower(), 3)
    
    if target <= current:
        return 0
    
    # Base hours per level progression
    base_hours = {
        0: 20,   # beginner -> intermediate
        1: 40,   # intermediate -> advanced
        2: 60,   # advanced -> expert
    }
    
    total_hours = 0
    for level in range(current, target):
        total_hours += base_hours.get(level, 30)
    
    # Apply complexity multiplier
    multiplier = complexity_multiplier.get(skill_complexity, 1.5)
    return int(total_hours * multiplier)


def format_duration(hours: int) -> str:
    """Format hours into human-readable duration"""
    if hours < 1:
        return f"{int(hours * 60)} minutes"
    elif hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = hours // 24
        remaining_hours = hours % 24
        if remaining_hours == 0:
            return f"{days} day{'s' if days != 1 else ''}"
        else:
            return f"{days} day{'s' if days != 1 else ''}, {remaining_hours} hour{'s' if remaining_hours != 1 else ''}"
