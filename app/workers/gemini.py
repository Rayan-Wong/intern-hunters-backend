import io

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.workers.internship_roles import ROLE_LIST
from app.core.config import get_settings
from app.exceptions.internship_listings_exceptions import GeminiDown

class Critique(BaseModel):
    good: str
    bad: str

class Skills(BaseModel):
    technical_skills: Critique
    education: Critique
    projects: Critique
    past_experience: Critique
    leadership: Critique
    others: Critique
    overall: Critique
    decision: str

class Comments(BaseModel):
    technical_skills: list[str]
    education: str
    projects: list[str]
    past_experience: list[str]
    leadership: list[str]
    others: list[str]

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
        prompt = """Improve each section of my resume. Do not fake anything, but you may put placeholder values."""
        return await self.__generate_content(prompt=prompt, file=file, config_schema=Comments)
    
    async def get_preference(self, file: bytes):
        """Predicts internship preference from a given resume"""
        prompt = f"""Given this resume, determine the most suitable internship role.
        You must use only an option from the list of roles below
        {ROLE_LIST}
        """
        return await self.__generate_content(prompt=prompt, file=file, config_schema=str)

def get_gemini_client():
    settings = get_settings()
    return GeminiAPI(api_key=settings.gemini_api_key)