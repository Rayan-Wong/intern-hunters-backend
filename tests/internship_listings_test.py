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

@pytest.mark.asyncio
async def test_get_skills(client: AsyncClient, get_user_token: str, construct_file_args: dict[str, tuple[str, TextIO, str]]):
    """Tests if an application is successfully created"""
    result = await client.post("/api/skills", files=construct_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []