"""Modules relevant for FastAPI testing"""
import os
from typing import TextIO

from fastapi import status
from httpx import AsyncClient
import pytest

from tests.conftest import UserTest, client, get_user_token

@pytest.fixture
def get_resume():
    current_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(current_dir, "test_resume.pdf")
    with open(pdf_path, "rb") as file:
        yield file

@pytest.fixture
def construct_file_args(get_resume: TextIO):
    return {
        "file": ("resume.pdf", get_resume, "application/pdf")
    }

@pytest.fixture
def get_bad_resume():
    current_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(current_dir, "test_resume.docx")
    with open(pdf_path, "rb") as file:
        yield file

@pytest.fixture
def construct_bad_file_args(get_resume: TextIO):
    return {
        # yes, that really is a docx mime type
        "file": ("resume.docx", get_bad_resume, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }

@pytest.mark.asyncio
async def test_get_skills(client: AsyncClient, get_user_token: str, construct_file_args: dict[str, tuple[str, TextIO, str]]):
    """Tests if a user's skills is successfully created from a resume"""
    result = await client.post("/api/skills", files=construct_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []

@pytest.mark.asyncio
async def test_bad_resume(client: AsyncClient, get_user_token: str, construct_bad_file_args: dict[str, tuple[str, TextIO, str]]):
    """Tests if the path rejects a bad resume"""
    result = await client.post("/api/skills", files=construct_bad_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_listings(client: AsyncClient, get_user_token: str):
    """Tests if the path rejects a bad resume"""
    result = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []