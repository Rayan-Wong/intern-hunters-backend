import io

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.workers.internship_roles import ROLE_LIST
from app.core.config import get_settings
from app.exceptions.internship_listings_exceptions import GeminiDown
from app.schemas.gemini import Opinion, Comments
from app.schemas.resume_editor import Resume

class GeminiAPI:
    def __init__(self, api_key):
        """Initialises gemini client"""
        self.client = genai.Client(api_key=api_key)
    
    async def __generate_content(self, prompt: str, file: bytes, config_schema):
        """Main response function"""
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=file,
                        mime_type="application/pdf"
                    ),
                prompt
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": config_schema
                }
            )
            if config_schema == str:
                return response.text.strip('"') # thanks google for adding extra quotes
            return response.text 
        except Exception as e:
            raise GeminiDown from e
    
    async def improve_resume(self, file: bytes):
        """Generates comments on how to improve a given resume"""
        prompt = """You are an expert technical recruiter and career coach with 10+ years of experience placing candidates at top-tier tech firms (e.g., Google, Amazon, Meta, startups, and enterprise software companies).

                    Review the following resume.

                    Provide specific, actionable feedback on clarity, formatting, relevance, and impact.

                    Identify any red flags or weak areas (e.g., vague language, lack of quantifiable achievements, or inconsistent structure).

                    Suggest improvements to wording, bullet points, or structure to better highlight the candidate’s strengths.

                    Comment on how the resume might perform with ATS (Applicant Tracking Systems) and human recruiters.

                    Finally, summarize what kind of roles or companies this resume would most likely appeal to."""
        return await self.__generate_content(prompt=prompt, file=file, config_schema=Opinion)
    
    async def get_preference(self, file: bytes):
        """Predicts internship preference from a given resume"""
        prompt = f"""You are an expert career advisor and recruiter with deep knowledge of internship roles in the tech industry.
        Given the resume below, analyze the candidate’s background—including their technical skills, projects, education, and experiences—and determine the single most suitable internship role for them.

        You must choose only one role from the list provided. Your decision should be based on the strongest demonstrated competencies and project alignment. Do not guess or invent qualifications not explicitly present in the resume.

        Valid internship roles (choose exactly one):
        {ROLE_LIST}
        """
        return await self.__generate_content(prompt=prompt, file=file, config_schema=str)
    
    async def parse_by_section(self, file: bytes):
        """Parses resume by section"""
        prompt = f"""
        You are a structured data extractor for resumes. Your task is to convert the raw resume text into the following JSON format, strictly adhering to this schema (based on Pydantic models):
            class Education(BaseModel):
                institution: str
                location: str
                degree: str
                start_date: str
                end_date: str
                gpa: Optional[str] = None
                relevant_coursework: Optional[str] = None
                activities: Optional[str] = None

            class Experience(BaseModel):
                company: str
                location: str
                position: str
                start_date: str
                end_date: str
                bullets: list[str]

            class Project(BaseModel):
                name: str
                location: str
                description: str
                start_date: str
                end_date: str
                bullets: list[str]

            class SkillCategory(BaseModel):
                category: str
                items: list[str]

            class Resume(BaseModel):
                name: str
                phone: Optional[str] = None
                email: str
                linkedin_link: str
                education: list[Education]
                experience: Optional[list[Experience]] = None
                projects: Optional[list[Project]] = None
                skills: Optional[list[SkillCategory]] = None
                
            Escape all LaTeX-special characters incluidng & and % by prefixing each with a backslash so the resulting JSON can be inserted directly into LaTeX without compilation errors.
            Dates for projects and experiences should be in 'MMM yyyy'
            Categorise the given skills based off the resume
            If a section is absent or contains no data, set it explicitly to null (JSON null) instead of an empty list or string.
            Preserve the ordering of sections exactly as they appear in the raw resume; do not invent or reorder content.
            Output only the final JSON object—no explanations, comments, or additional text.
        """
        return await self.__generate_content(prompt=prompt, file=file, config_schema=Resume)

def get_gemini_client():
    settings = get_settings()
    return GeminiAPI(api_key=settings.gemini_api_key)
