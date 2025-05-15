"""Modules relevant for FastAPI testing"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import status
import pytest
from pydantic import BaseModel

from tests.conftest import make_client, good_user

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

@pytest.fixture
def get_user_token(good_user):
    """generates good user token to use"""
    client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    return token

client = make_client()

def test_create_application(get_user_token):
    """Tests if an application is successfully created"""
    application = UserApplication(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
    )
    result = client.post("/api/create_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK

def test_get_application(get_user_token):
    """Tests if a requested valid application is successfully received"""
    result = client.get("/api/get_application",
        params={"post_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["company_name"] == "Skibidi"

def test_get_wrong_application(get_user_token):
    """Tests if a requested invalid application fails"""
    result = client.get("/api/get_application",
        params={"post_id": 2},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    print(result.json())
    assert result.status_code == status.HTTP_404_NOT_FOUND

def test_get_all_applications(get_user_token):
    """Tests if a user can get all their applications"""
    result = client.get("/api/get_all_applications",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK

def test_modify_application(get_user_token):
    """Tests if a user can modify the correct application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
        id=1
    )
    result = client.post("/api/modify_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK

def test_modify_wrong_application(get_user_token):
    """Tests if user fails to modify wrong application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
        id=2
    )
    result = client.post("/api/modify_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_404_NOT_FOUND
