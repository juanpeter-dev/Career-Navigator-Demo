"""
Skill Extractor - Uses LLM to extract structured skills from unstructured profile data
"""
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from models import Skill, SkillSet, SkillCategory, SkillLevel, UserProfile
from config import settings, get_api_key


class ExtractedSkills(BaseModel):
    """Schema for LLM output"""
    skills: List[Dict[str, Any]] = Field(description="List of extracted skills with metadata")


class SkillExtractor:
    """Extracts and categorizes skills from profile data using LLM"""
    
    def __init__(self):
        """Initialize LLM based on configuration"""
        api_key, model_name = get_api_key()
        
        if settings.USE_ANTHROPIC and settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model=model_name,
                anthropic_api_key=api_key,
                temperature=0.3
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=0.3
            )
    
    async def extract_skills_from_github(self, github_profile) -> List[Skill]:
        """
        Extract skills from GitHub profile
        
        Args:
            github_profile: GitHubProfile object
            
        Returns:
            List of Skill objects
        """
        if not github_profile:
            return []
        
        # Prepare context for LLM
        context = f"""
GitHub Profile Analysis:
- Username: {github_profile.username}
- Bio: {github_profile.bio or 'N/A'}
- Public Repos: {github_profile.public_repos}
- Top Languages: {', '.join(github_profile.top_technologies[:5])}

Repository Details:
"""
        
        # Add top repositories
        for repo in github_profile.repositories[:10]:
            context += f"\n- {repo['name']}: {repo['description'] or 'No description'}"
            context += f"\n  Language: {repo['language']}, Stars: {repo['stars']}, Topics: {', '.join(repo.get('topics', []))}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter analyzing GitHub profiles.
Extract all technical skills from the GitHub profile data provided.

For each skill, determine:
1. Skill name (normalized, e.g., "JavaScript" not "javascript")
2. Category (Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps, Tools & Technologies, AI/ML, Web Development, Mobile Development, System Design)
3. Proficiency level based on:
   - Number and complexity of projects
   - Repository stars and activity
   - Code quality indicators
   - Years of apparent experience

Proficiency levels:
- beginner: 0-1 years, simple projects, learning phase
- intermediate: 1-3 years, moderate complexity, some production experience
- advanced: 3-5 years, complex projects, significant contributions
- expert: 5+ years, highly complex projects, thought leadership

Return a JSON array of skills with: name, category, level, years_experience (estimated)"""),
            ("human", "{context}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context})
        
        # Parse response
        skills = self._parse_llm_response(response.content)
        return skills
    
    async def extract_skills_from_resume(self, resume_data) -> List[Skill]:
        """
        Extract skills from resume
        
        Args:
            resume_data: ResumeData object
            
        Returns:
            List of Skill objects
        """
        if not resume_data:
            return []
        
        context = f"""
Resume Analysis:

Full Text:
{resume_data.raw_text[:3000]}  # Limit to avoid token limits

Mentioned Skills: {', '.join(resume_data.skills_mentioned)}

Education:
{self._format_list(resume_data.education)}

Experience:
{self._format_list(resume_data.experience)}

Projects:
{self._format_list(resume_data.projects)}

Certifications:
{', '.join(resume_data.certifications)}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter analyzing resumes.
Extract all technical and soft skills from the resume data provided.

For each skill, determine:
1. Skill name (normalized)
2. Category (Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps, Tools & Technologies, AI/ML, Web Development, Mobile Development, System Design, Soft Skills)
3. Proficiency level based on:
   - Years of experience mentioned
   - Project complexity
   - Certifications
   - Job responsibilities

Return a JSON array of skills with: name, category, level, years_experience (from resume if mentioned, otherwise estimated)"""),
            ("human", "{context}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context})
        
        skills = self._parse_llm_response(response.content)
        return skills
    
    async def extract_skills_from_linkedin(self, linkedin_data) -> List[Skill]:
        """
        Extract skills from LinkedIn profile
        
        Args:
            linkedin_data: LinkedInData object
            
        Returns:
            List of Skill objects
        """
        if not linkedin_data:
            return []
        
        context = f"""
LinkedIn Profile Analysis:

Headline: {linkedin_data.headline or 'N/A'}

Summary:
{linkedin_data.summary or 'N/A'}

Listed Skills: {', '.join(linkedin_data.skills[:20])}

Top Endorsed Skills:
{self._format_dict(linkedin_data.endorsements)}

Experience:
{self._format_list(linkedin_data.experience[:5])}

Education:
{self._format_list(linkedin_data.education)}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter analyzing LinkedIn profiles.
Extract all technical and soft skills from the LinkedIn profile data.

Pay special attention to:
- Endorsed skills (higher endorsements = higher confidence)
- Skills mentioned in experience descriptions
- Certifications and education

