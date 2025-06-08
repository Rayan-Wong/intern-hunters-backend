import io

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.workers.internship_roles import role_list
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

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)

async def parse_resume(file: bytes):
    try:
        prompt = """Improve each section of my resume. Do not fake anything, but you may put placeholder values."""
        response = await client.aio.models.generate_content(
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
                "response_schema": Comments
            }
        )
        return response.text
    except Exception as e:
        raise GeminiDown from e

async def get_preference(file: bytes):
    try:
        prompt = f"""Given this resume, determine the most suitable internship role.
        You must use only an option from the list of roles below

        {role_list}
        """
        response = await client.aio.models.generate_content(
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
                "response_schema": str
            }
        )
        return response.text.strip('"') # thanks google for adding extra quotes
    except Exception as e:
        raise GeminiDown from e
