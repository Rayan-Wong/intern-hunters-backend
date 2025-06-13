"""Modules relevant for FastAPI testing"""
import os
from typing import TextIO

from fastapi import status
from httpx import AsyncClient
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from tests.conftest import UserTest, client, get_user_token
from app.schemas.internship_listings import InternshipListing

@pytest.fixture
def mock_scraper():
    def fake_scraper(unused: str, start: int, end: int):
        listings = [InternshipListing(
                company = f"{i}",
                job_url="Lorem",
                title="Ipsum",
                description="Lol",
                date_posted=None
            ) for i in range(start, end, 1)]
        return listings
    with patch("app.services.internship_listings_service.sync_scrape_jobs", side_effect=fake_scraper) as mock:
        yield mock

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

@pytest_asyncio.fixture
async def mock_boto3():
    mock_boto3 = AsyncMock()
    mock_boto3.upload_resume = AsyncMock()
    return mock_boto3

@pytest.mark.asyncio
async def test_no_listings(client: AsyncClient, get_user_token: str):
    """Tests if user without skills cannot get internship listings"""
    result = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch('app.services.internship_listings_service.R2') # todo: not need this by setting up local s3
async def test_get_skills(mock_r2, client: AsyncClient, get_user_token: str, construct_file_args: dict[str, tuple[str, TextIO, str]], mock_boto3):
    """Tests if a user's skills and preferences is successfully created from a resume"""
    mock_r2.return_value = mock_boto3
    result = await client.post("/api/upload_resume", files=construct_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    mock_boto3.upload_resume.assert_awaited()

@pytest.mark.asyncio
async def test_bad_resume(client: AsyncClient, get_user_token: str, construct_bad_file_args: dict[str, tuple[str, TextIO, str]]):
    """Tests if the path rejects a bad resume"""
    result = await client.post("/api/upload_resume", files=construct_bad_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_listings(client: AsyncClient, get_user_token: str):
    """Tests if user with skills can get internship listings"""
    result = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []

@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, get_user_token: str, mock_scraper):
    """Tests if pagination works"""
    result1 = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result1.status_code == status.HTTP_200_OK
    assert result1.json()[0]["company"] == "0"
    assert mock_scraper.called
    result2 = await client.get("/api/internship_listings",
        params={"page": 1},
        headers={
        "Authorization": f"Bearer {get_user_token}"
        })
    assert result2.status_code == status.HTTP_200_OK
    assert result2.json()[0]["company"] == "5"