Return a JSON array of skills with: name, category, level, years_experience"""),
            ("human", "{context}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context})
        
        skills = self._parse_llm_response(response.content)
        return skills
    
    async def consolidate_skills(self, user_profile: UserProfile) -> SkillSet:
        """
        Extract and consolidate skills from all profile sources
        
        Args:
            user_profile: Complete UserProfile object
            
        Returns:
            SkillSet with all extracted skills
        """
        all_skills = []
        
        # Extract from each source
        if user_profile.github:
            github_skills = await self.extract_skills_from_github(user_profile.github)
            all_skills.extend(github_skills)
        
        if user_profile.resume:
            resume_skills = await self.extract_skills_from_resume(user_profile.resume)
            all_skills.extend(resume_skills)
        
        if user_profile.linkedin:
            linkedin_skills = await self.extract_skills_from_linkedin(user_profile.linkedin)
            all_skills.extend(linkedin_skills)
        
        # Consolidate duplicate skills (take highest level)
        skill_map = {}
        for skill in all_skills:
            key = skill.name.lower()
            if key not in skill_map or self._compare_levels(skill.level, skill_map[key].level) > 0:
                skill_map[key] = skill
        
        # Create SkillSet
        skill_set = SkillSet()
        for skill in skill_map.values():
            skill_set.add_skill(skill)
        
        return skill_set
    
    def _parse_llm_response(self, response_text: str) -> List[Skill]:
        """Parse LLM response into Skill objects"""
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            json_text = json_match.group(0) if json_match else '[]'
        
        try:
            skills_data = json.loads(json_text)
            
            skills = []
            for skill_dict in skills_data:
                try:
                    # Map category string to enum
                    category_str = skill_dict.get('category', 'Tools & Technologies')
                    category = self._map_category(category_str)
                    
                    # Map level string to enum
                    level_str = skill_dict.get('level', 'beginner').lower()
                    level = SkillLevel(level_str) if level_str in ['beginner', 'intermediate', 'advanced', 'expert'] else SkillLevel.BEGINNER
                    
                    skill = Skill(
                        name=skill_dict.get('name', 'Unknown'),
                        category=category,
                        level=level,
                        years_experience=float(skill_dict.get('years_experience', 0)),
                        source='extracted'
                    )
                    skills.append(skill)
                except Exception as e:
                    print(f"Warning: Failed to parse skill {skill_dict}: {e}")
                    continue
            
            return skills
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse LLM response as JSON: {e}")
            return []
    
    def _map_category(self, category_str: str) -> SkillCategory:
        """Map category string to SkillCategory enum"""
        category_map = {
            'programming languages': SkillCategory.PROGRAMMING_LANGUAGE,
            'frameworks & libraries': SkillCategory.FRAMEWORK,
            'frameworks': SkillCategory.FRAMEWORK,
            'databases': SkillCategory.DATABASE,
            'cloud & devops': SkillCategory.CLOUD_DEVOPS,
            'cloud': SkillCategory.CLOUD_DEVOPS,
            'devops': SkillCategory.CLOUD_DEVOPS,
            'tools & technologies': SkillCategory.TOOLS,
            'tools': SkillCategory.TOOLS,
            'ai/ml': SkillCategory.AI_ML,
            'machine learning': SkillCategory.AI_ML,
            'web development': SkillCategory.WEB_DEV,
            'mobile development': SkillCategory.MOBILE_DEV,
            'system design': SkillCategory.SYSTEM_DESIGN,
            'soft skills': SkillCategory.SOFT_SKILL,
        }
        
        return category_map.get(category_str.lower(), SkillCategory.TOOLS)
    
    def _compare_levels(self, level1: SkillLevel, level2: SkillLevel) -> int:
        """Compare two skill levels. Returns 1 if level1 > level2, -1 if level1 < level2, 0 if equal"""
        level_order = {
            SkillLevel.BEGINNER: 0,
            SkillLevel.INTERMEDIATE: 1,
            SkillLevel.ADVANCED: 2,
            SkillLevel.EXPERT: 3
        }
        
        val1 = level_order.get(level1, 0)
        val2 = level_order.get(level2, 0)
        
        if val1 > val2:
            return 1
        elif val1 < val2:
            return -1
        else:
            return 0
    
    def _format_list(self, items: List[Any]) -> str:
        """Format list for LLM context"""
        if not items:
            return "None"
        
        result = ""
        for item in items[:5]:  # Limit to 5 items
            if isinstance(item, dict):
                result += f"\n- {', '.join(f'{k}: {v}' for k, v in item.items())}"
            else:
                result += f"\n- {item}"
        
        return result
    
    def _format_dict(self, items: Dict[str, Any]) -> str:
        """Format dictionary for LLM context"""
        if not items:
            return "None"
        
        # Sort by value (endorsements) and take top 10
        sorted_items = sorted(items.items(), key=lambda x: x[1], reverse=True)[:10]
        return "\n".join(f"- {k}: {v} endorsements" for k, v in sorted_items)
