"""Modules relevant for FastAPI testing and patching of scraper, boto3 API"""
import os
from typing import TextIO
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient
import pytest

from tests.conftest import UserTest, client, get_user_token, mock_boto3, mock_cache
from app.schemas.internship_listings import InternshipListing

PAGE_RESULTS = 10
ACTIVE_PORTALS = 2

@pytest.fixture
def mock_scraper():
    """Mock fixture to patch internship scraper API"""
    def fake_scraper(preference: str, start: int, end: int, industry: str | None):
        listings = [InternshipListing(
                company = f"{i}",
                job_url="Lorem",
                title="Ipsum",
                description="Lol",
                date_posted=None,
                is_remote=True,
                company_industry=None
            ) for i in range(start, end, 1)]
        return listings
    with patch(
        "app.services.internship_listings_service.sync_scrape_jobs",
        side_effect=fake_scraper
    ) as mock:
        yield mock

@pytest.fixture
def get_resume():
    """Fixture to get good resume pdf"""
    current_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(current_dir, "test_resume.pdf")
    with open(pdf_path, "rb") as file:
        yield file

@pytest.fixture
def construct_file_args(get_resume: TextIO):
    """Fixture to create needed args for AsyncClient"""
    return {
        "file": ("resume.pdf", get_resume, "application/pdf")
    }

@pytest.fixture
def get_bad_resume():
    """Fixture to get bad resume docx"""
    current_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(current_dir, "test_resume.docx")
    with open(pdf_path, "rb") as file:
        yield file

@pytest.fixture
def construct_bad_file_args(get_bad_resume: TextIO):
    """Fixture to create needed args for AsyncClient"""
    return {
        # yes, that really is a docx mime type
        "file": (
            "resume.docx",
            get_bad_resume,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    }

@pytest.mark.asyncio
# todo: not need to patch by setting up local s3
@patch('app.services.internship_listings_service.R2')
async def test_upload_resume(
    mock_r2, 
    client: AsyncClient,
    get_user_token: str,
    construct_file_args: dict[str, tuple[str, TextIO, str]],
    mock_boto3
):
    """Tests if a user's resume is successfully uploaded"""
    mock_r2.return_value = mock_boto3
    result = await client.post("/api/upload_resume", files=construct_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    mock_boto3.upload_resume.assert_awaited()

@pytest.mark.asyncio
async def test_bad_resume(
    client: AsyncClient,
    get_user_token: str,
    construct_bad_file_args: dict[str, tuple[str, TextIO, str]]
):
    """Tests if the path rejects a bad resume"""
    result = await client.post("/api/upload_resume", files=construct_bad_file_args, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_listings(client: AsyncClient, get_user_token: str, mock_scraper, mock_cache):
    """Tests if user with skills can get internship listings"""
    result = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    mock_cache.assert_awaited()
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []
    assert mock_scraper.called

@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, get_user_token: str, mock_scraper, mock_cache):
    """Tests if pagination works"""
    result1 = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result1.status_code == status.HTTP_200_OK
    assert result1.json()[0]["company"] == "0"
    assert mock_scraper.called
    mock_cache.assert_awaited()
    result2 = await client.get("/api/internship_listings",
        params={"page": 1},
        headers={
        "Authorization": f"Bearer {get_user_token}"
        })
    assert result2.status_code == status.HTTP_200_OK
    assert result2.json()[0]["company"] == str(PAGE_RESULTS // ACTIVE_PORTALS)

@pytest.mark.asyncio
async def test_less_listings(client: AsyncClient, get_user_token: str, mock_scraper, mock_cache):
    """Tests if user with skills can get fewer internship listings for dashboard"""
    result = await client.get("/api/less_internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    mock_cache.assert_awaited()
    assert result.status_code == status.HTTP_200_OK
    assert result.json() != []
