"""Modules relevant for FastAPI testing"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
import pytest
from pydantic import BaseModel

from tests.conftest import UserTest, client, get_user_token

class UserApplication(BaseModel):
    """User Application constructor for tests"""
    company_name: str
    role_name: str
    location: str
    status: str
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationModify(UserApplication):
    """"Constructor for user application modify requests"""
    id: int

@pytest.mark.asyncio
async def test_get_initial_application_stats(client: AsyncClient, get_user_token: str):
    """Tests if initialised user has 0 applications"""
    result = await client.get("/api/application_stats",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["total"] == 0

@pytest.mark.asyncio
async def test_create_application(client: AsyncClient, get_user_token: str):
    """Tests if an application is successfully created"""
    application = UserApplication(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Applied",
    )
    result = await client.post("/api/application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["company_name"] == "Skibidi"

@pytest.mark.asyncio
async def test_get_application_stats(client: AsyncClient, get_user_token: str):
    """Tests if  user now has 1 application"""
    result = await client.get("/api/application_stats",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["total"] == 1
    assert result.json()["applied"] == 1

@pytest.mark.asyncio
async def test_create_invalid_application(client: AsyncClient, get_user_token: str):
    """Tests if invalid application is not created"""
    application = UserApplication(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="ur mum",
    )
    result = await client.post("/api/application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_application(client: AsyncClient, get_user_token: str):
    """Tests if a requested valid application is successfully received"""
    result = await client.get("/api/application",
        params={"post_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["company_name"] == "Skibidi"

@pytest.mark.asyncio
async def test_get_wrong_application(client: AsyncClient, get_user_token: str):
    """Tests if a requested invalid application fails"""
    result = await client.get("/api/application",
        params={"post_id": 2},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    print(result.json())
    assert result.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_applications(client: AsyncClient, get_user_token: str):
    """Tests if a user can get all their applications"""
    result = await client.get("/api/all_applications",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()

@pytest.mark.asyncio
async def test_get_no_deadlines(client: AsyncClient, get_user_token: str):
    """Tests if a user gets no applications if they have no deadlines"""
    result = await client.get("/api/all_deadlines",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json() == []

@pytest.mark.asyncio
async def test_modify_application(client: AsyncClient, get_user_token: str):
    """Tests if a user can modify the correct application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Interview",
        id=1
    )
    result = await client.put("/api/application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["status"] == "Interview"

@pytest.mark.asyncio
async def test_modify_application_badly(client: AsyncClient, get_user_token: str):
    """Tests if a user can modify the correct application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Phonk",
        id=1
    )
    result = await client.put("/api/application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_modify_wrong_application(client: AsyncClient, get_user_token: str):
    """Tests if user fails to modify wrong application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
        id=9999
    )
    result = await client.put("/api/application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_valid_application(client: AsyncClient, get_user_token: str):
    """Tests if a requested valid application is successfully deleted"""
    result = await client.delete("/api/application",
        params={"application_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_202_ACCEPTED

@pytest.mark.asyncio
async def test_delete_invalid_application(client: AsyncClient, get_user_token: str):
    """Tests if a requested invalid application fails to delete"""
    result = await client.delete("/api/application",
        params={"application_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_no_applications(client: AsyncClient, get_user_token: str):
    """Tests if a user without any applications gets an empty list"""
    result = await client.get("/api/all_applications",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json() == []

@pytest.mark.asyncio
async def test_get_all_deadlines(client: AsyncClient, get_user_token: str):
    """Tests if a user gets all applications with deadlines in order"""
    application1 = UserApplication(
        company_name="Sigma",
        role_name="Boy",
        location="ts",
        status="Interview",
        action_deadline=datetime.now(timezone.utc)+timedelta(days=3)
    )
    check1 = await client.post(
        "/api/application",
        json=jsonable_encoder(application1.model_dump()),
        headers={
            "Authorization": f"Bearer {get_user_token}"
        }
    )
    assert check1.status_code == status.HTTP_200_OK
    application2 = UserApplication(
        company_name="Melvin",
        role_name="Gurt",
        location="Yo",
        status="Offered",
        action_deadline=datetime.now(timezone.utc)+timedelta(days=2)
    )
    check2 = await client.post(
        "/api/application",
        json=jsonable_encoder(application2.model_dump()),
        headers={
            "Authorization": f"Bearer {get_user_token}"
        }
    )
    assert check2.status_code == status.HTTP_200_OK
    result = await client.get("/api/all_deadlines",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()
    first_result = result.json()[0]
    assert first_result["company_name"] == "Melvin"

@pytest.mark.asyncio
async def test_get_multiple_application_stats(client: AsyncClient, get_user_token: str):
    """Tests if user now has 2 applications"""
    result = await client.get("/api/application_stats",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["total"] == 2
    assert result.json()["interview"] == 1
    assert result.json()["offered"] == 1