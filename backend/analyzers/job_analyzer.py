"""
Job Analyzer - Analyzes job descriptions and extracts requirements
"""
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from models import JobRole, Skill, SkillCategory, SkillLevel
from config import settings, get_api_key


class JobAnalyzer:
    """Analyzes job descriptions and extracts structured requirements"""
    
    def __init__(self):
        """Initialize LLM"""
        api_key, model_name = get_api_key()
        
        if settings.USE_ANTHROPIC and settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model=model_name,
                anthropic_api_key=api_key,
                temperature=0.2
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=0.2
            )
    
    async def analyze_job_role(
        self,
        job_title: str,
        job_description: str = "",
        experience_years: int = 0
    ) -> JobRole:
        """
        Analyze a job role and extract requirements
        
        Args:
            job_title: Target job title
            job_description: Optional job description (if empty, will generate typical requirements)
            experience_years: Years of experience required
            
        Returns:
            JobRole object with extracted requirements
        """
        if job_description:
            # Analyze provided job description
            return await self._analyze_job_description(job_title, job_description, experience_years)
        else:
            # Generate typical requirements for the role
            return await self._generate_role_requirements(job_title, experience_years)
    
    async def _analyze_job_description(
        self,
        job_title: str,
        job_description: str,
        experience_years: int
    ) -> JobRole:
        """Analyze a specific job description"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter analyzing job descriptions.

Extract structured information from the job description:

1. Required Skills: Skills that are must-haves (mentioned as "required", "must have", etc.)
2. Preferred Skills: Nice-to-have skills (mentioned as "preferred", "plus", "bonus", etc.)

For each skill, provide:
- name: Normalized skill name
- category: One of (Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps, Tools & Technologies, AI/ML, Web Development, Mobile Development, System Design, Soft Skills)
- level: Expected proficiency (beginner, intermediate, advanced, expert) based on job seniority
- years_experience: Expected years (estimate if not specified)

Return JSON with:
{{
  "required_skills": [...],
  "preferred_skills": [...],
  "key_responsibilities": ["...", "..."],
  "industry": "...",
  "salary_range": "..." (if mentioned)
}}"""),
            ("human", """Job Title: {job_title}
Experience Required: {experience_years} years

Job Description:
{job_description}""")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "job_title": job_title,
            "job_description": job_description,
            "experience_years": experience_years
        })
        
        # Parse response
        job_data = self._parse_job_response(response.content)
        
        return JobRole(
            title=job_title,
            description=job_description,
            required_skills=job_data['required_skills'],
            preferred_skills=job_data['preferred_skills'],
            experience_years=experience_years,
            industry=job_data.get('industry'),
            salary_range=job_data.get('salary_range')
        )
    
    async def _generate_role_requirements(
        self,
        job_title: str,
        experience_years: int
    ) -> JobRole:
        """Generate typical requirements for a job role"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter with deep knowledge of job market requirements.

Generate typical requirements for the given job role based on current industry standards.

Provide:
1. Required Skills: Core skills needed for this role
2. Preferred Skills: Additional skills that would be beneficial
3. Key Responsibilities: Main duties and responsibilities
4. Industry context

For each skill, provide:
- name: Normalized skill name
- category: One of (Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps, Tools & Technologies, AI/ML, Web Development, Mobile Development, System Design, Soft Skills)
- level: Expected proficiency based on experience level
- years_experience: Typical years needed

Return JSON with:
{{
  "description": "Brief role description",
  "required_skills": [...],
  "preferred_skills": [...],
  "key_responsibilities": ["...", "..."],
  "industry": "Typical industry",
  "salary_range": "Typical range (if applicable)"
}}"""),
            ("human", """Job Title: {job_title}
Experience Level: {experience_years} years

Generate comprehensive requirements for this role based on current market standards.""")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "job_title": job_title,
            "experience_years": experience_years
        })
        
        # Parse response
        job_data = self._parse_job_response(response.content)
        
        return JobRole(
            title=job_title,
            description=job_data.get('description', f"Requirements for {job_title}"),
            required_skills=job_data['required_skills'],
            preferred_skills=job_data['preferred_skills'],
            experience_years=experience_years,
            industry=job_data.get('industry'),
            salary_range=job_data.get('salary_range')
        )
    
    def _parse_job_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured job data"""
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            json_text = json_match.group(0) if json_match else '{}'
        
        try:
            data = json.loads(json_text)
            
            # Parse skills
            required_skills = self._parse_skills(data.get('required_skills', []))
            preferred_skills = self._parse_skills(data.get('preferred_skills', []))
            
            return {
                'description': data.get('description', ''),
                'required_skills': required_skills,
                'preferred_skills': preferred_skills,
                'key_responsibilities': data.get('key_responsibilities', []),
                'industry': data.get('industry'),
                'salary_range': data.get('salary_range')
            }
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse job response: {e}")
            return {
                'description': '',
                'required_skills': [],
                'preferred_skills': [],
                'key_responsibilities': [],
                'industry': None,
                'salary_range': None
            }
    
    def _parse_skills(self, skills_data: List[Dict[str, Any]]) -> List[Skill]:
        """Parse skills from JSON data"""
        skills = []
        
        for skill_dict in skills_data:
            try:
                # Map category
                category_str = skill_dict.get('category', 'Tools & Technologies')
                category = self._map_category(category_str)
                
                # Map level
                level_str = skill_dict.get('level', 'intermediate').lower()
                level = SkillLevel(level_str) if level_str in ['beginner', 'intermediate', 'advanced', 'expert'] else SkillLevel.INTERMEDIATE
                
                skill = Skill(
                    name=skill_dict.get('name', 'Unknown'),
                    category=category,
                    level=level,
                    years_experience=float(skill_dict.get('years_experience', 0)),
                    source='job_requirement'
                )
                skills.append(skill)
            except Exception as e:
                print(f"Warning: Failed to parse skill {skill_dict}: {e}")
                continue
        
        return skills
    
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
