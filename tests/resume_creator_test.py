from fastapi import status
from httpx import AsyncClient
import pytest
import pytest_asyncio
from unittest.mock import patch

from tests.conftest import UserTest, client, get_user_token, mock_boto3
from app.schemas.resume_editor import Resume, Education

@pytest.fixture
def get_resume_details():
    return Resume(
        name="test",
        email="test",
        linkedin_link="test",
        education=[
            Education(
                institution="test",
                location="test",
                degree="test",
                start_date="test",
                end_date="test"
            )
        ] 
    ).model_dump()

@pytest.mark.asyncio
async def test_no_listings(client: AsyncClient, get_user_token: str):
    """Tests if user without skills cannot get internship listings"""
    result = await client.get("/api/internship_listings", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_no_resume(client: AsyncClient, get_user_token: str):
    """Tests if user without skills cannot get parsed resume"""
    result = await client.get("/api/get_parsing", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch('app.services.resume_creator_service.R2')
async def test_no_download_resume(mock_r2, client: AsyncClient, get_user_token: str, mock_boto3):
    """Tests if user without skills cannot download resume"""
    result = await client.get("/api/get_resume", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch('app.services.resume_creator_service.R2')
async def test_create_resume(mock_r2, client: AsyncClient, get_user_token: str, get_resume_details: Resume, mock_boto3):
    """Tests if user can create resume"""
    mock_r2.return_value = mock_boto3
    result = await client.post("/api/create_resume", json=get_resume_details, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    mock_boto3.upload_resume.assert_awaited()

@pytest.mark.asyncio
async def test_resume(client: AsyncClient, get_user_token: str):
    """Tests if user with skills can get parsed resume"""
    result = await client.get("/api/get_parsing", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json()

@pytest.mark.asyncio
@patch('app.services.resume_creator_service.R2')
async def test_download_resume(mock_r2, client: AsyncClient, get_user_token: str, mock_boto3):
    """Tests if user without skills can download resume"""
    mock_r2.return_value = mock_boto3
    result = await client.get("/api/get_resume", headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    mock_boto3.download_resume.assert_awaited()

@pytest.mark.asyncio
@patch('app.services.resume_creator_service.R2')
async def test_edit_resume(mock_r2, client: AsyncClient, get_user_token: str, get_resume_details: Resume, mock_boto3):
    """Tests if user can create resume"""
    mock_r2.return_value = mock_boto3
    result = await client.put("/api/edit_resume", json=get_resume_details, headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    mock_boto3.upload_resume.assert_awaited()