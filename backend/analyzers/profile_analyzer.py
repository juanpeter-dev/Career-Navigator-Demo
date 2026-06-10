"""
Profile Analyzer - Extracts and analyzes user profile data from multiple sources
"""
from typing import Optional, Dict, Any
import PyPDF2
import docx
from io import BytesIO
from models import UserProfile, GitHubProfile, ResumeData, LinkedInData
from utils import GitHubClient, extract_skills_from_text


class ProfileAnalyzer:
    """Main profile analyzer that coordinates data extraction from all sources"""
    
    def __init__(self):
        self.github_client = GitHubClient()
    
    async def analyze_github(self, username: str) -> GitHubProfile:
        """
        Analyze GitHub profile
        
        Args:
            username: GitHub username
            
        Returns:
            GitHubProfile object with extracted data
        """
        try:
            profile_data = self.github_client.get_user_profile(username)
            return GitHubProfile(**profile_data)
        except Exception as e:
            raise ValueError(f"Failed to analyze GitHub profile: {str(e)}")
    
    def parse_resume_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF resume"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF resume: {str(e)}")
    
    def parse_resume_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX resume"""
        try:
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX resume: {str(e)}")
    
    def analyze_resume(self, file_content: bytes, file_type: str) -> ResumeData:
        """
        Analyze resume file
        
        Args:
            file_content: Binary content of the resume file
            file_type: File type ('pdf' or 'docx')
            
        Returns:
            ResumeData object with parsed information
        """
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            raw_text = self.parse_resume_pdf(file_content)
        elif file_type.lower() in ['docx', 'doc']:
            raw_text = self.parse_resume_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Extract basic information using pattern matching
        # (The AI agent will do more sophisticated extraction)
        skills_mentioned = extract_skills_from_text(raw_text)
        
        # Extract sections (basic implementation)
        education = self._extract_education(raw_text)
        experience = self._extract_experience(raw_text)
        projects = self._extract_projects(raw_text)
        certifications = self._extract_certifications(raw_text)
        
        return ResumeData(
            raw_text=raw_text,
            education=education,
            experience=experience,
            skills_mentioned=skills_mentioned,
            certifications=certifications,
            projects=projects
        )
    
    def _extract_education(self, text: str) -> list[Dict[str, str]]:
        """Extract education information from resume text"""
        # Basic implementation - AI agent will do better
        education = []
        
        # Look for common degree keywords
        import re
        degree_patterns = [
            r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?(\d{4})',
            r'(University|College|Institute).*?(\d{4})',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match[0] if isinstance(match, tuple) else match,
                    'year': match[1] if isinstance(match, tuple) and len(match) > 1 else 'Unknown'
                })
        
        return education[:5]  # Limit to 5 entries
    
    def _extract_experience(self, text: str) -> list[Dict[str, Any]]:
        """Extract work experience from resume text"""
        # Basic implementation
        experience = []
        
        import re
        # Look for job titles and companies
        title_patterns = [
            r'(Software Engineer|Developer|Data Scientist|Product Manager|Designer|Analyst)',
            r'(Senior|Junior|Lead|Principal|Staff)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                experience.append({
                    'title': match,
                    'company': 'Unknown',
                    'duration': 'Unknown'
                })
        
        return experience[:5]
    
    def _extract_projects(self, text: str) -> list[Dict[str, str]]:
        """Extract projects from resume text"""
        projects = []
        
        import re
        # Look for project indicators
        project_section = re.search(r'projects?:?(.*?)(?:experience|education|skills|$)', 
                                   text, re.IGNORECASE | re.DOTALL)
        
        if project_section:
            project_text = project_section.group(1)
            # Split by bullet points or newlines
            project_lines = [line.strip() for line in project_text.split('\n') 
                           if line.strip() and len(line.strip()) > 20]
            
            for line in project_lines[:5]:
                projects.append({
                    'name': line[:100],  # First 100 chars as name
                    'description': line
                })
        
        return projects
    
    def _extract_certifications(self, text: str) -> list[str]:
        """Extract certifications from resume text"""
        import re
        
        cert_keywords = [
            'AWS Certified',
            'Google Cloud',
            'Azure',
            'Certified',
            'Certificate',
            'Certification'
        ]
        
        certifications = []
        for keyword in cert_keywords:
            pattern = rf'{keyword}[^.\n]*'
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        
        return list(set(certifications))[:10]
    
    def analyze_linkedin(self, linkedin_data: Dict[str, Any]) -> LinkedInData:
        """
        Analyze LinkedIn data (provided as structured data or scraped)
        
        Args:
            linkedin_data: Dictionary containing LinkedIn profile information
            
        Returns:
            LinkedInData object
        """
        return LinkedInData(
            profile_url=linkedin_data.get('profile_url'),
            headline=linkedin_data.get('headline'),
            summary=linkedin_data.get('summary'),
            experience=linkedin_data.get('experience', []),
            education=linkedin_data.get('education', []),
            skills=linkedin_data.get('skills', []),
            endorsements=linkedin_data.get('endorsements', {})
        )
    
    async def create_user_profile(
        self,
        github_username: Optional[str] = None,
        resume_file: Optional[tuple[bytes, str]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Create comprehensive user profile from all available sources
        
        Args:
            github_username: GitHub username (optional)
            resume_file: Tuple of (file_content, file_type) (optional)
            linkedin_data: LinkedIn profile data (optional)
            
        Returns:
            Complete UserProfile object
        """
        profile = UserProfile()
        
        # Analyze GitHub if provided
        if github_username:
            try:
                profile.github = await self.analyze_github(github_username)
            except Exception as e:
                print(f"Warning: Failed to analyze GitHub profile: {e}")
        
        # Analyze resume if provided
        if resume_file:
            try:
                file_content, file_type = resume_file
                profile.resume = self.analyze_resume(file_content, file_type)
            except Exception as e:
                print(f"Warning: Failed to analyze resume: {e}")
        
        # Analyze LinkedIn if provided
        if linkedin_data:
            try:
                profile.linkedin = self.analyze_linkedin(linkedin_data)
            except Exception as e:
                print(f"Warning: Failed to analyze LinkedIn data: {e}")
        
        return profile
